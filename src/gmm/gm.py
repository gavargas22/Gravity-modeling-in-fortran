import json
import csv
import numpy as np
import pandas as pd
import pathlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from gmm.inversion_complete import execute_inversion_complete


@dataclass
class InversionProgress:
    """Data class for inversion progress reporting"""
    iteration: int
    max_iterations: int
    chi_squared: float
    parameters_updated: int
    message: str


class GMModel():
    '''
    Gravity/Magnetics Model
    ---
    Enhanced with validation, serialization, and progress reporting
    '''

    def __init__(self, *args, **kwargs):
        '''
        Initialize Gravity Modeling with enhanced validation
        '''
        # Basic attributes
        self.project_name = ""
        self.ambient_field = 0.0
        self.inclination = 0.0
        self.units = ""
        self.azimuth = 0.0
        self.modeling_mode = ""
        self.project_file = kwargs.get("project_file", "")
        self.new_project = kwargs.get("new_project", False)

        # Validation flags
        self.is_valid = False
        self.validation_errors: List[str] = []

        # Progress callback
        self.progress_callback = kwargs.get("progress_callback", None)

        if self.new_project:
            self._initialize_new_project()
        else:
            self._load_existing_project()

    def _initialize_new_project(self):
        """Initialize a new project with defaults"""
        self.project_name = "New Project"
        self.ambient_field = 0.5
        self.inclination = 60.0
        self.units = "km"
        self.azimuth = 0.0
        self.modeling_mode = "gravity"
        self.num_poly = 1
        self.distance_units = "km"
        self.obs_agreement_station = 1
        self.number_of_stations = 0

        # Initialize empty arrays
        self._initialize_empty_arrays()
        self.is_valid = True

    def _load_existing_project(self):
        """Load existing project with validation"""
        if not self.project_file:
            self.validation_errors.append("No project file specified")
            return

        project_path = pathlib.Path(self.project_file)
        if not project_path.exists():
            self.validation_errors.append(f"Project file not found: {self.project_file}")
            return

        try:
            # Load configuration
            with open(self.project_file, mode="r") as f:
                configuration = json.load(f)

            # Validate required fields
            required_fields = [
                "project_name", "ambient_field", "inclination", "units",
                "azimuth", "modeling_mode", "num_poly", "distance_units",
                "obs_agreement_station"
            ]

            for field in required_fields:
                if field not in configuration:
                    self.validation_errors.append(f"Missing required field: {field}")
                    continue

                setattr(self, field, configuration[field])

            # Load data files
            self.inputs_dir = project_path.parent / "inputs"
            self.outputs_dir = project_path.parent / "outputs"

            if not self.inputs_dir.exists():
                self.validation_errors.append(f"Inputs directory not found: {self.inputs_dir}")
                return

            # Load measurements
            self.measurements = self.read_data()
            if self.measurements is None or self.measurements.empty:
                self.validation_errors.append("Failed to load measurement data")
                return

            self.number_of_stations = len(self.measurements)

            # Load model geometry
            self.load_model_geometry()

            # Initialize computed fields
            self._initialize_computed_fields()

            # Calculate magnetic field components
            self.calculate_magnetic_field_components()

            # Validate data consistency
            self._validate_data_consistency()

            self.is_valid = len(self.validation_errors) == 0

        except json.JSONDecodeError as e:
            self.validation_errors.append(f"Invalid JSON in project file: {e}")
        except Exception as e:
            self.validation_errors.append(f"Error loading project: {e}")

    def _initialize_empty_arrays(self):
        """Initialize empty arrays for new projects"""
        self.dist = np.array([])
        self.nstat = 0
        self.grav = np.array([])
        self.mag = np.array([])
        self.elev = np.array([])
        self.gtot = np.array([])
        self.mtot = np.array([])
        self.npoly = 0
        self.nsides = np.array([])
        self.z = np.zeros((12, 25))
        self.x = np.zeros((12, 25))
        self.sl = np.array([])
        self.densty = np.array([])
        self.suscp = np.array([])

    def _initialize_computed_fields(self):
        """Initialize computed fields from loaded data"""
        self.dist = self.measurements.distance.values
        self.nstat = len(self.measurements)
        self.grav = self.measurements.obs_grav.values
        self.mag = self.measurements.obs_mag.values
        self.elev = self.measurements.get('elev', np.zeros(self.nstat)).values

        # Initialize computed fields
        self.gtot = np.zeros(self.nstat)
        self.mtot = np.zeros(self.nstat)

        # Constants
        self.ct = 6.6666667e-08  # gravitational constant
        self.nbase = self.obs_agreement_station - 1  # 0-based indexing
        self.ian = 0  # magnetic field flag

    def _validate_data_consistency(self):
        """Validate consistency between configuration and data"""
        if self.nstat == 0:
            self.validation_errors.append("No measurement stations found")
            return

        if self.npoly == 0:
            self.validation_errors.append("No polygons defined")
            return

        # Check array sizes
        expected_size = (self.npoly, 25)
        if self.z.shape != expected_size:
            self.validation_errors.append(f"Z array size mismatch: {self.z.shape} vs {expected_size}")
        if self.x.shape != expected_size:
            self.validation_errors.append(f"X array size mismatch: {self.x.shape} vs {expected_size}")

        # Validate physical parameters
        if not (0 <= self.ambient_field <= 2.0):
            self.validation_errors.append(f"Ambient field out of range: {self.ambient_field}")

        if not (-90 <= self.inclination <= 90):
            self.validation_errors.append(f"Inclination out of range: {self.inclination}")

        if self.modeling_mode not in ["gravity", "magnetics", "joint"]:
            self.validation_errors.append(f"Invalid modeling mode: {self.modeling_mode}")

    def save_project(self, filepath: Optional[str] = None) -> bool:
        """Save project to JSON file"""
        if not self.is_valid:
            return False

        save_path = pathlib.Path(filepath or self.project_file)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            config = {
                "project_name": self.project_name,
                "ambient_field": self.ambient_field,
                "inclination": self.inclination,
                "units": self.units,
                "azimuth": self.azimuth,
                "modeling_mode": self.modeling_mode,
                "num_poly": self.npoly,
                "distance_units": self.distance_units,
                "obs_agreement_station": self.obs_agreement_station,
                "number_of_stations": self.number_of_stations
            }

            with open(save_path, 'w') as f:
                json.dump(config, f, indent=2)

            # Save model geometry if modified
            self.save_model_geometry()

            return True

        except Exception as e:
            self.validation_errors.append(f"Error saving project: {e}")
            return False

    def save_model_geometry(self):
        """Save polygon geometry to CSV"""
        if not hasattr(self, 'inputs_dir'):
            return

        model_file = self.inputs_dir / "model_1.csv"

        try:
            with open(model_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['x', 'y', 'z', 'unit'])

                for i in range(self.npoly):
                    for j in range(self.nsides[i] + 1):  # +1 for closing vertex
                        writer.writerow([
                            self.x[i, j],
                            0.0,  # y coordinate (always 0 for 2D profiles)
                            self.z[i, j],
                            i + 1  # polygon unit number
                        ])

        except Exception as e:
            print(f"Warning: Could not save model geometry: {e}")

    def get_validation_report(self) -> str:
        """Get a formatted validation report"""
        if self.is_valid:
            return "Project is valid"

        report = "Validation Errors:\n"
        for error in self.validation_errors:
            report += f"  - {error}\n"
        return report

    def inversion(self, *args, **kwargs):
        '''
        Inversion Program with progress reporting
        '''
        if not self.is_valid:
            raise ValueError("Cannot run inversion on invalid project")

        # Set progress callback
        if self.progress_callback:
            kwargs['progress_callback'] = self.progress_callback

        execute_inversion_complete(iterations=10, model=self, **kwargs)
