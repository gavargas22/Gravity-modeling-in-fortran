import json
import csv
import numpy as np
import pandas as pd
import pathlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .inversion_complete import execute_inversion_complete
from .types import InversionProgress


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
        self.elev = self.measurements.get('elev', np.zeros(self.nstat)).values if hasattr(self.measurements.get('elev', None), 'values') else np.zeros(self.nstat)

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

    def load_model_geometry(self):
        """Load polygon geometry from model CSV file"""
        model_file = self.inputs_dir.joinpath("model_1.csv")
        if model_file.exists():
            model_data = pd.read_csv(model_file)

            # Group by unit (polygon number)
            polygons = model_data.groupby('unit')

            self.npoly = len(polygons)
            self.nsides = np.zeros(self.npoly, dtype=int)
            self.z = np.zeros((self.npoly, 25))
            self.x = np.zeros((self.npoly, 25))
            self.sl = np.zeros(self.npoly)
            self.densty = np.zeros(self.npoly)
            self.suscp = np.zeros(self.npoly)

            for i, (poly_id, poly_data) in enumerate(polygons):
                vertices = poly_data[['x', 'z']].values
                n_vertices = len(vertices)
                self.nsides[i] = n_vertices - 1  # number of sides = vertices - 1

                # Store vertices
                for j in range(n_vertices):
                    self.x[i, j] = vertices[j, 0]
                    self.z[i, j] = vertices[j, 1]

                # Set default strike length (would be in config)
                self.sl[i] = 100.0

                # Set default physical properties (would be in config)
                self.densty[i] = -0.2  # g/cm³
                self.suscp[i] = 0.0    # SI units
        else:
            # Default single polygon for testing
            self.npoly = 1
            self.nsides = np.array([6])
            self.z = np.zeros((12, 25))
            self.x = np.zeros((12, 25))
            self.sl = np.array([100.0])
            self.densty = np.array([-0.2])
            self.suscp = np.array([0.0])

            # Simple rectangular polygon
            self.x[0, :7] = [-1000, 1000, 45, 24.4, 10.175, 0, -1000]
            self.z[0, :7] = [0, 0, -1.94, -2.84, -4, -4.4, -4.4]

    def get_validation_report(self) -> str:
        """Get a formatted validation report"""
        if self.is_valid:
            return "Project is valid"

        report = "Validation Errors:\n"
        for error in self.validation_errors:
            report += f"  - {error}\n"
        return report

    def inversion(self, iterations=10, *args, **kwargs):
        '''
        Inversion Program with progress reporting
        '''
        if not self.is_valid:
            raise ValueError("Cannot run inversion on invalid project")

        # Set progress callback
        if self.progress_callback:
            kwargs['progress_callback'] = self.progress_callback

        execute_inversion_complete(iterations=iterations, model=self, **kwargs)

    def read_data(self, *args, **kwargs):
        '''
        Read Data
        =========

        This function opens up a file located in the place where we store the
        profile .json

        The file must be inside of the inputs folder and named input_data.csv

        Returns a Pandas dataframe with all of the data measurements
        '''
        data_loc = self.inputs_dir.joinpath("input_data.csv")
        data = pd.read_csv(data_loc.__str__()).dropna(axis=1)

        return(data)

    def calculate_magnetic_field_components(self):
        """Calculate magnetic field direction components for talw calculations"""
        # Convert degrees to radians
        incl_rad = np.radians(self.inclination)
        azim_rad = np.radians(self.azimuth)

        # Magnetic field components (similar to Fortran main.f)
        if self.modeling_mode == "magnetics":
            # For magnetics: PXC = cos(incl)*cos(2*azim)
            pxcf = np.cos(incl_rad) * np.cos(2 * azim_rad)
            pzcf = -np.sin(incl_rad)
            qcf = 200000.0 * self.ambient_field
        else:
            # For gravity or default
            pxcf = 0.0
            pzcf = 0.0
            qcf = 0.0

        self.pxcf = pxcf
        self.pzcf = pzcf
        self.qcf = qcf
