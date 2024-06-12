"""This module defines classes for representing data related to actions, frames, and worlds in a scenario,
with functionality for generating output files and saving various types of data."""
import numpy as np
from PIL import Image

from DataAnalysis import OutputGenerator
from EgoVehicleSetup import RGB_CAM_TYPE, DEPTH_CAM_TYPE, INSTANCE_CAM_TYPE, SEMANTIC_CAM_TYPE, LIDAR_TYPE, \
    SEMANTIC_LIDAR_TYPE


# ======================================================================================================================
# region -- ACTION_DATA ------------------------------------------------------------------------------------------------
# ======================================================================================================================
class ActionData:
    """
    A class representing the data for an action.
    """

    def __init__(
            self,
            scenario_id,
            frame_id,
            action_dict,
            anomaly_dict,
    ):
        self.scenario_id = scenario_id
        self.frame_id = frame_id
        self.action_dict = action_dict
        self.anomaly_dict = anomaly_dict
        self._action_csv_path = None
        self.action_csv_path
        self._anomaly_csv_path = None
        self.anomaly_csv_path

    @property
    def action_dict(self):
        return self._action_dict

    @action_dict.setter
    def action_dict(self, action_dict):
        self._action_dict = action_dict

    @property
    def action_csv_path(self):
        if not self._action_csv_path:
            self._action_csv_path = OutputGenerator.generate_action_csv(self)
        return self._action_csv_path

    @property
    def anomaly_csv_path(self):
        if not self._anomaly_csv_path and self.anomaly_dict != None:
            self._anomaly_csv_path = OutputGenerator.generate_anomaly_csv(self)
        return self._anomaly_csv_path


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- FRAMEDATA --------------------------------------------------------------------------------------------------
# ======================================================================================================================
class FrameData:
    """
    Class representing a frame of data in a data set.contains all types of data relevant to finished data set
    """

    def __init__(self, frame_id, scenario_id):
        # Tuple of scenario ID and frame number
        self.frame_id = frame_id
        self.scenario_id = scenario_id
        self.anomalies = []  # List to store anomalies
        self.route_map = None
        self.route_map_data = None

        # AnoVox is a path to .ply file
        self._action_state_dict = None

        # dict with sensor data with location+rotation for keys
        self.sensor_data = dict()
        # {
        #     ((0, 0, 1.8), (0, 0, 0)): {
        #         'RGB-CAM': {'file_path': <str>, 'data': <camera data>},
        #         'DEPTH_CAM': {'file_path': <str>, 'data': <depth camera data>},
        #         'LIDAR': {'file_path': <str>, 'data': <lidar data>},
        #         ...
        #     },
        #     ((0, -1, 1.8), (0, 0, 0)): {
        #         'RGB-CAM': {'file_path': <str>, 'data': <camera data>},
        #         'DEPTH_CAM': {'file_path': <str>, 'data': <depth camera data>},
        #         'LIDAR': {'file_path': <str>, 'data': <lidar data>},
        #         ...
        #     }
        # }

    def set_point_ids(self, point_ids, location, rotation):
        if not self.sensor_data.get((location, rotation)):
            self.sensor_data[(location, rotation)] = dict()
        if not self.sensor_data[(location, rotation)].get(SEMANTIC_LIDAR_TYPE):
            self.sensor_data[(location, rotation)][SEMANTIC_LIDAR_TYPE] = dict()

        self.sensor_data[(location, rotation)][SEMANTIC_LIDAR_TYPE]['point_ids'] = point_ids

    def set_data(
            self,
            file_path,
            raw_data,
            sensor_type,
            location,
            rotation,
            save_data
    ):
        if not self.sensor_data.get((location, rotation)):
            self.sensor_data[(location, rotation)] = dict()
        self.sensor_data[(location, rotation)][sensor_type] = {
            'file_path': file_path,
            'data': raw_data,
            'save_data': save_data
        }

    def set_route_map(self, file_path, raw_data):
        self.route_map = file_path
        self.route_map_data = raw_data

    def save_files(self):

        for location_rotation in self.sensor_data:
            for sensor_type in self.sensor_data[location_rotation]:
                if self.sensor_data[location_rotation][sensor_type]['save_data']:
                    if sensor_type in (RGB_CAM_TYPE, DEPTH_CAM_TYPE, SEMANTIC_CAM_TYPE, INSTANCE_CAM_TYPE):
                        im = Image.fromarray(self.sensor_data[location_rotation][sensor_type]['data'])
                        im.save(self.sensor_data[location_rotation][sensor_type]['file_path'])
                    elif sensor_type in (LIDAR_TYPE, SEMANTIC_LIDAR_TYPE):
                        np.save(
                            self.sensor_data[location_rotation][sensor_type]['file_path'],
                            self.sensor_data[location_rotation][sensor_type]['data']
                        )

    def save_route_map(self):
        route_map = Image.fromarray((self.route_map_data * 255).astype(np.uint8), mode='L')
        route_map.save(self.route_map)


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- WORLD ------------------------------------------------------------------------------------------------------
# ======================================================================================================================
class World:
    """
    A class representing a world.
    """

    def __init__(self, world):
        self.world = world

# endregion
# ======================================================================================================================
