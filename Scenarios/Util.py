import json
import math
import random
import sys

import carla
from colorama import Fore, Style

import Definitions
from Models.Models import ActionData
from Models.World import World


# ======================================================================================================================
# region -- SCENARIO_MAIN ----------------------------------------------------------------------------------------------
# ======================================================================================================================
def get_vehicle_action(scenario_id, frame_id, is_anomaly_vehicle=False):
    if is_anomaly_vehicle:
        ego_vehicle = World.get_anomaly_vehicle()
    else:
        ego_vehicle = World.get_ego_vehicle()

    v = ego_vehicle.get_velocity()
    veh_p_c, veh_p = (
        ego_vehicle.get_physics_control(),
        ego_vehicle.get_control(),
    )
    front_left_wheel = veh_p_c.wheels[0]
    front_right_wheel = veh_p_c.wheels[1]
    back_left_wheel = veh_p_c.wheels[2]
    back_right_wheel = veh_p_c.wheels[3]

    sensor_list = World.WORLD_STATE.SENSORS
    camera = None
    lidar = None

    for sensor in sensor_list:
        if sensor.type_id == Definitions.CAMERA_NAME:
            camera = sensor
        elif sensor.type_id == Definitions.LIDAR_NAME:
            lidar = sensor

    camera_trans = camera.get_transform()
    lidar_trans = lidar.get_transform()
    try:
        action_dict = {
            "frame_id": frame_id,
            "scenario_id": scenario_id,
            "vehicle_id": ego_vehicle.id,
            "vehicle_type_id": ego_vehicle.type_id,
            "speed": 3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2),
            "throttle": veh_p.throttle,
            "steer": veh_p.steer,
            "brake": veh_p.brake,
            "hand_brake": veh_p.hand_brake,
            "reverse": veh_p.reverse,
            "gear": veh_p.gear,
            "max_rpm": veh_p_c.max_rpm,
            "final_ratio": veh_p_c.final_ratio,
            "mass": veh_p_c.mass,
            "center_of_mass": (
                veh_p_c.center_of_mass.x,
                veh_p_c.center_of_mass.y,
                veh_p_c.center_of_mass.z,
            ),
            "steering_curve": (
                f"{veh_p_c.steering_curve[0].x},{veh_p_c.steering_curve[0].y})",
                f"({veh_p_c.steering_curve[1].x}/{veh_p_c.steering_curve[1].y}",
            ),
            "FR_wheel max steer angle": front_right_wheel.max_steer_angle,
            "FL_wheel max steer angle": front_left_wheel.max_steer_angle,
            "BR_wheel max steer angle": back_right_wheel.max_steer_angle,
            "BL_wheel max steer angle": back_left_wheel.max_steer_angle,
            "FR_wheel tire friction": front_right_wheel.tire_friction,
            "FL_wheel tire friction": front_left_wheel.tire_friction,
            "BR_wheel tire friction": back_right_wheel.tire_friction,
            "BL_wheel tire friction": back_left_wheel.tire_friction,
            "camera transformation matrix": camera_trans.get_matrix(),
            "camera inverse transformation matrix": camera_trans.get_inverse_matrix(),
            "lidar transformation matrix": lidar_trans.get_matrix(),
            "lidar inverse transformation matrix": lidar_trans.get_inverse_matrix(),
        }
    except Exception as e:
        raise Exception(
            "Could not get values for Action from Vehicle\n",
            e,
        )

    return action_dict


def get_anomaly_dict(scenario_id, frame_id):
    anomaly_dict = None
    if len(World.WORLD_STATE.ANOMALY_OBJECTS) > 0:
        anomaly = World.WORLD_STATE.ANOMALY_OBJECTS[0]
        anom_loc = anomaly.get_location()
        anom_velo = anomaly.get_velocity()
        anom_accel = anomaly.get_acceleration()
        try:
            anomaly_dict = {
                "frame_id": frame_id,
                "scenario_id": scenario_id,
                "anomaly_id": anomaly.id,
                "anomaly_type_id": anomaly.type_id,
                "anomaly_is_alive": anomaly.is_alive,
                "semantic_tags": anomaly.semantic_tags,
                "location": (
                    anom_loc.x,
                    anom_loc.y,
                    anom_loc.z,
                ),
                "velocity": (
                    anom_velo.x,
                    anom_velo.y,
                    anom_velo.z,
                ),
                "acceleration": (
                    anom_accel.x,
                    anom_accel.y,
                    anom_accel.z,
                ),
            }
            anomaly_dict.update(anomaly.attributes)
        except Exception as e:
            raise Exception(
                "Could not get values for Action from Vehicle\n",
                e,
            )

    return anomaly_dict


def get_action_state_data(scenario_id, frame_id, scenario_type):
    action_data_dict = get_vehicle_action(scenario_id, frame_id)
    if scenario_type == "SUDDEN_BREAKING_OF_VEHICLE_AHEAD":
        anomaly_dict = get_vehicle_action(scenario_id, frame_id, True)
    else:
        anomaly_dict = get_anomaly_dict(scenario_id, frame_id)
    action_data_object = ActionData(
        scenario_id,
        frame_id,
        action_data_dict,
        anomaly_dict,
    )

    return action_data_object


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- PROGRESS ---------------------------------------------------------------------------------------------------
# ======================================================================================================================
def update_progress(tick_count, max_tickcount, label):
    frame_id = World.get_world().tick()
    tick_count += 1
    print_progress_bar(tick_count, max_tickcount, label)
    return frame_id, tick_count


def print_progress_bar(index, total, label):
    n_bar = 30  # Modern progress display with 30 blocks
    progress = index / total
    num_blocks = int(n_bar * progress)
    num_spaces = n_bar - num_blocks
    progress_percent = int(progress * 100)

    if progress_percent == 100:
        # At 100%, change the color to Green
        color = Fore.GREEN
    elif progress_percent >= 75:
        # At 75% and above, change the color to Yellow
        color = Fore.LIGHTYELLOW_EX
    elif progress_percent >= 30:
        # At 50% and above, change the color to Orange
        color = Fore.LIGHTYELLOW_EX
    else:
        # For everything else, stay at Red
        color = Fore.RED

    # Progress display with the corresponding color
    progress_bar = f"{label}: [{color}{'█' * num_blocks}{' ' * num_spaces}{Style.RESET_ALL}] {progress_percent}%"

    # Improved formatting for brackets and scenario progress
    sys.stdout.write("\r" + progress_bar.ljust(60) + f"({index}/{total})")
    sys.stdout.flush()


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- SCENARIO-CONFIG --------------------------------------------------------------------------------------------
# ======================================================================================================================
def get_scenario_config(file_path):
    """Generates and returns file with a preset set of scenarios. For more information about the scenario generation
    see ScenarioDefinitionGenerator."""

    # Open generated scenarios
    with open(file_path, "r") as json_file:
        scenario_definitions = json.load(json_file)
        json_file.close()

    return scenario_definitions


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- FUNCTIONS --------------------------------------------------------------------------------------------------
# ======================================================================================================================
def draw_waypoint(world, waypoint, color, lifetime=30.0, persistent_lines=True, mark="O"):
    world.debug.draw_string(
        waypoint.transform.location,
        mark,
        draw_shadow=False,
        color=color,
        life_time=lifetime,
        persistent_lines=persistent_lines,
    )


def compare_locations(location_a, location_b, tolerance=0.5):
    return abs(location_a.x - location_b.x) <= tolerance and abs(location_a.y - location_b.y) <= tolerance


def destructure_dict(dictionary, *args):
    return (dictionary[arg] for arg in args)


def get_transform(spawnpoint_json):
    """This Method converts the scenario_definition values into carla computable objects."""

    spawnpoint_transform = carla.Transform(
        carla.Location(
            spawnpoint_json["location"]["x"],
            spawnpoint_json["location"]["y"],
            spawnpoint_json["location"]["z"],
        ),
        carla.Rotation(
            spawnpoint_json["rotation"]["pitch"],
            spawnpoint_json["rotation"]["yaw"],
            spawnpoint_json["rotation"]["roll"],
        ),
    )

    return spawnpoint_transform


def count_different_lanes(ego_vehicle_route, waypoint_ego_vehicle_start):
    """
    This function counts the number of waypoints in the first 5 waypoints of the ego vehicle's route
    that are in a different lane than the starting waypoint of the ego vehicle.
    """
    counter = 0
    for j, waypoint in enumerate(ego_vehicle_route):
        if j >= 5:
            break
        if waypoint[0].lane_id != waypoint_ego_vehicle_start.lane_id:
            counter += 1
    return counter


def get_valid_route(list_of_spawnpoints):
    """
    This function generates a valid route for the ego vehicle in a simulation environment.

    It randomly selects start and end spawnpoints from a list of spawnpoints, and generates the shortest path between them. It then checks if the
    first 5 waypoints of the route are in the same lane as the starting waypoint of the ego vehicle. If the number of waypoints in a different lane
    is less than or equal to 2, and the length of the route is greater than or equal to a predefined distance interval, and the road ID of the
    starting waypoint is the same as the road ID of the first waypoint in the route, the function returns the start and end spawnpoints, the route,
    and the starting waypoint. Otherwise, it continues to generate routes until it finds a valid one.
    """
    while True:
        ego_start_spawnpoint = random.choice(list_of_spawnpoints)
        ego_end_spawnpoint = random.choice(list_of_spawnpoints)

        ego_vehicle_route = World.create_shortest_path_data(
            World.WORLD_STATE,
            ego_start_spawnpoint,
            ego_end_spawnpoint,
        )

        waypoint_ego_vehicle_start = World.get_map().get_waypoint(carla.Location(ego_start_spawnpoint.location))
        counter = count_different_lanes(ego_vehicle_route, waypoint_ego_vehicle_start)

        if (
                counter <= 2
                and len(ego_vehicle_route) >= Definitions.DISTANCE_INTERVAL[1]
                and waypoint_ego_vehicle_start.road_id == ego_vehicle_route[0][0].road_id
        ):
            return ego_start_spawnpoint, ego_end_spawnpoint, ego_vehicle_route

# endregion
# ======================================================================================================================
