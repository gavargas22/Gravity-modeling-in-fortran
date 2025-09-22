"""
Modern PySide6 GUI application for Gravity and Magnetics Modeling
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QStatusBar, QMenuBar, QMenu,
    QProgressBar, QLabel, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QFont

from gmm.gm import GMModel


class InversionWorker(QThread):
    """Worker thread for running inversion in background"""
    progress = Signal(int)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        try:
            # Run inversion (this will be updated to emit progress)
            self.model.inversion()
            self.finished.emit(self.model)
        except Exception as e:
            self.error.emit(str(e))


class GravityModelingApp(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.current_model = None
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
        root = QTreeWidgetItem(self.project_explorer)
        root.setText(0, "Test Project 1")
        root.setExpanded(True)

        inputs = QTreeWidgetItem(root)
        inputs.setText(0, "Inputs")
        inputs.addChild(QTreeWidgetItem(["input_data.csv"]))
        inputs.addChild(QTreeWidgetItem(["model_1.csv"]))

        outputs = QTreeWidgetItem(root)
        outputs.setText(0, "Outputs")
        outputs.addChild(QTreeWidgetItem(["OUTPUT.TXT"]))

    def create_main_content(self):
        """Create the main content area with tabs"""
        self.main_content = QWidget()
        layout = QVBoxLayout(self.main_content)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Data Visualization Tab
        self.create_visualization_tab()

        # Parameter Editor Tab
        self.create_parameter_tab()

        # Results Tab
        self.create_results_tab()

        layout.addWidget(self.tab_widget)

    def create_visualization_tab(self):
        """Create data visualization tab"""
        viz_widget = QWidget()
        layout = QVBoxLayout(viz_widget)

        # Placeholder for matplotlib plots
        plot_area = QTextEdit()
        plot_area.setPlainText("Data visualization will be implemented here\n"
                             "- Profile plot (observed vs calculated)\n"
                             "- Residual plot\n"
                             "- Model geometry view")
        plot_area.setReadOnly(True)

        layout.addWidget(plot_area)
        self.tab_widget.addTab(viz_widget, "Visualization")

    def create_parameter_tab(self):
        """Create parameter editor tab"""
        param_widget = QWidget()
        layout = QVBoxLayout(param_widget)

        # Project settings
        settings_text = QTextEdit()
        settings_text.setPlainText("Project Settings:\n"
                                 "- Ambient field: 0.55\n"
                                 "- Inclination: 65.0°\n"
                                 "- Azimuth: 0.0°\n"
                                 "- Modeling mode: Gravity\n"
                                 "- Units: km")
        settings_text.setMaximumHeight(150)

        # Model parameters table
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(4)
        self.param_table.setHorizontalHeaderLabels(["Polygon", "Density", "Susceptibility", "Strike Length"])
        self.param_table.setRowCount(5)  # For 5 polygons

        # Populate with current model data if available
        if self.current_model:
            for i in range(self.current_model.npoly):
                self.param_table.setItem(i, 0, QTableWidgetItem(f"{i+1}"))
                self.param_table.setItem(i, 1, QTableWidgetItem(f"{self.current_model.densty[i]:.3f}"))
                self.param_table.setItem(i, 2, QTableWidgetItem(f"{self.current_model.suscp[i]:.3f}"))
                self.param_table.setItem(i, 3, QTableWidgetItem(f"{self.current_model.sl[i]:.1f}"))

        layout.addWidget(settings_text)
        layout.addWidget(self.param_table)

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

        load_action = QAction('Load Project', self)
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)

        run_action = QAction('Run Inversion', self)
        run_action.triggered.connect(self.run_inversion)
        file_menu.addAction(run_action)

        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        # Help menu
        help_menu = menubar.addMenu('Help')

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()

        # Progress bar for long operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def apply_styling(self):
        """Apply application styling"""
        # Set a modern font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

    def load_project(self):
        """Load a project file"""
        try:
            # For now, load the test project
            project_path = Path("models/test1/test1.json")
            if project_path.exists():
                self.current_model = GMModel(project_file=str(project_path), new_project=False)
                self.status_label.setText(f"Loaded project: {self.current_model.project_name}")
                self.update_parameter_table()
                self.results_text.setPlainText(f"Model loaded successfully\n"
                                             f"Stations: {self.current_model.nstat}\n"
                                             f"Polygons: {self.current_model.npoly}")
            else:
                self.status_label.setText("Test project not found")
        except Exception as e:
            self.status_label.setText(f"Error loading project: {str(e)}")

    def update_parameter_table(self):
        """Update the parameter table with current model data"""
        if self.current_model:
            self.param_table.setRowCount(self.current_model.npoly)
            for i in range(self.current_model.npoly):
                self.param_table.setItem(i, 0, QTableWidgetItem(f"{i+1}"))
                self.param_table.setItem(i, 1, QTableWidgetItem(f"{self.current_model.densty[i]:.3f}"))
                self.param_table.setItem(i, 2, QTableWidgetItem(f"{self.current_model.suscp[i]:.3f}"))
                self.param_table.setItem(i, 3, QTableWidgetItem(f"{self.current_model.sl[i]:.1f}"))

    def run_inversion(self):
        """Run the inversion algorithm"""
        if not self.current_model:
            self.status_label.setText("No project loaded")
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Running inversion...")

        # Run inversion in background thread
        self.worker = InversionWorker(self.current_model)
        self.worker.finished.connect(self.on_inversion_finished)
        self.worker.error.connect(self.on_inversion_error)
        self.worker.start()

    def on_inversion_finished(self, model):
        """Handle inversion completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Inversion completed")
        self.update_parameter_table()

        # Display results
        results = "Inversion Results:\n\n"
        for i in range(model.npoly):
            results += f"Polygon {i+1}: Density={model.densty[i]:.3f}, Susceptibility={model.suscp[i]:.3f}\n"

        self.results_text.setPlainText(results)

    def on_inversion_error(self, error_msg):
        """Handle inversion error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Inversion failed")
        self.results_text.setPlainText(f"Error: {error_msg}")


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

    # Load test project on startup
    window.load_project()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()