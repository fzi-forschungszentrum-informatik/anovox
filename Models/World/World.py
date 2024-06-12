"""This module contains the World class, which is responsible for creating the world in the simulation environment.It
defines various functions and classes to control and interact with the simulation environment. Some key
functionalities include spawning NPC vehicles and walkers, setting up the world, creating routes for vehicles,
handling traffic lights, and managing anomalies."""

import logging
import math
import random
import sys

import carla
import numpy as np

import Definitions
from Definitions import WeatherPresets
from Models.World.misc import compute_distance

sys.path.append("../")
from Models.World.global_route_planner import (
    GlobalRoutePlanner,
)
from Models.World.behavior_agent import (
    BehaviorAgent,
)

# ======================================================================================================================
# region -- GLOBAL VARIABLES -------------------------------------------------------------------------------------------
# ======================================================================================================================
TOLERANCE = 5
LARGE_TOLERANCE = 15


class WorldState:
    """
    A class representing the state of the world in a simulation.
    """

    def __init__(self):
        self.WORLD = None
        self.ANOMALY_OBJECTS = []

        self.NORMAL_VEHICLE_LIST = {}
        self.NORMAL_WALKER_LIST = []
        self.CONTROLLER_LIST = []

        self.SENSORS = []

        self.EGO_VEHICLE = None
        self.EGO_AGENT = None
        self.EGO_VEHICLE_ROUTE = None

        self.EGO_VEHICLE_COLLISIONS = []

        self.ANOMALY_AGENT = None
        self.ANOMALY_VEHICLE = None
        self.ANOMALY_VEHICLE_ROUTE = None

        self.ANOMALY_WAYPOINT = None

        self.anomalous_behavior_started = False

        self.client = carla.Client(Definitions.HOST, Definitions.PORT)
        self.client.set_timeout(Definitions.TIMEOUT)

        self.traffic_manager = None
        self.world_offset = None


WORLD_STATE = WorldState()


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- NPCS------------------------------------------------------------------------------------------------
# ======================================================================================================================
def spawn_npcs_to_world(self, npc_vehicle_amount, npc_walker_amount):
    """
    Spawns NPC vehicles and walkers to the world.
    """
    if npc_vehicle_amount > 0:
        spawn_npc_vehicle(self, npc_vehicle_amount)
    if npc_walker_amount > 0:
        spawn_npc_walker_to_world(self, npc_walker_amount)


# ======================================================================================================================
# region -- NPC_VEHICLE ------------------------------------------------------------------------------------------------
# ======================================================================================================================
def spawn_npc_vehicle(self, number_of_vehicles):
    """
    Spawns NPC (non-player character) vehicles in the game world.
    """

    # Get a list of vehicle blueprints
    vehicle_bp = self.WORLD.get_blueprint_library().filter("*vehicle*")

    # Get not occupied spawn points
    spawn_points = get_not_occupied_spawn_points(WORLD_STATE)
    number_of_spawn_points = len(spawn_points)

    # Select spawn points for the vehicles
    spawn_points = random.sample(
        spawn_points,
        min(
            number_of_vehicles,
            number_of_spawn_points,
        ),
    )

    if number_of_vehicles < number_of_spawn_points:
        random.shuffle(spawn_points)
        spawn_points = take_n_elements(spawn_points, number_of_vehicles)
    else:
        logging.warning(
            f"requested {number_of_vehicles} vehicles, but could only find {number_of_spawn_points} " f"spawn points")

    # Spawn vehicles at selected spawn points
    for spawn_point in spawn_points:
        vehicle_name = random.choice(vehicle_bp)

        actor = self.WORLD.try_spawn_actor(vehicle_name, spawn_point)
        if actor:
            # Add the spawned actor to the global list
            self.NORMAL_VEHICLE_LIST[actor] = None
            logging.debug(f"Spawned npc_vehicle: {actor}")

    logging.info(f"Spawned: {len(self.NORMAL_VEHICLE_LIST)}")


def start_movement_of_npcs(tm_port):
    set_normal_vehicles_on_autopilot(WORLD_STATE, tm_port)
    start_walking_walker(WORLD_STATE)


# --- GET_NOT_OCCUPIED_SPAWN_POINTS ------------------------------------------------------------------------------------
def get_not_occupied_spawn_points(self):
    """
    This method returns a list of spawn points that are not occupied by any vehicles. It takes no parameters.
    """

    # Get the map's spawn points
    spawn_points = self.WORLD.get_map().get_spawn_points()
    logging.debug(f" spawn points at beginning: {len(spawn_points)}")

    spawn_points = remove_occupied_spawn_points(WORLD_STATE, spawn_points)
    logging.debug(f"spawn points after removing occupied spawn points: {len(spawn_points)}")

    if self.ANOMALY_WAYPOINT is not None:
        spawn_points = remove_vehicles_on_the_road_of_ego_vehicle_to_anomaly(spawn_points)
        logging.debug(f"spawn points after removing available spawn points on the road to anomaly: {len(spawn_points)}")

    spawn_points = remove_spawn_points_in_radius_of_ego_vehicle(spawn_points)
    logging.debug(f"spawn points after removing spawnpoints in radius of ego_vehicle: {len(spawn_points)}")

    return spawn_points


def remove_occupied_spawn_points(self, spawn_points):
    """
    Removes occupied spawn points from a given list.
    """
    global TOLERANCE
    not_occupied_spawn_points = []
    vehicles = self.WORLD.get_actors().filter("*vehicle*")

    for spawn_point in spawn_points:
        occupied = False

        for vehicle in vehicles:
            vehicle_location = vehicle.get_location()
            if (
                    abs(vehicle_location.x - spawn_point.location.x) <= TOLERANCE
                    and abs(vehicle_location.y - spawn_point.location.y) <= TOLERANCE
            ):
                occupied = True
                break

        if not occupied:
            not_occupied_spawn_points.append(spawn_point)

    return not_occupied_spawn_points


def remove_vehicles_on_the_road_of_ego_vehicle_to_anomaly(
        spawn_points,
):
    """
    This method removes vehicles on the road of the ego vehicle to the anomaly.
    """
    global TOLERANCE
    route_ego_to_anomaly = get_route_from_ego_to_anomaly(WORLD_STATE)

    not_occupied_spawn_points = []

    for spawn_point in spawn_points:
        occupied = False
        for ego_vehicle_waypoint in route_ego_to_anomaly:
            ego_location = ego_vehicle_waypoint[0].transform.location
            if abs(ego_location.x - spawn_point.location.x) <= TOLERANCE and abs(
                    ego_location.y - spawn_point.location.y) <= TOLERANCE:
                occupied = True
                break
        if not occupied:
            not_occupied_spawn_points.append(spawn_point)

    return not_occupied_spawn_points


def remove_spawn_points_in_radius_of_ego_vehicle(
        spawn_points,
):
    """
    Remove spawn points within a certain radius of the ego vehicle.
    """
    global LARGE_TOLERANCE

    ego_location = get_ego_vehicle().get_location()

    not_occupied_spawn_points = []

    for spawn_point in spawn_points:
        spawn_location = spawn_point.location

        x_difference = abs(ego_location.x - spawn_location.x)
        y_difference = abs(ego_location.y - spawn_location.y)

        if x_difference <= LARGE_TOLERANCE and y_difference <= LARGE_TOLERANCE:
            continue
        else:
            not_occupied_spawn_points.append(spawn_point)

    return not_occupied_spawn_points


def get_route_from_ego_to_anomaly(self):
    """
    This method called "get_route_from_ego_to_anomaly" retrieves the route from the ego vehicle to the anomaly
    waypoint. It takes no parameters and returns a list representing the route *.
    """
    ego_vehicle_waypoints = self.EGO_VEHICLE_ROUTE
    anomaly_waypoint = self.ANOMALY_WAYPOINT
    route_ego_to_anomaly = []

    index = None

    for i, ego_vehicle_waypoint in enumerate(ego_vehicle_waypoints):
        ego_location = ego_vehicle_waypoint[0].transform.location
        if (
                abs(ego_location.x - anomaly_waypoint[0].transform.location.x) <= TOLERANCE
                and abs(ego_location.y - anomaly_waypoint[0].transform.location.y) <= TOLERANCE
        ):
            index = i  # Store the index of the current waypoint

    if index is not None:
        route_ego_to_anomaly = ego_vehicle_waypoints[: index + 1]

    return route_ego_to_anomaly


def set_normal_vehicles_on_autopilot(self, tm_port):
    """
    Sets normal vehicles on autopilot.
    """
    try:
        for vehicle in self.NORMAL_VEHICLE_LIST.keys():
            if vehicle:
                vehicle.set_autopilot(True, tm_port)

    except Exception as e:
        error_message = "Could not set on autopilot"
        logging.error(f"{error_message}: {e}", exc_info=True)


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- NPC_WALKER -------------------------------------------------------------------------------------------------
# ======================================================================================================================


def spawn_npc_walker_to_world(self, npc_walker_amount):
    """
    Spawn NPC walkers to the world.
    """

    walker_bp_library = self.WORLD.get_blueprint_library().filter("walker.pedestrian.*")

    # 1. take all the random location to spawn
    spawn_points = []
    for i in range(npc_walker_amount):
        spawn_point = carla.Transform()
        loc = self.WORLD.get_random_location_from_navigation()

        if loc is not None:
            spawn_point.location = loc
            spawn_points.append(spawn_point)

    # 2. we spawn the walker object
    for spawn_point in spawn_points:
        walker_bp = random.choice(walker_bp_library)

        # set as not invincible
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")

        actor = self.WORLD.try_spawn_actor(walker_bp, spawn_point)

        if actor:
            self.NORMAL_WALKER_LIST.append(actor)
            logging.debug(f"spawned npc_walker: {actor} ")

    logging.info(f"spawned: {len(self.NORMAL_WALKER_LIST)} npc_walkers")

    # 3. we spawn the walker controller
    walker_controller_bp = self.WORLD.get_blueprint_library().find("controller.ai.walker")
    for i in range(len(self.NORMAL_WALKER_LIST)):
        controller = self.WORLD.spawn_actor(
            walker_controller_bp,
            carla.Transform(),
            self.NORMAL_WALKER_LIST[i],
        )

        if controller:
            self.CONTROLLER_LIST.append(controller)
            logging.debug(f"spawned controller: {controller}")


def start_walking_walker(self):
    """
    Starts the walking behavior of all walkers in the controller list.
    """
    for i in range(len(self.CONTROLLER_LIST)):
        # start walker
        self.CONTROLLER_LIST[i].start()

        # set walk to random point
        self.CONTROLLER_LIST[i].go_to_location(
            self.WORLD.get_random_location_from_navigation())  # FIXME: Segmentation Fault from C++

    if len(self.CONTROLLER_LIST) > 0:
        logging.info(f"walkers now walking")


# endregion
# ======================================================================================================================

# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- FUNCTIONS --------------------------------------------------------------------------------------------------
# ======================================================================================================================


def write_scenario_id_to_file(scenario_id):
    """
    Writes the scenario id to a file. When the scenario have an error for instance
    there is no target waypoint for the NPC_Vehicle or pedestrian crashes to the ego vehicle
    """
    with open("scenario_id_fails.txt", "a") as file:
        file.write(str(scenario_id) + "\n")

    logging.info(f"scenario_id: {scenario_id} written to file")


def take_n_elements(lst, n):
    """
    Returns a new list containing the first n elements from the given list.
    """
    if n >= len(lst):
        return lst
    else:
        return lst[:n]


def activate_synchronous_mode_settings(self):
    """
    Activates the synchronous mode settings for the current world configuration.This method sets the synchronous mode
    settings for the world by updating the relevant properties of the current world settings.
    """
    synch_settings = self.WORLD.get_settings()
    synch_settings.synchronous_mode = True
    synch_settings.fixed_delta_seconds = Definitions.FIXED_DELTA_SECONDS
    synch_settings.substepping = Definitions.SUBSTEPPING
    synch_settings.max_substep_delta_time = Definitions.MAX_SUBSTEP_DELTA_TIME
    synch_settings.max_substeps = Definitions.MAX_SUBSTEP
    self.WORLD.apply_settings(synch_settings)


def deactivate_synchronous_mode_settings(self):
    """
    Deactivates the synchronous mode settings.
    """
    synch_settings = self.WORLD.get_settings()
    synch_settings.synchronous_mode = False
    synch_settings.substepping = False
    self.WORLD.apply_settings(synch_settings)


def get_world(self=WORLD_STATE):
    """
    Get the current state of the world.
    """
    if self.WORLD is None:
        raise Exception("World not created yet.")
    return self.WORLD


def change_world(self, map_world):
    """
    Change the current world to the specified map_world.
    """
    self.WORLD = self.client.load_world(f"{map_world}")
    self.WORLD.set_pedestrians_cross_factor(0.0)  # FIXME: Does not work


def get_map(self=WORLD_STATE):
    """
    Return the map of the current world state.
    """
    return self.WORLD.get_map()


def create_world(self=WORLD_STATE, synchronous_mode=True):
    """
    Creates the world in the simulation environment.
    """
    self.WORLD = self.client.get_world()

    if synchronous_mode:
        activate_synchronous_mode_settings(WORLD_STATE)

    return self.WORLD


def activate_traffic_manager(self=WORLD_STATE):
    """
    Activate Traffic Manager. This method activates the traffic manager and sets various parameters for controlling
    the behavior of the simulated traffic.
    """
    self.traffic_manager = self.client.get_trafficmanager(8000)
    self.traffic_manager.set_global_distance_to_leading_vehicle(2.5)
    self.traffic_manager.set_hybrid_physics_mode(True)
    self.traffic_manager.set_hybrid_physics_radius(200)

    self.traffic_manager.set_synchronous_mode(True)

    return self.traffic_manager


def set_weather(self, weather_preset):
    """
    Set the weather of the world based on the given weather preset.
    """
    weather_value = WeatherPresets[weather_preset].value
    self.WORLD.set_weather(getattr(carla.WeatherParameters, weather_value))
    logging.info(f"Set weather to {weather_preset}")


def generate_lidar(bp, lidar_name):
    """
    Generate LiDAR. Generates a LiDAR sensor object and sets its attributes based on the given parameters.
    """
    lidar_bp = bp.find(lidar_name)

    lidar_bp.set_attribute("range", str(Definitions.LIDAR_RANGE))
    lidar_bp.set_attribute(
        "upper_fov",
        str(Definitions.LIDAR_UPPER_FOV),
    )
    lidar_bp.set_attribute(
        "lower_fov",
        str(Definitions.LIDAR_LOWER_FOV),
    )
    lidar_bp.set_attribute(
        "channels",
        str(Definitions.LIDAR_CHANNELS),
    )
    lidar_bp.set_attribute(
        "rotation_frequency",
        str(Definitions.LIDAR_ROTATION_FREQUENCY),
    )
    lidar_bp.set_attribute(
        "points_per_second",
        str(Definitions.LIDAR_POINTS_PER_SEC),
    )
    # normal lidar:
    # no drop off, lidar point cloud will be used for voxel transformation and should be as detailed as possible
    if lidar_name == Definitions.LIDAR_NAME:
        lidar_bp.set_attribute(
            "noise_stddev",
            str(Definitions.LIDAR_NOISE_STDDEV),
        )
        lidar_bp.set_attribute(
            "dropoff_general_rate",
            str(Definitions.LIDAR_DROPOFF_RATE),
        )
        lidar_bp.set_attribute(
            "dropoff_intensity_limit",
            str(Definitions.LIDAR_DROPOFF_INTENSITY_LIMIT),
        )
        lidar_bp.set_attribute(
            "dropoff_zero_intensity",
            str(Definitions.LIDAR_DROPOFF_ZERO_INTENSITY),
        )
    # snapshot every 2 seconds
    return lidar_bp


def spawn_lidar_to_vehicle(self, vehicle, name, location, rotation):
    """
    Spawns a lidar sensor and attaches it to the specified vehicle.
    """
    lidar = generate_lidar(self.WORLD.get_blueprint_library(), name)
    x, y, z = location
    x_rotation, y_rotation, z_rotation = rotation
    lidar_initial = carla.Transform(
        carla.Location(x=x, y=y, z=z),
        carla.Rotation(pitch=y_rotation, yaw=z_rotation, roll=x_rotation)
    )
    logging.info(lidar_initial)
    lidar = self.WORLD.spawn_actor(lidar, lidar_initial, attach_to=vehicle)

    logging.debug("spawned_lidar_to_vehicle")

    self.SENSORS.append(lidar)

    return lidar


def spawn_anomaly_to_world(self, anomaly_name, spawn_point):
    """
    Spawn an anomaly to the world.
    """
    anomaly_bp = self.WORLD.get_blueprint_library().find(anomaly_name)

    try:
        anomaly = self.WORLD.spawn_actor(anomaly_bp, spawn_point)

        anomaly.set_simulate_physics(True)
        anomaly.set_enable_gravity(True)

        if anomaly:
            self.ANOMALY_OBJECTS.append(anomaly)

        logging.debug(f"spawned anomaly: {anomaly}")

        return anomaly

    except Exception as e:
        error_message = f"Could not spawn anomaly {anomaly_name}"
        logging.error(f"{error_message}\n{e}", exc_info=True)


def get_object_ids(obj_list):
    """
    Get Object IDs
    """
    obj_ids = []
    for obj in obj_list:
        if obj is not None:
            obj_ids.append(obj.id)
    return obj_ids  # Return a list of IDs, not the original obj_list


def destroy_everything(self=WORLD_STATE):
    """
    Destroy everything in the world. This method destroys all actors and clears the lists in the current world state.
    """
    logging.info("Trying to destroy everything ...")

    # Collect all actor IDs to be destroyed
    actor_ids = (
            get_object_ids(self.SENSORS)
            + [self.EGO_VEHICLE.id]
            + get_object_ids(self.ANOMALY_OBJECTS)
            + list(get_object_ids(self.NORMAL_VEHICLE_LIST.keys()))
            + get_object_ids(self.NORMAL_WALKER_LIST)
            + get_object_ids(self.CONTROLLER_LIST)
    )

    # Stop Controller
    for controller in self.WORLD.get_actors(actor_ids=get_object_ids(self.CONTROLLER_LIST)):
        if controller.is_alive:
            controller.stop()

    # Destroy each actor if it is alive
    for actor in self.WORLD.get_actors(actor_ids=actor_ids):
        if actor.is_alive:
            actor.destroy()

    # Clear the lists
    self.SENSORS.clear()
    self.ANOMALY_OBJECTS.clear()
    self.NORMAL_VEHICLE_LIST.clear()
    self.NORMAL_WALKER_LIST.clear()
    self.CONTROLLER_LIST.clear()

    self.EGO_VEHICLE = None
    self.EGO_AGENT = None
    self.EGO_VEHICLE_ROUTE = None

    self.EGO_VEHICLE_COLLISIONS.clear()

    self.ANOMALY_VEHICLE = None
    self.ANOMALY_AGENT = None
    self.ANOMALY_VEHICLE_ROUTE = None

    self.ANOMALY_WAYPOINT = None

    logging.info("Destroyed everything")


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- EGO_VEHICLE ------------------------------------------------------------------------------------------------
# ======================================================================================================================


def get_ego_vehicle(
        self=WORLD_STATE,
):
    """
    This method is used to find the ego vehicle within the world.
    """
    if self.EGO_VEHICLE:
        return self.EGO_VEHICLE

    raise Exception("Ego Vehicle does not exist.")


def spawn_coll_detec_sensor(self, vehicle):
    """
    Spawn a collision sensor attached to the ego vehicle.
    """
    coll_detec_bp = self.WORLD.get_blueprint_library().find("sensor.other.collision")
    coll_detec = self.WORLD.spawn_actor(
        coll_detec_bp,
        carla.Transform(),
        attach_to=vehicle,
    )

    coll_detec.listen(lambda event: self.EGO_VEHICLE_COLLISIONS.append(event))
    self.SENSORS.append(coll_detec)
    logging.info(f"spawned coll_sensor to world: {coll_detec}")

    return coll_detec


def spawn_ego_vehicle_to_world(
        self,
        vehicle_name=Definitions.EGO_VEHICLE,
        spawn_points_num=0,
):
    """
    Spawn an ego vehicle to the world.
    """
    vehicle_bp = self.WORLD.get_blueprint_library().find(vehicle_name)
    vehicle = None

    try:
        vehicle_bp.set_attribute("role_name", "hero")
        vehicle = self.WORLD.spawn_actor(vehicle_bp, spawn_points_num)

        logging.info(f"spawned ego_vehicle to world: {vehicle}")

        if vehicle:
            self.EGO_VEHICLE = vehicle

    except Exception as e:
        error_message = f"could not spawn vehicle {vehicle_name}"
        logging.error(f"{error_message}\n{e}", exc_info=True)

    return vehicle


def attach_camera_to_vehicle(self, vehicle, camera_name, location, rotation):
    """
    Attaches a camera to a vehicle.
    self:
    vehicule:
    camera_name:
    location: tuple (<float>, <float>, <float>)

    """
    bp = self.WORLD.get_blueprint_library()
    camera_bp = bp.find(camera_name)
    camera_bp.set_attribute("fov", str(Definitions.CAMERA_FOV))
    camera_bp.set_attribute(
        "image_size_x",
        str(Definitions.IMAGE_WIDTH),
    )
    camera_bp.set_attribute(
        "image_size_y",
        str(Definitions.IMAGE_HEIGHT),
    )
    camera_bp.set_attribute(
        "image_size_x",
        str(Definitions.IMAGE_WIDTH),
    )
    x, y, z = location
    x_rotation, y_rotation, z_rotation = rotation
    camera_init_trans = carla.Transform(
        carla.Location(x=x, y=y, z=z),
        carla.Rotation(pitch=y_rotation, yaw=z_rotation, roll=x_rotation)
    )  # Change this to move camera
    camera = self.WORLD.spawn_actor(
        camera_bp,
        camera_init_trans,
        attach_to=vehicle,
    )
    camera.image_size_x = Definitions.IMAGE_WIDTH
    camera.image_size_y = Definitions.IMAGE_HEIGHT
    self.SENSORS.append(camera)
    return camera


def move_spectator_behind_vehicle(self, vehicle):
    """
    Move the spectator camera behind the given vehicle.
    """
    spectator = self.WORLD.get_spectator()
    transformation = carla.Transform(
        vehicle.get_transform().transform(carla.Location(x=-6, z=2)),
        vehicle.get_transform().rotation,
    )
    spectator.set_transform(transformation)


# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- ANOMALY_ VEHICLE  ------------------------------------------------------------------------------------------------
# ======================================================================================================================
def get_anomaly_vehicle(
        self=WORLD_STATE,
):
    if self.ANOMALY_VEHICLE:
        return self.ANOMALY_VEHICLE

    raise Exception("Leader Vehicle does not exist.")


def spawn_anomaly_vehicle_to_world(
        self,
        vehicle_name,
        spawn_points_num=0,
):
    """
    Spawn an anomaly vehicle to the world.
    """
    vehicle_bp = self.WORLD.get_blueprint_library().find(vehicle_name)
    vehicle = None

    try:
        vehicle_bp.set_attribute("role_name", "anomaly")
        vehicle = self.WORLD.spawn_actor(vehicle_bp, spawn_points_num)

        logging.info(f"spawned anomaly_vehicle to world: {vehicle}")
        print("anomaly vehicle spawned", vehicle)
        if vehicle:
            self.ANOMALY_VEHICLE = vehicle
            self.ANOMALY_OBJECTS.append(vehicle)

    except Exception as e:
        error_message = f"could not spawn vehicle {vehicle_name}"
        logging.error(f"{error_message}\n{e}", exc_info=True)

    return vehicle


# ======================================================================================================================
# region -- NAVIGATION -------------------------------------------------------------------------------------------------
# ======================================================================================================================

# can be used for anomaly vehicle aswell
def debug_route(self, ego_vehicle_route):
    """
    Draws debug information for the ego vehicle route and the anomaly vehicle route.
    """
    world_debug = self.WORLD.debug

    for idx, w in enumerate(ego_vehicle_route):
        color = carla.Color(r=255, g=255, b=255)
        life_time = 25.0
        world_debug.draw_string(
            w[0].transform.location,
            "^",
            draw_shadow=False,
            color=color,
            life_time=life_time,
            persistent_lines=True,
        )


def create_shortest_path(self, start_transform, end_transform):
    """
    Create shortest path between two given transforms.
    """
    amap = self.WORLD.get_map()
    sampling_resolution = 1

    grp = GlobalRoutePlanner(amap, sampling_resolution)

    ego_vehicle_start_location = carla.Location(start_transform.location)
    ego_vehicle_end_location = carla.Location(end_transform.location)

    self.EGO_VEHICLE_ROUTE = grp.trace_route(
        ego_vehicle_start_location,
        ego_vehicle_end_location,
    )

    return self.EGO_VEHICLE_ROUTE


def create_shortest_path_anomaly(self, start_transform, end_transform):
    """
    Create shortest path between two given transforms.
    """
    amap = self.WORLD.get_map()
    sampling_resolution = 1

    grp = GlobalRoutePlanner(amap, sampling_resolution)

    anomaly_vehicle_start_location = carla.Location(start_transform.location)
    anomaly_vehicle_end_location = carla.Location(end_transform.location)

    self.ANOMALY_VEHICLE_ROUTE = grp.trace_route(
        anomaly_vehicle_start_location,
        anomaly_vehicle_end_location,
    )

    return self.ANOMALY_VEHICLE_ROUTE


def create_shortest_path_data(self, start_transform, end_transform):
    """
    Create the shortest path data between start and end transforms.
    """
    amap = self.WORLD.get_map()
    sampling_resolution = 1

    grp = GlobalRoutePlanner(amap, sampling_resolution)

    ego_vehicle_start_location = carla.Location(start_transform.location)
    ego_vehicle_end_location = carla.Location(end_transform.location)

    ego_route = grp.trace_route(
        ego_vehicle_start_location,
        ego_vehicle_end_location,
    )

    return ego_route


def create_behavior_agent_and_set_global_plan(self, ego_vehicle_route):
    """
    Creates a behavior agent for the ego vehicle and sets its global plan.
    """
    self.EGO_AGENT = BehaviorAgent(get_ego_vehicle(), behavior="normal")
    self.EGO_AGENT.set_global_plan(
        plan=ego_vehicle_route,
        stop_waypoint_creation=True,
        clean_queue=True,
    )
    return self.EGO_AGENT


def create_anomaly_behaviour_agent_and_set_global_plan(self, anomaly_vehicle_route):
    """
    Creates a behavior agent for the anomaly vehicle and sets its global plan.
    """
    self.ANOMALY_AGENT = BehaviorAgent(get_anomaly_vehicle(), behavior="aggressive")
    self.ANOMALY_AGENT.set_global_plan(
        plan=anomaly_vehicle_route,
        stop_waypoint_creation=True,
        clean_queue=True,
    )
    return self.ANOMALY_AGENT


def ego_vehicle_apply_control_run_step(self, mode):
    """
    Apply a control to the ego vehicle and run a simulation step.
    """
    if mode != 'SUDDEN_BREAKING_OF_VEHICLE_AHEAD':
        ego_vehicle_control = self.EGO_AGENT.run_step(False)
        if ego_vehicle_control.brake == 1.0:
            logging.error(f"Ego vehicle performed a sudden braking. Ignore scenario")
            raise ValueError('Ego vehicle sudden breaking. Ignore scenario')
        get_ego_vehicle().apply_control(ego_vehicle_control)

    else:
        distance = compute_distance(get_anomaly_vehicle().get_location(), get_ego_vehicle().get_location())
        distance = distance - Definitions.DISTANCE_BETWEEN_CARS
        control = self.EGO_AGENT.car_following_manager(get_anomaly_vehicle(), distance)
        get_ego_vehicle().apply_control(control)


def anomaly_vehicle_apply_control_run_step(self):
    """
    Apply a control to the ego vehicle and run a simulation step.
    """
    control = self.ANOMALY_AGENT.run_step(False)
    get_anomaly_vehicle().apply_control(control)


def anomaly_vehicle_apply_control_emergency_break():
    get_anomaly_vehicle().apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))


def compute_world_offset(self):
    """Calculates the world offset as the minimum x and y map waypoint-coords minus a margin for BEV view
    Adapted from https://github.com/zhejz/carla-roach/ CC-BY-NC 4.0 license.
    """

    waypoints = self.WORLD.get_map().generate_waypoints(2)  # list of carla.Waypoints
    min_x = min(waypoints,
                key=lambda x: x.transform.location.x).transform.location.x - Definitions.BEV_WORLD_OFFSET_MARGIN
    min_y = min(waypoints,
                key=lambda x: x.transform.location.y).transform.location.y - Definitions.BEV_WORLD_OFFSET_MARGIN
    self.world_offset = np.array([min_x, min_y], dtype=np.float32)
    return True


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- NPC_VEHICLE_AGENT ------------------------------------------------------------------------------------------
# ======================================================================================================================
def create_behavior_agent_and_set_global_plan_normal_vehicle(self, normal_vehicle_route, normal_vehicle):
    """
    This method creates a behavior agent for a normal vehicle and sets its global plan.
    """
    self.NORMAL_VEHICLE_LIST[normal_vehicle] = BehaviorAgent(normal_vehicle, behavior="normal")
    self.NORMAL_VEHICLE_LIST[normal_vehicle].set_global_plan(
        plan=normal_vehicle_route,
        stop_waypoint_creation=False,
        clean_queue=True,
    )

    return self.NORMAL_VEHICLE_LIST[normal_vehicle]


def create_shortest_path_normal_vehicle(self, start_transform, end_transform):
    """
    Create shortest path for a normal vehicle.
    """
    amap = self.WORLD.get_map()
    sampling_resolution = 1
    grp = GlobalRoutePlanner(amap, sampling_resolution)
    normal_vehicle_start_location = carla.Location(start_transform.location)
    normal_vehicle_end_location = carla.Location(end_transform.location)
    normal_vehicle_route = grp.trace_route(
        normal_vehicle_start_location,
        normal_vehicle_end_location,
    )
    return normal_vehicle_route


def normal_vehicle_agent_apply_control_run_step(self):
    """
    Apply a control to the npcs vehicles and run a simulation step.
    """
    for normal_vehicle, normal_vehicle_controller in self.NORMAL_VEHICLE_LIST.items():
        if normal_vehicle_controller:
            result = normal_vehicle_controller.run_step(False)
            if result:
                normal_vehicle.apply_control(result)


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- TRAFFIC LIGHTS ---------------------------------------------------------------------------------------------
# ======================================================================================================================


def get_trafficlight_trigger_location(
        traffic_light,
):
    """
    The `get_trafficlight_trigger_location` method takes a `traffic_light` object as a parameter and returns the location of the trigger point of the traffic light.
    """

    def rotate_point(point_pos, angle):
        """
        rotate a given point by a given angle
        """
        x_ = math.cos(math.radians(angle)) * point_pos.x - math.sin(math.radians(angle)) * point_pos.y
        y_ = math.sin(math.radians(angle)) * point_pos.x - math.cos(math.radians(angle)) * point_pos.y

        return carla.Vector3D(x_, y_, point_pos.z)

    base_transform = traffic_light.get_transform()
    base_rot = base_transform.rotation.yaw
    area_loc = base_transform.transform(traffic_light.trigger_volume.location)
    area_ext = traffic_light.trigger_volume.extent

    point = rotate_point(carla.Vector3D(0, 0, area_ext.z), base_rot)
    point_location = area_loc + carla.Location(x=point.x, y=point.y)

    return carla.Location(
        point_location.x,
        point_location.y,
        point_location.z,
    )


def get_next_traffic_light(mode):
    """
    This method, `get_next_traffic_light()`, returns the most relevant traffic light for the ego vehicle.
    """
    if mode == "ego":
        vehicle = get_ego_vehicle()
    if mode == "anomaly":
        vehicle = get_anomaly_vehicle()

    vehicle_location = vehicle.get_transform().location

    waypoint = get_map().get_waypoint(vehicle_location)
    # Create list of all waypoints until next intersection
    list_of_waypoints = []
    while waypoint and not waypoint.is_intersection:
        list_of_waypoints.append(waypoint)
        waypoint = waypoint.next(5.0)[0]

    # If the list is empty, the actor is in an intersection
    if not list_of_waypoints:
        return None

    relevant_traffic_light = None
    distance_to_relevant_traffic_light = float("inf")

    for traffic_light in get_world().get_actors().filter("traffic.*"):
        if hasattr(traffic_light, "trigger_volume"):
            transformed_tv = get_trafficlight_trigger_location(traffic_light)
            # transformed_tv = traffic_light.transform(traffic_light.trigger_volume.location)
            distance = carla.Location(transformed_tv).distance(list_of_waypoints[-1].transform.location)

            if distance < distance_to_relevant_traffic_light:
                relevant_traffic_light = traffic_light
                distance_to_relevant_traffic_light = distance

    return relevant_traffic_light


def set_green_relevant_traffic_light(mode="ego"):
    """
    Set the relevant traffic light to green and other traffic lights in the same group to red.
    """
    relevant_traffic_light = get_next_traffic_light(mode)

    if relevant_traffic_light and relevant_traffic_light.type_id == "traffic.traffic_light":
        group_of_traffic_lights_list = relevant_traffic_light.get_group_traffic_lights()
        for other_traffic_light in group_of_traffic_lights_list:
            if other_traffic_light.id != relevant_traffic_light.id:
                other_traffic_light.set_state(carla.TrafficLightState.Red)
                other_traffic_light.set_red_time(10)
                other_traffic_light.freeze(True)

        relevant_traffic_light.set_state(carla.TrafficLightState.Green)
        relevant_traffic_light.set_green_time(10)
        relevant_traffic_light.freeze(True)
    return


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- ANOMALY BEHAVIOR ------------------------------------------------------------------------------------------
# ======================================================================================================================
def make_anomaly_spawnpoint(self, waypoint_number):
    """
    Sets a random waypoint from ego_vehicle_route as the ANOMALY_WAYPOINT.
    """
    self.ANOMALY_WAYPOINT = self.EGO_VEHICLE_ROUTE[waypoint_number]
    return self.ANOMALY_WAYPOINT

# endregion
# ======================================================================================================================
