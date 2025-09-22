"""
Modern PySide6 GUI application for Gravity and Magnetics Modeling
Enhanced with API layer and progress reporting
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QStatusBar, QMenuBar, QMenu,
    QProgressBar, QLabel, QSplitter, QCheckBox, QSpinBox, QGroupBox,
    QFormLayout, QLineEdit, QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QAction, QFont, QDoubleValidator

from gmm.api import GravityModelingAPI
from gmm.gm import InversionProgress


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
        """Create data visualization tab"""
        viz_widget = QWidget()
        layout = QVBoxLayout(viz_widget)

        # Placeholder for matplotlib plots
        self.plot_area = QTextEdit()
        self.plot_area.setPlainText("Data visualization will be implemented here\n"
                                  "- Profile plot (observed vs calculated)\n"
                                  "- Residual plot\n"
                                  "- Model geometry view\n"
                                  "- Real-time parameter adjustment")
        self.plot_area.setReadOnly(True)

        layout.addWidget(self.plot_area)
        self.tab_widget.addTab(viz_widget, "Visualization")

    def create_parameter_tab(self):
        """Create parameter editor tab"""
        param_widget = QWidget()
        layout = QVBoxLayout(param_widget)

        # Project settings
        settings_group = QGroupBox("Project Settings")
        settings_layout = QFormLayout(settings_group)

        self.project_name_edit = QLineEdit()
        self.ambient_field_edit = QLineEdit()
        self.ambient_field_edit.setValidator(QDoubleValidator(0, 2, 3))
        self.inclination_edit = QLineEdit()
        self.inclination_edit.setValidator(QDoubleValidator(-90, 90, 2))
        self.azimuth_edit = QLineEdit()
        self.azimuth_edit.setValidator(QDoubleValidator(-180, 180, 2))

        settings_layout.addRow("Project Name:", self.project_name_edit)
        settings_layout.addRow("Ambient Field:", self.ambient_field_edit)
        settings_layout.addRow("Inclination (°):", self.inclination_edit)
        settings_layout.addRow("Azimuth (°):", self.azimuth_edit)

        # Update button
        update_settings_btn = QPushButton("Update Settings")
        update_settings_btn.clicked.connect(self.update_project_settings)
        settings_layout.addRow(update_settings_btn)

        layout.addWidget(settings_group)

        # Model parameters table
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(4)
        self.param_table.setHorizontalHeaderLabels(["Polygon", "Density", "Susceptibility", "Strike Length"])
        self.param_table.setMaximumHeight(300)

        # Update button for parameters
        update_params_btn = QPushButton("Update Parameters")
        update_params_btn.clicked.connect(self.update_model_parameters)

        layout.addWidget(self.param_table)
        layout.addWidget(update_params_btn)

        self.tab_widget.addTab(param_widget, "Parameters")

    def create_results_tab(self):
        """Create results display tab"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setPlainText("Inversion results will be displayed here")
        self.results_text.setReadOnly(True)

        layout.addWidget(self.results_text)

        self.tab_widget.addTab(results_widget, "Results")

    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        new_action = QAction('New Project', self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        load_action = QAction('Load Project', self)
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)

        save_action = QAction('Save Project', self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        # Help menu
        help_menu = menubar.addMenu('Help')

        validate_action = QAction('Validate Project', self)
        validate_action.triggered.connect(self.validate_project)
        help_menu.addAction(validate_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()

        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def apply_styling(self):
        """Apply application styling"""
        # Set a modern font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

    def new_project(self):
        """Create a new project"""
        result = self.api.create_new_project("New Project")
        self.handle_api_result(result, "New project created")

    def load_project(self):
        """Load a project file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Project", "", "JSON files (*.json)"
        )

        if file_path:
            result = self.api.load_project(file_path)
            self.handle_api_result(result, "Project loaded")
            if result["success"]:
                self.update_ui_from_project()

    def save_project(self):
        """Save the current project"""
        if not self.api.current_model:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "JSON files (*.json)"
        )

        if file_path:
            result = self.api.save_project(file_path)
            self.handle_api_result(result, "Project saved")

    def update_project_settings(self):
        """Update project settings from UI"""
        updates = {}
        try:
            if self.project_name_edit.text():
                updates["project_name"] = self.project_name_edit.text()
            if self.ambient_field_edit.text():
                updates["ambient_field"] = float(self.ambient_field_edit.text())
            if self.inclination_edit.text():
                updates["inclination"] = float(self.inclination_edit.text())
            if self.azimuth_edit.text():
                updates["azimuth"] = float(self.azimuth_edit.text())

            if updates:
                result = self.api.update_model_parameters(updates)
                self.handle_api_result(result, "Settings updated")

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"Please enter valid numbers: {e}")

    def update_model_parameters(self):
        """Update model parameters from table"""
        if not self.api.current_model:
            return

        polygons = []
        try:
            for row in range(self.param_table.rowCount()):
                poly_id = int(self.param_table.item(row, 0).text()) if self.param_table.item(row, 0) else row + 1
                density = float(self.param_table.item(row, 1).text()) if self.param_table.item(row, 1) else 0.0
                susceptibility = float(self.param_table.item(row, 2).text()) if self.param_table.item(row, 2) else 0.0
                strike_length = float(self.param_table.item(row, 3).text()) if self.param_table.item(row, 3) else 100.0

                polygons.append({
                    "id": poly_id,
                    "density": density,
                    "susceptibility": susceptibility,
                    "strike_length": strike_length
                })

            if polygons:
                result = self.api.update_model_parameters({"polygons": polygons})
                self.handle_api_result(result, "Parameters updated")

        except (ValueError, AttributeError) as e:
            QMessageBox.warning(self, "Invalid Input", f"Please enter valid numbers: {e}")

    def run_inversion(self):
        """Run the inversion algorithm"""
        if not self.api.current_model:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, self.iterations_spin.value())
        self.run_button.setEnabled(False)
        self.status_label.setText("Running inversion...")

        # Run inversion in background thread
        self.worker = InversionWorker(
            self.api,
            self.iterations_spin.value(),
            self.adjust_params_check.isChecked()
        )
        self.worker.progress.connect(self.on_inversion_progress)
        self.worker.finished.connect(self.on_inversion_finished)
        self.worker.error.connect(self.on_inversion_error)
        self.worker.start()

    def on_inversion_progress(self, progress: InversionProgress):
        """Handle inversion progress updates"""
        self.progress_bar.setValue(progress.iteration)
        self.status_label.setText(progress.message)

        # Update results tab with current progress
        self.results_text.append(f"{progress.message}")

    def on_inversion_finished(self, result):
        """Handle inversion completion"""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)

        if result["success"]:
            self.status_label.setText("Inversion completed")
            self.update_results_display(result)
            self.update_parameter_table()
        else:
            self.status_label.setText("Inversion failed")
            self.results_text.setPlainText(f"Error: {result.get('message', 'Unknown error')}")
            if "errors" in result:
                for error in result["errors"]:
                    self.results_text.append(f"  - {error}")

    def on_inversion_error(self, error_msg):
        """Handle inversion error"""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.status_label.setText("Inversion failed")
        self.results_text.setPlainText(f"Error: {error_msg}")

    def update_ui_from_project(self):
        """Update UI elements with current project data"""
        if not self.api.current_model:
            return

        # Update project explorer
        self.update_project_explorer()

        # Update settings fields
        project_info = self.api.get_project_info()
        if project_info:
            self.project_name_edit.setText(project_info.get("name", ""))
            self.ambient_field_edit.setText(str(project_info.get("ambient_field", "")))
            self.inclination_edit.setText(str(project_info.get("inclination", "")))
            self.azimuth_edit.setText(str(project_info.get("azimuth", "")))

        # Update parameter table
        self.update_parameter_table()

        # Update results
        self.results_text.setPlainText(f"Project loaded: {self.api.current_model.project_name}\n"
                                     f"Stations: {self.api.current_model.nstat}\n"
                                     f"Polygons: {self.api.current_model.npoly}")

    def update_parameter_table(self):
        """Update the parameter table with current model data"""
        params = self.api.get_model_parameters()
        if not params:
            return

        self.param_table.setRowCount(params["total_polygons"])
        for i, poly in enumerate(params["polygons"]):
            self.param_table.setItem(i, 0, QTableWidgetItem(str(poly["id"])))
            self.param_table.setItem(i, 1, QTableWidgetItem(f"{poly['density']:.4f}"))
            self.param_table.setItem(i, 2, QTableWidgetItem(f"{poly['susceptibility']:.4f}"))
            self.param_table.setItem(i, 3, QTableWidgetItem(f"{poly['strike_length']:.1f}"))

    def update_results_display(self, result):
        """Update results display with inversion results"""
        results_text = "Inversion Results:\n\n"

        if "results" in result and result["results"]:
            results = result["results"]
            if "polygons" in results:
                results_text += "Final Model Parameters:\n"
                for poly in results["polygons"]:
                    results_text += f"Polygon {poly['id']}: Density={poly['density']:.4f}, "
                    results_text += f"Susceptibility={poly['susceptibility']:.4f}, "
                    results_text += f"Strike Length={poly['strike_length']:.1f}\n"

            if "chi_squared" in results and results["chi_squared"] is not None:
                results_text += f"\nFinal Chi-squared: {results['chi_squared']:.2f}"

        self.results_text.setPlainText(results_text)

    def validate_project(self):
        """Validate the current project"""
        result = self.api.validate_project()

        if result["valid"]:
            QMessageBox.information(self, "Validation", "Project is valid!")
        else:
            error_msg = result["message"]
            QMessageBox.warning(self, "Validation Errors", error_msg)

    def handle_api_result(self, result, success_message):
        """Handle API result and show appropriate message"""
        if result["success"]:
            self.status_label.setText(success_message)
            if "project_info" in result and result["project_info"]:
                self.update_ui_from_project()
        else:
            self.status_label.setText("Operation failed")
            error_msg = result.get("message", "Unknown error")
            if "errors" in result:
                error_msg += "\n\nErrors:\n" + "\n".join(f"  - {e}" for e in result["errors"])
            QMessageBox.warning(self, "Error", error_msg)


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