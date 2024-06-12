"""
This file contains utility functions for scenarios.
"""
import json
from queue import Queue

import Definitions
from DataAnalysis.DataGenerator import image_callback, lidar_callback, semantic_lidar_callback
from Definitions import AnomalyTypes
from EgoVehiculeSensorDefaults import CAMERA_ARGUMENTS, LIDAR_ARGUMENTS
from EgoVehicleSetup import RGB_CAM_TYPE, DEPTH_CAM_TYPE, INSTANCE_CAM_TYPE, SEMANTIC_CAM_TYPE, \
    LIDAR_TYPE, \
    SEMANTIC_LIDAR_TYPE
from Models.World import World


def _create_sensor_name(sensor_type, location, rotation, sensor_arguments):
    name = sensor_type + str(location) + str(rotation) + '_' + str(
        abs(hash(json.dumps(sensor_arguments, sort_keys=True))))
    return name


def construct_cameras_and_sensors(ego_vehicle):
    """
    Constructs and attaches cameras and sensors to the specified ego vehicle.
    """

    transforms = dict()
    sensors = dict()
    for sensor_set in Definitions.CURRENT_SENSOR_SETS[0]:
        location = sensor_set['location']
        rotation = sensor_set['rotation']
        has_camera = bool(sensor_set.get('camera_arguments'))
        has_lidar = bool(sensor_set.get('lidar_arguments'))
        camera_args = sensor_set['camera_arguments'] if has_camera else CAMERA_ARGUMENTS
        lidar_args = sensor_set['lidar_arguments'] if has_lidar else LIDAR_ARGUMENTS
        # sensors[(location, rotation)] = dict()
        transforms[(location, rotation)] = dict()

        sensors[_create_sensor_name(RGB_CAM_TYPE, location, rotation, camera_args)] = {
            "sensor": World.attach_camera_to_vehicle(
                World.WORLD_STATE,
                ego_vehicle,
                camera_name=Definitions.CAMERA_NAME,
                location=location,
                rotation=rotation
            ),
            'sensor_type': RGB_CAM_TYPE,
            'dataformat': Definitions.DataFormat.RGB_IMG,
            'file_ending': Definitions.DataFormat.RGB_IMG.value,
            'callback': image_callback,
            'location': location,
            'rotation': rotation,
            'args': camera_args,
            'save_data': has_camera
        }
        transforms[(location, rotation)]['camera'] = \
        sensors[_create_sensor_name(RGB_CAM_TYPE, location, rotation, camera_args)][
            'sensor'].get_transform()

        sensors[_create_sensor_name(DEPTH_CAM_TYPE, location, rotation, camera_args)] = {
            "sensor": World.attach_camera_to_vehicle(
                World.WORLD_STATE,
                ego_vehicle,
                camera_name=Definitions.DEPTH_NAME,
                location=location,
                rotation=rotation
            ),
            'sensor_type': DEPTH_CAM_TYPE,
            'dataformat': Definitions.DataFormat.DEPTH_IMG,
            'file_ending': Definitions.DataFormat.DEPTH_IMG.value,
            'callback': image_callback,
            'location': location,
            'rotation': rotation,
            'args': camera_args,
            'save_data': has_camera
        }
        sensors[_create_sensor_name(SEMANTIC_CAM_TYPE, location, rotation, camera_args)] = {
            "sensor": World.attach_camera_to_vehicle(
                World.WORLD_STATE,
                ego_vehicle,
                camera_name=Definitions.SEMANTIC_CAMERA_NAME,
                location=location,
                rotation=rotation
            ),
            'sensor_type': SEMANTIC_CAM_TYPE,
            'dataformat': Definitions.DataFormat.SEMANTIC_IMG,
            'file_ending': Definitions.DataFormat.SEMANTIC_IMG.value,
            'callback': image_callback,
            'location': location,
            'rotation': rotation,
            'args': camera_args,
            'save_data': has_camera
        }
        sensors[_create_sensor_name(INSTANCE_CAM_TYPE, location, rotation, camera_args)] = {
            'sensor': World.attach_camera_to_vehicle(
                World.WORLD_STATE,
                ego_vehicle,
                camera_name=Definitions.INSTANCE_CAMERA_NAME,
                location=location,
                rotation=rotation
            ),
            'sensor_type': INSTANCE_CAM_TYPE,
            'dataformat': Definitions.DataFormat.INSTANCE_IMG,
            'file_ending': Definitions.DataFormat.INSTANCE_IMG.value,
            'callback': image_callback,
            'location': location,
            'rotation': rotation,
            'args': camera_args,
            'save_data': has_camera
        }
        sensors[_create_sensor_name(LIDAR_TYPE, location, rotation, lidar_args)] = {
            'sensor': World.spawn_lidar_to_vehicle(
                World.WORLD_STATE,
                ego_vehicle,
                name=Definitions.LIDAR_NAME,
                location=location,
                rotation=rotation
            ),
            'sensor_type': LIDAR_TYPE,
            'dataformat': Definitions.DataFormat.PCD,
            'file_ending': Definitions.DataFormat.PCD.value,
            'callback': lidar_callback,
            'location': location,
            'rotation': rotation,
            'args': lidar_args,
            'save_data': has_lidar
        }
        transforms[(location, rotation)]['lidar'] = \
        sensors[_create_sensor_name(LIDAR_TYPE, location, rotation, lidar_args)][
            'sensor'].get_transform()

        sensors[_create_sensor_name(SEMANTIC_LIDAR_TYPE, location, rotation, lidar_args)] = {
            'sensor': World.spawn_lidar_to_vehicle(
                World.WORLD_STATE,
                ego_vehicle,
                name=Definitions.SEMANTIC_LIDAR_NAME,
                location=location,
                rotation=rotation
            ),
            'sensor_type': SEMANTIC_LIDAR_TYPE,
            'dataformat': Definitions.DataFormat.SEMANTIC_PCD,
            'file_ending': Definitions.DataFormat.SEMANTIC_PCD.value,
            'callback': semantic_lidar_callback,
            'location': location,
            'rotation': rotation,
            'args': lidar_args,
            'save_data': has_lidar
        }

    return sensors, transforms


def build_scenario_config(scenario, ego_vehicle):
    """
    Builds a scenario configuration dictionary.
    """
    return {
        "anomaly_config": scenario["anomaly_config"],
        "anomaly_type": AnomalyTypes[scenario["anomaly_config"]["anomalytype"]].name,
        "scenario_id": scenario["id"],
        "ego_vehicle": ego_vehicle,
        "scenario": scenario,
        "npc_walker_amount": scenario["npc_walker_amount"],
        "npc_vehicle_amount": scenario["npc_vehicle_amount"],
    }


def start_listening_cameras_lidars(sensors, image_lidar_queues):
    """
    Start listening to cameras and lidars. Starts listening to the given cameras and lidars and puts the captured
    images and lidar data into the respective queues.
    """

    for sensor_name in sensors:
        sensors[sensor_name]['sensor'].listen(image_lidar_queues[sensor_name].put)


def initialize_cameras_and_sensors_queues(sensors):
    """
    Initialize queues for each sensor.
    """
    image_lidar_queues = {sensor_name: Queue() for sensor_name in sensors}
    return image_lidar_queues


def stop_sensors(sensors):
    """
    Stops all sensors in the dict. Otherwise, they will be running in the background.
    """
    for sensor in sensors.values():
        if sensor['sensor'].is_alive:
            sensor['sensor'].stop()
