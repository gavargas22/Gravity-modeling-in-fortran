"""
Modern PySide6 GUI application for Gravity and Magnetics Modeling
Enhanced with API layer and progress reporting
"""

import sys
import os
from pathlib import Path
import numpy as np

# Set matplotlib backend before importing pyplot
os.environ['QT_API'] = 'PySide6'
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for PySide6 compatibility
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QStatusBar, QMenuBar, QMenu,
    QProgressBar, QLabel, QSplitter, QCheckBox, QSpinBox, QGroupBox,
    QFormLayout, QLineEdit, QPushButton, QMessageBox, QFileDialog,
    QComboBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QAction, QFont, QDoubleValidator

from gmm.api import GravityModelingAPI
from gmm.gm import InversionProgress


class MatplotlibCanvas(FigureCanvas):
    """Custom matplotlib canvas for PySide6 integration"""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.setParent(parent)

        # Create subplot
        self.axes = self.figure.add_subplot(111)

        # Set default styling
        self.figure.patch.set_facecolor('#f0f0f0')
        self.axes.grid(True, alpha=0.3)
        self.axes.set_xlabel('Distance (m)')
        self.axes.set_ylabel('Gravity Anomaly (mGal)')

    def clear_plot(self):
        """Clear the current plot"""
        self.axes.clear()
        self.axes.grid(True, alpha=0.3)
        self.draw()

    def plot_profile(self, x_data, y_obs, y_calc=None, residuals=None, title="Gravity Profile"):
        """Plot gravity profile with observed and calculated data"""
        self.axes.clear()
        self.axes.grid(True, alpha=0.3)

        # Plot observed data
        self.axes.plot(x_data, y_obs, 'bo-', label='Observed', markersize=4, linewidth=1)

        # Plot calculated data if available
        if y_calc is not None:
            self.axes.plot(x_data, y_calc, 'r-', label='Calculated', linewidth=2)

        # Plot residuals if available
        if residuals is not None:
            ax2 = self.axes.twinx()
            ax2.plot(x_data, residuals, 'g--', label='Residuals', alpha=0.7)
            ax2.set_ylabel('Residuals (mGal)', color='g')
            ax2.tick_params(axis='y', labelcolor='g')

        self.axes.set_xlabel('Distance (m)')
        self.axes.set_ylabel('Gravity Anomaly (mGal)')
        self.axes.set_title(title)
        self.axes.legend()

        self.figure.tight_layout()
        self.draw()

    def plot_residuals(self, x_data, residuals, title="Residual Analysis"):
        """Plot residuals analysis"""
        self.axes.clear()
        self.axes.grid(True, alpha=0.3)

        # Plot residuals
        self.axes.plot(x_data, residuals, 'g-o', markersize=3, linewidth=1, alpha=0.8)

        # Add zero line
        self.axes.axhline(y=0, color='r', linestyle='--', alpha=0.5)

        # Add statistics
        rms = np.sqrt(np.mean(residuals**2))
        mean_res = np.mean(residuals)
        std_res = np.std(residuals)

        stats_text = '.2f'
        self.axes.text(0.02, 0.98, stats_text, transform=self.axes.transAxes,
                      verticalalignment='top', fontsize=9,
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        self.axes.set_xlabel('Distance (m)')
        self.axes.set_ylabel('Residuals (mGal)')
        self.axes.set_title(title)

        self.figure.tight_layout()
        self.draw()

    def plot_model_geometry(self, model, title="Model Geometry"):
        """Plot 2D model geometry"""
        self.axes.clear()
        self.axes.grid(True, alpha=0.3)

        # Plot polygons
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink']

        for i in range(model.npoly):
            # Get polygon vertices
            vertices = []
            for j in range(model.nsides[i]):
                if j < model.x.shape[1] and j < model.z.shape[1]:
                    x = model.x[i, j]
                    z = model.z[i, j]
                    if not (np.isnan(x) or np.isnan(z)):
                        vertices.append((x, z))

            if len(vertices) > 2:
                # Close the polygon
                vertices.append(vertices[0])
                x_coords, z_coords = zip(*vertices)

                # Plot polygon
                color = colors[i % len(colors)]
                self.axes.fill(x_coords, z_coords, color=color, alpha=0.6,
                              label=f'Polygon {i+1} (ρ={model.densty[i]:.3f})')

                # Plot outline
                self.axes.plot(x_coords, z_coords, 'k-', linewidth=1)

        self.axes.set_xlabel('Distance (m)')
        self.axes.set_ylabel('Depth (m)')
        self.axes.set_title(title)
        self.axes.legend()
        self.axes.invert_yaxis()  # Depth increases downward

        self.figure.tight_layout()
        self.draw()


class InversionWorker(QThread):
    """Worker thread for running inversion in background"""
    progress = Signal(InversionProgress)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, api, iterations, enable_adjustment):
        super().__init__()
        self.api = api
        self.iterations = iterations
        self.enable_adjustment = enable_adjustment

    def run(self):
        try:
            # Set progress callback
            self.api.set_progress_callback(self.progress.emit)

            # Run inversion
            result = self.api.run_inversion(
                iterations=self.iterations,
                enable_parameter_adjustment=self.enable_adjustment
            )

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class GravityModelingApp(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.api = GravityModelingAPI()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Gravity and Magnetics Modeling")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Project explorer
        self.create_project_explorer()
        splitter.addWidget(self.project_explorer)

        # Right panel: Main content
        self.create_main_content()
        splitter.addWidget(self.main_content)

        # Set splitter proportions
        splitter.setSizes([300, 900])

        main_layout.addWidget(splitter)

        # Create menus
        self.create_menus()

        # Create status bar
        self.create_status_bar()

        # Apply styling
        self.apply_styling()

    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        load_action = QAction("Load Project", self)
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)

        save_action = QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def apply_styling(self):
        """Apply application styling"""
        # Set a modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
            }
            QPushButton:pressed {
                background-color: #cce7ff;
            }
        """)

    def load_project(self):
        """Load project via menu"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Project files (*.json)")

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            result = self.api.load_project(selected_file)

            if result["success"]:
                self.status_label.setText(f"Loaded project: {self.api.current_model.project_name}")
                self.update_ui_from_project()
            else:
                QMessageBox.critical(self, "Load Failed",
                                   f"Failed to load project:\n{result.get('message', 'Unknown error')}")

    def save_project(self):
        """Save project via menu"""
        if not self.api.current_model:
            QMessageBox.warning(self, "No Project", "Please load a project first.")
            return

        result = self.api.save_project()
        if result["success"]:
            self.status_label.setText("Project saved successfully")
        else:
            QMessageBox.critical(self, "Save Failed",
                               f"Failed to save project:\n{result.get('message', 'Unknown error')}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Gravity Modeling",
                         "Gravity and Magnetics Modeling Application\n"
                         "Modern Python implementation with PySide6 GUI\n"
                         "Enhanced with matplotlib visualization and batch processing")

    def create_project_explorer(self):
        """Create the project explorer tree"""
        self.project_explorer = QTreeWidget()
        self.project_explorer.setHeaderLabel("Projects")
        self.project_explorer.setMaximumWidth(300)

        # Add sample project structure
        self.update_project_explorer()

    def update_project_explorer(self):
        """Update project explorer with current project"""
        self.project_explorer.clear()

        if self.api.current_model:
            root = QTreeWidgetItem(self.project_explorer)
            root.setText(0, self.api.current_model.project_name)
            root.setExpanded(True)

            # Add inputs
            if hasattr(self.api.current_model, 'inputs_dir') and self.api.current_model.inputs_dir.exists():
                inputs = QTreeWidgetItem(root)
                inputs.setText(0, "Inputs")
                for file in self.api.current_model.inputs_dir.glob("*"):
                    if file.is_file():
                        QTreeWidgetItem(inputs, [file.name])

            # Add outputs
            if hasattr(self.api.current_model, 'outputs_dir') and self.api.current_model.outputs_dir.exists():
                outputs = QTreeWidgetItem(root)
                outputs.setText(0, "Outputs")
                for file in self.api.current_model.outputs_dir.glob("*"):
                    if file.is_file():
                        QTreeWidgetItem(outputs, [file.name])
        else:
            # No project loaded
            root = QTreeWidgetItem(self.project_explorer)
            root.setText(0, "No project loaded")

    def create_main_content(self):
        """Create the main content area with tabs"""
        self.main_content = QWidget()
        layout = QVBoxLayout(self.main_content)

        # Inversion controls
        self.create_inversion_controls()
        layout.addWidget(self.inversion_controls)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Data Visualization Tab
        self.create_visualization_tab()

        # Batch Processing Tab
        self.create_batch_processing_tab()

        # Parameter Editor Tab
        self.create_parameter_tab()

        # Results Tab
        self.create_results_tab()

        layout.addWidget(self.tab_widget)

    def create_inversion_controls(self):
        """Create inversion control panel"""
        self.inversion_controls = QGroupBox("Inversion Controls")
        layout = QHBoxLayout(self.inversion_controls)

        # Iterations
        iter_layout = QVBoxLayout()
        iter_layout.addWidget(QLabel("Iterations:"))
        self.iterations_spin = QSpinBox()
        self.iterations_spin.setRange(1, 100)
        self.iterations_spin.setValue(10)
        iter_layout.addWidget(self.iterations_spin)
        layout.addLayout(iter_layout)

        # Parameter adjustment
        self.adjust_params_check = QCheckBox("Enable Parameter Adjustment")
        self.adjust_params_check.setChecked(False)
        layout.addWidget(self.adjust_params_check)

        # Run button
        self.run_button = QPushButton("Run Inversion")
        self.run_button.clicked.connect(self.run_inversion)
        layout.addWidget(self.run_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def create_visualization_tab(self):
        """Create data visualization tab with matplotlib plots"""
        viz_widget = QWidget()
        layout = QVBoxLayout(viz_widget)

        # Plot controls
        controls_layout = QHBoxLayout()

        # Plot type selector
        controls_layout.addWidget(QLabel("Plot Type:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            "Profile (Obs vs Calc)",
            "Residuals Analysis",
            "Model Geometry",
            "3D Model View"
        ])
        self.plot_type_combo.currentTextChanged.connect(self.update_plot)
        controls_layout.addWidget(self.plot_type_combo)

        # Update plot button
        self.update_plot_button = QPushButton("Update Plot")
        self.update_plot_button.clicked.connect(self.update_plot)
        controls_layout.addWidget(self.update_plot_button)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Create matplotlib canvas
        self.canvas = MatplotlibCanvas(viz_widget, width=8, height=6)
        layout.addWidget(self.canvas)

        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, viz_widget)
        layout.addWidget(self.toolbar)

        # Status label for plot info
        self.plot_status = QLabel("Load a project and run inversion to see plots")
        layout.addWidget(self.plot_status)

        self.tab_widget.addTab(viz_widget, "Visualization")

    def update_plot(self):
        """Update the current plot based on selected type"""
        if not self.api.current_model:
            self.plot_status.setText("No project loaded")
            self.canvas.clear_plot()
            return

        plot_type = self.plot_type_combo.currentText()

        try:
            if plot_type == "Profile (Obs vs Calc)":
                self.plot_profile_comparison()
            elif plot_type == "Residuals Analysis":
                self.plot_residuals_analysis()
            elif plot_type == "Model Geometry":
                self.plot_model_geometry_view()
            elif plot_type == "3D Model View":
                self.plot_3d_model_view()
        except Exception as e:
            self.plot_status.setText(f"Error creating plot: {str(e)}")
            self.canvas.clear_plot()

    def plot_profile_comparison(self):
        """Plot observed vs calculated gravity profile"""
        model = self.api.current_model

        # Get station data
        distances = model.measurements.distance.values
        observed = model.measurements.obs_grav.values

        # Get calculated data if available
        calculated = None
        if hasattr(model, 'gtot') and len(model.gtot) > 0:
            calculated = model.gtot.copy()

        # Calculate residuals if both datasets available
        residuals = None
        if calculated is not None:
            residuals = observed - calculated

        # Plot the data
        title = f"Gravity Profile - {model.project_name}"
        self.canvas.plot_profile(distances, observed, calculated, residuals, title)

        # Update status
        if calculated is not None:
            rms = np.sqrt(np.mean(residuals**2)) if residuals is not None else 0
            self.plot_status.setText(".2f")
        else:
            self.plot_status.setText("Showing observed data only (run inversion for calculated data)")

    def plot_residuals_analysis(self):
        """Plot residuals analysis"""
        model = self.api.current_model

        # Check if we have calculated data
        if not hasattr(model, 'gtot') or len(model.gtot) == 0:
            self.plot_status.setText("Run inversion first to generate residuals")
            self.canvas.clear_plot()
            return

        distances = model.measurements.distance.values
        observed = model.measurements.obs_grav.values
        calculated = model.gtot
        residuals = observed - calculated

        title = f"Residual Analysis - {model.project_name}"
        self.canvas.plot_residuals(distances, residuals, title)

        # Update status with statistics
        rms = np.sqrt(np.mean(residuals**2))
        mean_res = np.mean(residuals)
        std_res = np.std(residuals)
        self.plot_status.setText(".2f")

    def plot_model_geometry_view(self):
        """Plot 2D model geometry"""
        model = self.api.current_model

        title = f"Model Geometry - {model.project_name}"
        self.canvas.plot_model_geometry(model, title)

        self.plot_status.setText(f"Showing {model.npoly} polygons")

    def plot_3d_model_view(self):
        """Plot 3D model view with polygons and optional field vectors"""
        model = self.api.current_model

        # Clear and set up 3D axes
        self.canvas.figure.clear()
        self.axes = self.canvas.figure.add_subplot(111, projection='3d')

        # Set labels and title
        self.axes.set_xlabel('X Distance (m)')
        self.axes.set_ylabel('Y Distance (m)')
        self.axes.set_zlabel('Depth (m)')
        self.axes.set_title(f"3D Model View - {model.project_name}")

        # Plot polygons as 3D surfaces
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink']

        for i in range(model.npoly):
            # Get polygon vertices
            vertices = []
            for j in range(model.nsides[i]):
                if j < model.x.shape[1] and j < model.z.shape[1]:
                    x = model.x[i, j]
                    y = 0.0  # Assume 2.5D model (constant Y)
                    z = model.z[i, j]
                    if not (np.isnan(x) or np.isnan(z)):
                        vertices.append((x, y, z))

            if len(vertices) > 2:
                # Create polygon surface
                x_coords, y_coords, z_coords = zip(*vertices)

                # Plot the polygon outline
                self.axes.plot(x_coords + (x_coords[0],),  # Close the polygon
                              y_coords + (y_coords[0],),
                              z_coords + (z_coords[0],),
                              'k-', linewidth=2)

                # Fill the polygon (simplified - just plot the boundary)
                color = colors[i % len(colors)]
                self.axes.fill(x_coords, y_coords, z_coords,
                              color=color, alpha=0.3,
                              label=f'Polygon {i+1}')

        # Add station locations
        if hasattr(model, 'measurements') and len(model.measurements) > 0:
            station_x = model.measurements.distance.values
            station_y = np.zeros_like(station_x)  # Surface stations
            station_z = np.zeros_like(station_x)

            self.axes.scatter(station_x, station_y, station_z,
                            c='red', marker='^', s=50,
                            label='Stations')

        # Set equal aspect ratio and invert Z for depth
        self.axes.set_box_aspect([1, 1, 0.5])  # Make Z axis shorter
        self.axes.invert_zaxis()  # Depth increases downward

        self.axes.legend()
        self.axes.grid(True, alpha=0.3)

        self.canvas.draw()
        self.plot_status.setText(f"3D view: {model.npoly} polygons, {len(model.measurements)} stations")

    def run_inversion(self):
        """Start inversion process"""
        if not self.api.current_model:
            QMessageBox.warning(self, "No Project", "Please load a project first.")
            return

        iterations = self.iterations_spin.value()
        enable_adjustment = self.adjust_params_check.isChecked()

        # Disable run button and show progress
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, iterations)
        self.status_label.setText("Running inversion...")

        # Clear previous results
        self.results_text.clear()

        # Start inversion in background thread
        self.inversion_worker = InversionWorker(self.api, iterations, enable_adjustment)
        self.inversion_worker.progress.connect(self.update_progress)
        self.inversion_worker.finished.connect(self.on_inversion_finished)
        self.inversion_worker.error.connect(self.on_inversion_error)
        self.inversion_worker.start()

    def create_parameter_tab(self):
        """Create parameter editor tab"""
        param_widget = QWidget()
        layout = QVBoxLayout(param_widget)

        # Project settings group
        settings_group = QGroupBox("Project Settings")
        settings_layout = QFormLayout(settings_group)

        # Ambient field
        self.ambient_field_edit = QLineEdit()
        self.ambient_field_edit.setValidator(QDoubleValidator(0, 2, 3))
        self.ambient_field_edit.setText("0.5")
        settings_layout.addRow("Ambient Field (T):", self.ambient_field_edit)

        # Inclination
        self.inclination_edit = QLineEdit()
        self.inclination_edit.setValidator(QDoubleValidator(-90, 90, 1))
        self.inclination_edit.setText("65.0")
        settings_layout.addRow("Inclination (°):", self.inclination_edit)

        # Azimuth
        self.azimuth_edit = QLineEdit()
        self.azimuth_edit.setValidator(QDoubleValidator(-180, 180, 1))
        self.azimuth_edit.setText("12.0")
        settings_layout.addRow("Declination (°):", self.azimuth_edit)

        layout.addWidget(settings_group)

        # Update button
        self.update_params_button = QPushButton("Update Parameters")
        self.update_params_button.clicked.connect(self.update_project_parameters)
        layout.addWidget(self.update_params_button)

        # Parameter table placeholder
        self.param_table = QTextEdit()
        self.param_table.setPlaceholderText("Model parameters will appear here after loading a project...")
        layout.addWidget(self.param_table)

        self.tab_widget.addTab(param_widget, "Parameters")

    def create_results_tab(self):
        """Create results display tab"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Inversion results will appear here...")
        layout.addWidget(self.results_text)

        self.tab_widget.addTab(results_widget, "Results")

    def update_project_parameters(self):
        """Update project parameters from UI"""
        if not self.api.current_model:
            QMessageBox.warning(self, "No Project", "Please load a project first.")
            return

        updates = {}
        try:
            if self.ambient_field_edit.text():
                updates["ambient_field"] = float(self.ambient_field_edit.text())
            if self.inclination_edit.text():
                updates["inclination"] = float(self.inclination_edit.text())
            if self.azimuth_edit.text():
                updates["azimuth"] = float(self.azimuth_edit.text())

            result = self.api.update_project_settings(updates)
            if result["success"]:
                self.status_label.setText("Parameters updated successfully")
                # Update parameter display
                self.update_parameter_table()
            else:
                QMessageBox.warning(self, "Update Failed", result.get("message", "Unknown error"))

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"Please enter valid numbers: {e}")

    def update_results_display(self, result):
        """Update results display with inversion results"""
        if "results" in result:
            results = result["results"]
            self.results_text.append("Inversion Results:")
            self.results_text.append(f"Final χ²: {results.get('chi_squared', 'N/A')}")
            self.results_text.append(f"Iterations: {results.get('iterations', 'N/A')}")
            if "final_parameters" in results:
                self.results_text.append("Final Parameters:")
                for param in results["final_parameters"]:
                    self.results_text.append(f"  {param}")

    def update_parameter_table(self):
        """Update parameter table with current model parameters"""
        if not self.api.current_model:
            return

        # This would update a parameter table if it existed
        # For now, just update the status
        params = self.api.get_model_parameters()
        if params:
            self.status_label.setText(f"Model: {params['total_polygons']} polygons loaded")

    def update_ui_from_project(self):
        """Update UI elements when a project is loaded"""
        self.update_project_explorer()
        self.update_parameter_table()
        # Switch to visualization tab
        self.tab_widget.setCurrentIndex(0)  # Visualization tab

    def create_batch_processing_tab(self):
        """Create batch processing tab for multiple projects"""
        batch_widget = QWidget()
        layout = QVBoxLayout(batch_widget)

        # Project selection
        project_group = QGroupBox("Project Selection")
        project_layout = QVBoxLayout(project_group)

        # Add projects button
        self.add_projects_button = QPushButton("Add Projects...")
        self.add_projects_button.clicked.connect(self.add_batch_projects)
        project_layout.addWidget(self.add_projects_button)

        # Project list
        self.batch_project_list = QTextEdit()
        self.batch_project_list.setMaximumHeight(150)
        self.batch_project_list.setPlaceholderText("Selected projects will appear here...")
        project_layout.addWidget(self.batch_project_list)

        layout.addWidget(project_group)

        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QFormLayout(options_group)

        self.batch_iterations = QSpinBox()
        self.batch_iterations.setRange(1, 100)
        self.batch_iterations.setValue(10)
        options_layout.addRow("Iterations per project:", self.batch_iterations)

        self.batch_adjust_params = QCheckBox("Enable parameter adjustment")
        self.batch_adjust_params.setChecked(True)
        options_layout.addRow("", self.batch_adjust_params)

        self.batch_save_results = QCheckBox("Save results to files")
        self.batch_save_results.setChecked(True)
        options_layout.addRow("", self.batch_save_results)

        layout.addWidget(options_group)

        # Control buttons
        buttons_layout = QHBoxLayout()

        self.start_batch_button = QPushButton("Start Batch Processing")
        self.start_batch_button.clicked.connect(self.start_batch_processing)
        self.start_batch_button.setEnabled(False)
        buttons_layout.addWidget(self.start_batch_button)

        self.stop_batch_button = QPushButton("Stop Batch")
        self.stop_batch_button.clicked.connect(self.stop_batch_processing)
        self.stop_batch_button.setEnabled(False)
        buttons_layout.addWidget(self.stop_batch_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Progress and results
        self.batch_progress = QTextEdit()
        self.batch_progress.setMaximumHeight(200)
        self.batch_progress.setPlaceholderText("Batch processing results will appear here...")
        layout.addWidget(self.batch_progress)

        self.tab_widget.addTab(batch_widget, "Batch Processing")

        # Initialize batch processing variables
        self.batch_projects = []
        self.batch_worker = None
        self.batch_running = False

    def add_batch_projects(self):
        """Add multiple projects for batch processing"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Project files (*.json)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.batch_projects.extend(selected_files)

            # Update display
            project_text = "\n".join([os.path.basename(p) for p in self.batch_projects])
            self.batch_project_list.setPlainText(project_text)

            # Enable start button if we have projects
            self.start_batch_button.setEnabled(len(self.batch_projects) > 0)

    def start_batch_processing(self):
        """Start batch processing of selected projects"""
        if not self.batch_projects:
            QMessageBox.warning(self, "No Projects", "Please add projects to process first.")
            return

        self.batch_running = True
        self.start_batch_button.setEnabled(False)
        self.stop_batch_button.setEnabled(True)
        self.batch_progress.clear()

        # Start batch processing in background
        self.batch_worker = BatchProcessingWorker(
            self.batch_projects,
            self.batch_iterations.value(),
            self.batch_adjust_params.isChecked(),
            self.batch_save_results.isChecked()
        )
        self.batch_worker.progress.connect(self.update_batch_progress)
        self.batch_worker.finished.connect(self.on_batch_finished)
        self.batch_worker.error.connect(self.on_batch_error)
        self.batch_worker.start()

    def stop_batch_processing(self):
        """Stop batch processing"""
        if self.batch_worker and self.batch_running:
            self.batch_worker.stop()
            self.batch_running = False
            self.start_batch_button.setEnabled(True)
            self.stop_batch_button.setEnabled(False)
            self.batch_progress.append("Batch processing stopped by user.")

    def update_batch_progress(self, message):
        """Update batch processing progress"""
        self.batch_progress.append(message)
        # Scroll to bottom
        cursor = self.batch_progress.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.batch_progress.setTextCursor(cursor)

    def on_batch_finished(self, results):
        """Handle batch processing completion"""
        self.batch_running = False
        self.start_batch_button.setEnabled(True)
        self.stop_batch_button.setEnabled(False)

        self.batch_progress.append(f"\nBatch processing completed!")
        self.batch_progress.append(f"Processed {len(results)} projects")

        # Show summary
        successful = sum(1 for r in results if r.get('success', False))
        self.batch_progress.append(f"Successful: {successful}/{len(results)}")

    def on_batch_error(self, error_msg):
        """Handle batch processing error"""
        self.batch_running = False
        self.start_batch_button.setEnabled(True)
        self.stop_batch_button.setEnabled(False)
        self.batch_progress.append(f"Error: {error_msg}")


class BatchProcessingWorker(QThread):
    """Worker thread for batch processing multiple projects"""
    progress = Signal(str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, project_files, iterations, adjust_params, save_results):
        super().__init__()
        self.project_files = project_files
        self.iterations = iterations
        self.adjust_params = adjust_params
        self.save_results = save_results
        self.stop_requested = False

    def stop(self):
        """Request stop"""
        self.stop_requested = True

    def run(self):
        """Run batch processing"""
        results = []

        try:
            for i, project_file in enumerate(self.project_files):
                if self.stop_requested:
                    break

                self.progress.emit(f"Processing project {i+1}/{len(self.project_files)}: {os.path.basename(project_file)}")

                # Create API instance for this project
                api = GravityModelingAPI()

                # Load project
                result = api.load_project(project_file)
                if not result.get('success', False):
                    self.progress.emit(f"  Failed to load: {result.get('message', 'Unknown error')}")
                    results.append({'success': False, 'file': project_file, 'error': result.get('message')})
                    continue

                self.progress.emit(f"  Running inversion ({self.iterations} iterations)...")

                # Run inversion
                inv_result = api.run_inversion(
                    iterations=self.iterations,
                    enable_parameter_adjustment=self.adjust_params
                )

                if inv_result.get('success', False):
                    self.progress.emit(f"  Success! Final χ² = {inv_result.get('results', {}).get('chi_squared', 'N/A'):.2f}")

                    # Save results if requested
                    if self.save_results:
                        # Could save results to file here
                        pass
                else:
                    self.progress.emit(f"  Failed: {inv_result.get('message', 'Unknown error')}")

                results.append({
                    'success': inv_result.get('success', False),
                    'file': project_file,
                    'result': inv_result
                })

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Gravity Modeling")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Geophysics Lab")

    # Create and show main window
    window = GravityModelingApp()
    window.show()

    # Load test project on startup if it exists
    test_project = Path("models/test1/test1.json")
    if test_project.exists():
        result = window.api.load_project(str(test_project))
        if result["success"]:
            window.update_ui_from_project()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()