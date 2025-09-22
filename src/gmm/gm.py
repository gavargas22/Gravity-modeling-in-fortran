import json
import csv
import numpy as np
import pandas as pd
import pathlib
from .inversion import execute_inversion


class GMModel():
    '''
    Gravity/Magnetics Model
    ---
    '''
    def __init__(self, *args, **kwargs):
        '''
        Initialize Gravity Modeling
        '''
        self.project_name = ""
        self.ambient_field = 0.0
        self.inclination = 0.0
        self.units = ""
        self.azimuth = 0.0
        self.modeling_mode = ""
        self.project_file = kwargs["project_file"]
        self.new_project = kwargs["new_project"]

        if self.new_project:
            # Take all the parameters and create a new save file
            # Check what modeling we want
            if self.modeling_mode == "gravity":
                # Do gravity modeling
                pass
            elif self.modeling_mode == "magnetics":
                # Do a magnetics model
                pass
        else:
            # Grab the configurations from the json file
            f = open(self.project_file, mode="r")
            configuration = json.load(f)

            self.project_name = configuration["project_name"]
            self.ambient_field = configuration["ambient_field"]
            self.inclination = configuration["inclination"]
            self.units = configuration["units"]
            self.azimuth = configuration["azimuth"]
            self.modeling_mode = configuration["modeling_mode"]
            self.num_poly = configuration["num_poly"]
            self.distance_units = configuration["distance_units"]
            self.obs_agreement_station = configuration["obs_agreement_station"]
            self.inputs_dir = pathlib.Path(self.project_file)\
                .parent.resolve().joinpath("inputs")
            self.outputs_dir = pathlib.Path(self.project_file)\
                .parent.resolve().joinpath("outputs")
            self.measurements = self.read_data()
            self.number_of_stations = self.measurements.shape[0]
            # Data about the model
            self.dist = self.measurements.distance.values
            self.nstat = len(self.measurements)
            self.grav = self.measurements.obs_grav.values
            self.mag = self.measurements.obs_mag.values
            self.elev = self.measurements.elev.values if 'elev' in self.measurements.columns else np.zeros(self.nstat)

            # Load model geometry
            self.load_model_geometry()

            # Initialize computed fields
            self.gtot = np.zeros(self.nstat)
            self.mtot = np.zeros(self.nstat)

            # Constants
            self.ct = 6.6666667e-08  # gravitational constant
            self.nbase = self.obs_agreement_station - 1  # 0-based indexing
            self.ian = 0  # magnetic field flag

    def inversion(self, *args, **kwargs):
        '''
        Inversion Program
        '''
        from .inversion_complete import execute_inversion_complete
        execute_inversion_complete(iterations=10, model=self)

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
