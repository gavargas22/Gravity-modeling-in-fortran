import json
import csv
import numpy as np
import pandas as pd
import pathlib
from gmm.inversion import execute_inversion


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
            self.dist = self.measurements.distance
            self.nstat = self.measurements.station.count()
            self.grav = self.measurements.obs_grav
            self.gtot = 0.0
            self.mag = 0.0
            self.mtot = 0.0
            self.npoly = 0.0
            self.nsides = 0.0
            self.z = np.zeros(12, 25)
            self.x = np.zeros(12, 25)
            self.elev = 0.0
            self.sl = 0.0
            self.densty = 0.0
            self.ct = 0.0
            self.suscp = 0.0
            self.nbase = 0.0
            self.ian = 0.0

    def inversion(self, *args, **kwargs):
        '''
        Inversion Program
        '''

        execute_inversion(iterations=10, model=self)

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
