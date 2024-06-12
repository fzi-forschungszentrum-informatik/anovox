"""This module, defines the default arguments and configurations for various types of sensors (like cameras and
LIDARs) attached to an ego vehicle in different positions and orientations, for different sensor setups such as mono,
stereo, multi, and surround."""

from EgoVehiculeSensorDefaults import CAMERA_ARGUMENTS, LIDAR_ARGUMENTS

RGB_CAM_TYPE = "RGB-CAM"
DEPTH_CAM_TYPE = "DEPTH_CAM"
INSTANCE_CAM_TYPE = "INSTANCE-CAM"
SEMANTIC_CAM_TYPE = "SEMANTIC-CAM"
LIDAR_TYPE = "LIDAR"
SEMANTIC_LIDAR_TYPE = "SEMANTIC-LIDAR"

ALLOWED_SENSOR_TYPES = [
    RGB_CAM_TYPE,
    INSTANCE_CAM_TYPE,
    SEMANTIC_CAM_TYPE,
    RGB_CAM_TYPE,
    LIDAR_TYPE,
    SEMANTIC_LIDAR_TYPE
]

MONO_SENSOR_SETS = [
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 0),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
]

STEREO_SENSOR_SETS = [
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 0),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, -1, 1.8),
        "rotation": (0, 0, -15),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 1, 1.8),
        "rotation": (0, 0, 15),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
]

STEREO_ONE_LIDAR_SENSOR_SETS = [
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 0),
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, -1, 1.8),
        "rotation": (0, 0, -15),
        "camera_arguments": CAMERA_ARGUMENTS,
    },
    {
        "location": (0, 1, 1.8),
        "rotation": (0, 0, 15),
        "camera_arguments": CAMERA_ARGUMENTS,
    },
]

MULTI_SENSOR_SETS = [
    # centered above car
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 0),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    # at the front tip of car
    {
        "location": (1.5, 0, 1.8),
        "rotation": (0, 0, 0),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    # above right front wheel
    {
        "location": (1, 0.9, 1.8),
        "rotation": (0, 0, 15),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    # above left front wheel
    {
        "location": (1, -0.9, 1.8),
        "rotation": (0, 0, -15),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    # centered at rear tip of car, facing backwards
    {
        "location": (-1.5, 0, 1),
        "rotation": (0, 0, 180),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    # behind right back wheel, facing backwards
    {
        "location": (-1.5, 0.9, 1),
        "rotation": (0, 0, 170),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    # behind left back wheel, facing backwards
    {
        "location": (-1.5, -0.9, 1),
        "rotation": (0, 0, -170),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
]

SURROUND_SENSOR_SETS = [
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 0),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 40),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 80),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 120),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 160),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, -40),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, -80),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, -120),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, -160),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    },
    {
        "location": (0, 0, 1.8),
        "rotation": (0, 0, 180),
        "camera_arguments": CAMERA_ARGUMENTS,
        "lidar_arguments": LIDAR_ARGUMENTS,
    }
]
