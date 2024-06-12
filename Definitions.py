"""This module serves as a configuration file for interacting with the CARLA simulator in the context of autonomous
driving research. It defines various parameters and settings related to the simulation environment, including
connection details, logging configuration, synchronous mode settings, scenario configurations, weather and anomaly
specifications, NPC (Non-Player Character) configurations, and data processing parameters."""

import logging
from collections import namedtuple

import numpy as np
from aenum import Enum, NoAlias

from EgoVehicleSetup import MONO_SENSOR_SETS, STEREO_SENSOR_SETS, STEREO_ONE_LIDAR_SENSOR_SETS, SURROUND_SENSOR_SETS

# ======================================================================================================================
# region -- GENERAL ----------------------------------------------------------------------------------------------------
# ======================================================================================================================

HOST = "localhost"
"""Host, on which the carla server is run."""

PORT = 2000
"""Port, on which the carla server is run."""

TIMEOUT = 10000  # Default is 5sec
"""Timeout for carla connection"""

# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- SYNCHRONOUS MODE -------------------------------------------------------------------------------------------
# ======================================================================================================================

FIXED_DELTA_SECONDS = 0.1  # FIXED_DELTA_SECONDS <= MAX_SUBSTEP_DELTA_TIME * MAX_SUBSTEP
SUBSTEPPING = True
MAX_SUBSTEP = 10  # Carla 0.9.14 have maximum of 10 physics substeps
MAX_SUBSTEP_DELTA_TIME = 0.01  # Carla 0.9.14 have maximum of 0.01 delta time

MAX_TICKCOUNT = 215  # 15 Ticks for spawning, 200 Ticks for driving (200 * 0.1 = 20 seconds)

TICK_COUNT_MODULO_VALUE = 1
"""
By changing this you change the interval in which data gets "recorded" - 2 means every second tick. 
With fixed delta seconds 0.1 (100ms) with 400 max Tick count means every second data package out of 400 - which is 200.
"""

# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- SCENARIO CONFIG --------------------------------------------------------------------------------------------
# ======================================================================================================================

NBR_OF_SCENARIOS = 1
"""Number of Scenarios in the desired dataset. Set as you wish."""

USED_MAPS = [
    # "Town01",
    # "Town02",
    # "Town03",
    # "Town04",
    # "Town05",
    # "Town06",
    # "Town07",
    "Town10HD",
]
"""
Towns to be used in the dataset.
Uncomment every Map that should be used in the dataset.

Warning: Do not uncomment more towns than the value of NBR_OF_SCENARIOS.
"""

TOWN_CONFIGS = {
    "Town01": {
        "npc_vehicle_amount": 100,
        "npc_walker_amount": 200,
    },
    "Town02": {
        "npc_vehicle_amount": 50,
        "npc_walker_amount": 100,
    },
    "Town03": {
        "npc_vehicle_amount": 200,
        "npc_walker_amount": 150,
    },
    "Town04": {
        "npc_vehicle_amount": 250,
        "npc_walker_amount": 100,
    },
    "Town05": {
        "npc_vehicle_amount": 150,
        "npc_walker_amount": 150,
    },
    "Town06": {
        "npc_vehicle_amount": 150,
        "npc_walker_amount": 50,
    },
    "Town07": {
        "npc_vehicle_amount": 50,
        "npc_walker_amount": 100,
    },
    "Town10HD": {
        "npc_vehicle_amount": 150,
        "npc_walker_amount": 150,
    }
}
"""
Set the amount of NPCS per town. It could be that there are fewer NPCs if there are not enough spawn points available.
"""

EGO_VEHICLE = "vehicle.lincoln.mkz_2020"
"""Carla Blueprint ID of the ego vehicle."""


class WeatherPresets(Enum):
    """
    The WeatherPresets class is an enumeration that represents different weather presets for specific times of day.
    Each preset is represented by a string value.
    """

    CLEAR_NOON = "ClearNoon"
    CLOUDY_NOON = "CloudyNoon"
    WET_NOON = "WetNoon"
    WET_CLOUDY_NOON = "WetCloudyNoon"
    MID_RAINY_NOON = "MidRainyNoon"
    HARD_RAIN_NOON = "HardRainNoon"
    SOFT_RAIN_NOON = "SoftRainNoon"
    CLEAR_SUNSET = "ClearSunset"
    CLOUDY_SUNSET = "CloudySunset"
    WET_SUNSET = "WetSunset"
    WET_CLOUDYSUNSET = "WetCloudySunset"
    MID_RAIN_SUNSET = "MidRainSunset"
    HARD_RAIN_SUNSET = "HardRainSunset"
    SOFT_RAIN_SUNSET = "SoftRainSunset"


"""
WEATHER_PRESETS to be used in the dataset
Uncomment every WEATHER_PRESET that should be used in the dataset.
"""


class AnomalyTypes(Enum):
    """
    Enum class for different types of anomalies.
    """
    NORMALITY = "normality"
    STATIC = "static"
    SUDDEN_BREAKING_OF_VEHICLE_AHEAD = "sudden_braking_of_vehicle_ahead"


selected_anomaly_types = [
    # AnomalyTypes.NORMALITY,
    AnomalyTypes.STATIC,
    # AnomalyTypes.SUDDEN_BREAKING_OF_VEHICLE_AHEAD,
]
"""
ANOMALY_TYPES to be used in the dataset
Uncomment every ANOMALY_TYPE that should be used in the dataset.
"""

categories = [
    "home",
    "animal",
    # 'nature',
    "special",
    # 'airplane',
    # 'falling'
]
"""
Static objects to be used in the dataset
Uncomment every Static object category that should be used in the dataset
"""

DISTANCE_INTERVAL = [65, 105]  # in Waypoints (the route length of the ego vehicle should be at least 105 waypoints)

# --- SUDDEN BREAKING OF VEHICLE AHEAD ---------------------------------------------------------------------------------
DISTANCE_INTERVAL_SUDDEN_BREAKING = [7, 12]  # in Waypoints (the route length of the ego vehicle should be at least 12 waypoints)

BREAKING_START = 140  # when the anomaly vehicle should start breaking- must be smaller than BREAKING_STOP and less than MAX_TICKCOUNT
BREAKING_STOP = 170  # when the abnormal vehicle continues to drive - must be greater than BREAKING_START and less than MAX_TICKCOUNT

DISTANCE_BETWEEN_CARS = 5  # Measure for the distance between the cars - should be in the interval [3,8], where 3 is very close and 8 is far away


# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- DATA PROCESSING --------------------------------------------------------------------------------------------
# ======================================================================================================================

CURRENT_SENSOR_SETS = [
    MONO_SENSOR_SETS,
    #STEREO_SENSOR_SETS,
    #STEREO_ONE_LIDAR_SENSOR_SETS,
    #MULTI_SENSOR_SETS,
    #SURROUND_SENSOR_SETS
]
"""" Set the sensor setups to be used in the dataset. Uncomment only the sensor setups that should be used in the 
dataset. (only one at a time)"""

# Assign format for each type of sensory data.
class DataFormat(Enum):
    """
    Enum class representing different data formats.
    """

    _settings_ = NoAlias  # This is needed to prevent the enum from being case-sensitive
    RGB_IMG = ".png"
    DEPTH_IMG = ".png"
    SEMANTIC_IMG = ".png"
    INSTANCE_IMG = ".png"
    PCD = ".npy"
    SEMANTIC_PCD = ".npy"
    VOXEL_GRID = ".npy"
    ACTION = ".csv"
    ANOMALY = ".csv"
    ROUTE_MAP = ".png"


IMAGE_HEIGHT = 512
"""Height of Image in px for all image outputs."""

IMAGE_WIDTH = 768
"""Width of Image in px for all image outputs."""

CAMERA_FOV = 90.0
"""Field of view for all image outputs."""

FOCAL = IMAGE_WIDTH / (2.0 * np.tan(CAMERA_FOV * np.pi / 360.0))

LIDAR_RANGE = 100.0
"""Maximum distance to measure/ray-cast in meters"""

LIDAR_UPPER_FOV = 15.0
"""Angle in degrees of the highest laser."""

LIDAR_LOWER_FOV = -25.0
"""Angle in degrees of the lowest laser."""

LIDAR_CHANNELS = 64
"""Number of lasers for the LIDAR"""

LIDAR_ROTATION_FREQUENCY = 200.0
"""highly advised to not change this parameter. Fixed Delta Time steps for synchronous mode needs to be adjusted 
as well"""

LIDAR_POINTS_PER_SEC = 1000000  # highly advised not to change this parameter. Point Cloud will
"""Points generated by all lasers per second."""

LIDAR_NOISE_STDDEV = 0.1

LIDAR_DROPOFF_RATE = 0.0
"""General proportion of points that are random dropped."""

LIDAR_DROPOFF_INTENSITY_LIMIT = 0.0
"""For the intensity based drop-off, the threshold intensity value above which no points are dropped."""

LIDAR_DROPOFF_ZERO_INTENSITY = 0.0
"""For the intensity based drop-off, the probability of each point with zero intensity being dropped."""
# --- SENSORS ----------------------------------------------------------------------------------------------------------

LIDAR_NAME = "sensor.lidar.ray_cast"
SEMANTIC_LIDAR_NAME = "sensor.lidar.ray_cast_semantic"
CAMERA_NAME = "sensor.camera.rgb"
DEPTH_NAME = "sensor.camera.depth"
SEMANTIC_CAMERA_NAME = "sensor.camera.semantic_segmentation"
INSTANCE_CAMERA_NAME = "sensor.camera.instance_segmentation"

SENSOR_TICK = "2.0"

VOXEL_SIZE = 0.5

# --- VOXEL CONFIG  --------------------------------------------------------------------------------------------------

CAMERA_POSITION_YC = [1.0, 0.0, 2.0]
LIDAR_POSITION_YC = [1.0, 0.0, 2.0]
FOV_YC = 90
VOXEL_RESOLUTION_YC = 0.5
VOXEL_SIZE_YC = [1000, 1000, 64]
BEV_OFFSET_FORWARD_YC = 0  # in px
BEV_RESOLUTION_YC = 0.2
OFFSET_Z_YC = 0  # in px

# --- ROUTEMAP  --------------------------------------------------------------------------------------------------

ROUTE_COLOR_WHITE = (255, 255, 255)
ROUTE_COLOR_BLACK = (0, 0, 0)

BEV_WORLD_OFFSET_MARGIN = 100
BEV_WIDTH = 192
BEV_PIXELS_PER_METER = float(5.0)
BEV_PIXELS_EV_TO_BOTTOM = 40

# --- COLORS -----------------------------------------------------------------------------------------------------------

Label = namedtuple(
    "Label",
    [
        "name",  # The identifier of this label, e.g. 'car', 'person', ... .
        # We use them to uniquely name a class
        "id",  # An integer ID that is associated with this label.
        # 'category'    , # The name of the category that this label belongs to
        # 'categoryId'  , # The ID of this category. Used to create ground truth images
        # on category level.
        "agent_mode",
        # actor is currently in agent mode and is more prone for unexpected behavior due to turned off autopilot.
        # It is therefore recommended to ignore these instances in evaluation
        "color",  # The color of this label
    ],
)

LABELS = [
    #       name                 id     agent_mode    color
    Label(
        "unlabeled",
        0,
        False,
        (0, 0, 0),
    ),
    Label(
        "road",
        1,
        False,
        (128, 64, 128),
    ),
    Label(
        "sidewalk",
        2,
        False,
        (244, 35, 232),
    ),
    Label(
        "building",
        3,
        False,
        (70, 70, 70),
    ),
    Label(
        "wall",
        4,
        False,
        (102, 102, 156),
    ),
    Label(
        "fence",
        5,
        False,
        (190, 153, 153),
    ),
    Label(
        "pole",
        6,
        False,
        (153, 153, 153),
    ),
    Label(
        "traffic light",
        7,
        False,
        (250, 170, 30),
    ),
    Label(
        "traffic sign ",
        8,
        False,
        (220, 220, 0),
    ),
    Label(
        "vegetation",
        9,
        False,
        (107, 142, 35),
    ),
    Label(
        "terrain",
        10,
        False,
        (152, 251, 152),
    ),
    Label(
        "sky",
        11,
        False,
        (70, 130, 180),
    ),
    Label(
        "pedestrian",
        12,
        False,
        (220, 20, 60),
    ),
    Label(
        "rider",
        13,
        False,
        (255, 0, 0),
    ),
    Label(
        "Car",
        14,
        False,
        (0, 0, 142),
    ),
    Label(
        "truck",
        15,
        False,
        (0, 0, 70),
    ),
    Label(
        "bus",
        16,
        False,
        (0, 60, 100),
    ),
    Label(
        "train",
        17,
        False,
        (0, 80, 100),
    ),
    Label(
        "motorcycle",
        18,
        False,
        (0, 0, 230),
    ),
    Label(
        "bicycle",
        19,
        False,
        (119, 11, 32),
    ),
    Label(
        "static",
        20,
        False,
        (110, 190, 160),
    ),
    Label(
        "dynamic",
        21,
        False,
        (170, 120, 50),
    ),
    Label(
        "other",
        22,
        False,
        (55, 90, 80),
    ),
    Label(
        "water",
        23,
        False,
        (45, 60, 150),
    ),
    Label(
        "road line",
        24,
        False,
        (157, 234, 50),
    ),
    Label(
        "ground",
        25,
        False,
        (81, 0, 81),
    ),
    Label(
        "bridge",
        26,
        False,
        (150, 100, 100),
    ),
    Label(
        "rail track",
        27,
        False,
        (230, 150, 140),
    ),
    Label(
        "guard rail",
        28,
        False,
        (180, 165, 180),
    ),
    # anomalies
    Label('home', 29, False, (245, 29, 0), ),
    Label('animal', 30, False, (245, 30, 0), ),
    Label('nature', 31, False, (245, 31, 0), ),
    Label('special', 32, False, (245, 32, 0), ),
    Label('falling', 34, False, (245, 34, 0), ),
    Label('airplane', 33, False, (245, 33, 0), ),
    Label(
        "anomaly",
        100,
        False,
        (245, 0, 0),
    ),
    # agents
    Label(
        "agent_pedestrian",
        112,
        True,
        (220, 20, 61),
    ),
    Label(
        "agent_car",
        114,
        True,
        (3, 0, 143),
    ),
    Label(
        "agent_truck",
        115,
        True,
        (0, 0, 71),
    ),
    Label(
        "agent_bus",
        116,
        True,
        (0, 60, 101),
    ),
    Label("agent_rider", 113, True, (255, 0, 1)),
    Label(
        "agent_motorcycle",
        118,
        True,
        (0, 0, 231),
    ),
    Label(
        "agent_bicycle",
        119,
        True,
        (119, 11, 33),
    ),
    # misc
    Label(
        "ego_vehicle",
        214,
        True,
        (0, 0, 1),
    ),
]

WHITE_COLOR = [255, 255, 255]

ANOMALY_COLOR = [245, 0, 0]

EGO_COLOR = [0, 0, 0]

# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- LOGGING ----------------------------------------------------------------------------------------------------
# ======================================================================================================================
# Configure logging
logging.basicConfig(
    filename="logfile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    filemode="a",
)

# Create a handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the desired log level for console output

# Define a format for console output (optional)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)

# Add the handler to the root logger instance
logging.getLogger().addHandler(console_handler)

# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- GENERAL DEFAULTS -------------------------------------------------------------------------------------------
# ======================================================================================================================

SENSOR_SETUP_FILE_NAME = 'sensor_setup.json'

# endregion
# ======================================================================================================================
