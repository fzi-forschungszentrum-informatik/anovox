import logging
import random

import carla

from Models.World import World
from .Util import compare_locations, draw_waypoint


# ======================================================================================================================
# region -- 1. PREPARE THE JUNCTION FOR NAVIGATION ---------------------------------------------------------------------
# ======================================================================================================================


def junction_prep(ego_vehicle_route, distance_to_waypoint_to_anomaly):
    """
    Prepares information related to the junction and critical waypoints between the ego vehicle
    and the anomaly spawn point for navigation.
    """

    # Extracts a list of waypoints from the anomaly to the start of the lane separated by a certain distance (here 1).
    route_from_anomaly_to_critical_junction = extract_route_from_anomaly_to_junction(ego_vehicle_route,
                                                                                     distance_to_waypoint_to_anomaly)

    # Gets the road IDs from the waypoints
    waypoint_road_ids = [waypoint[0].road_id for waypoint in route_from_anomaly_to_critical_junction]

    # Creates a new list with the relevant road IDs
    relevant_waypoint_road_ids_list = list(set(waypoint_road_ids))
    logging.info(f"relevant_waypoint_road_ids_list: {relevant_waypoint_road_ids_list}")

    # Creates a route from ego_vehicle to anomaly spawn point
    route_to_anomaly = ego_vehicle_route[:distance_to_waypoint_to_anomaly]
    logging.info(f"route from ego_vehicle to anomaly configured")

    # Searches for the critical junction from ego_vehicle to anomaly spawn point (the last junction before the anomaly spawn point)
    critical_junction = get_critical_junction(route_to_anomaly)
    critical_paths = None

    if critical_junction:
        critical_waypoints = get_critical_waypoints(critical_junction)

        # Groups the critical waypoints by their starting waypoint (returns a list of tuples, but as waypoints)
        critical_paths = group_by_start_waypoint(critical_waypoints)

        # Debug drawing the critical waypoints
        for index, (start, ends) in enumerate(critical_paths):
            start_color = carla.Color(r=255, g=0, b=0)  # Yellow for start waypoints
            end_color = carla.Color(r=0, g=0, b=255)  # Green for end waypoints

            draw_waypoint(World.WORLD_STATE.WORLD, start, start_color, mark=f"S{index}")

            for end in ends:
                draw_waypoint(World.WORLD_STATE.WORLD, end, end_color, mark=f"E{index}")

    return (
        critical_paths,
        relevant_waypoint_road_ids_list,
    )


# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- 2. HANDLE THE NORMAL VEHICLES AT THE CRITICAL WAYPOINTS ----------------------------------------------------
# ======================================================================================================================


def junction_case(
        relevant_waypoint_road_ids_list,
        critical_paths,
        scenario_id,
):
    """
    This method is responsible for handling vehicles at critical waypoints in a junction scenario.
    """
    agent_mode_vehicles = []

    # WE CHECK IF THERE ARE VEHICLES AT THE START OF THE CRITICAL PATHS
    if critical_paths:
        for key in World.WORLD_STATE.NORMAL_VEHICLE_LIST:
            for critical_path in critical_paths:
                if compare_locations(key.get_location(), critical_path[0].transform.location):
                    if World.WORLD_STATE.NORMAL_VEHICLE_LIST[key] is None:
                        logging.info(
                            f"NPC_VEHICLE is a critical_start_waypoint: {key} in Road_id {critical_path[0].road_id}")

                        # STOP AUTOPILOT
                        key.set_autopilot(False)

                        # GIVE ME THE TUPLE WHERE THE START WAYPOINT IS THE SAME AS THE KEY LOCATION
                        critical_path_tuple = critical_path  # HERE ARE THE TARGET WAYPOINTS WHERE THE NPC CAN DRIVE TO
                        critical_path_target = critical_path[
                            1]  # HERE ARE THE TARGET WAYPOINTS WHERE THE NPC CAN DRIVE TO

                        # WE WANT TO REMOVE THE TARGET WAYPOINTS THAT ARE IN THE DIRECTION OF THE ANOMALY
                        for target_waypoint in critical_path_target:
                            target_waypoint_next_list = target_waypoint.next(distance=10)

                            # FIND THE MOST COMMON TARGET ROAD ID IN THE LIST OF TARGET WAYPOINTS
                            target_waypoint_road_ids = [target_waypoint_next.road_id for target_waypoint_next in
                                                        target_waypoint_next_list]
                            most_common_target_road_id = max(set(target_waypoint_road_ids),
                                                             key=target_waypoint_road_ids.count)

                            # IF THE LIST OF ANOMALY_ROAD_ID HAVE A ROAD_ID WHICH IS EQUALS THE MOST_COMMON_TARGET_ROAD_ID THE REMOVE THIS TARGET
                            # WAYPOINT FROM THE LIST
                            if most_common_target_road_id in relevant_waypoint_road_ids_list:
                                critical_path_target.remove(target_waypoint)

                        # NOW GIVE THE NPC A RANDOM TARGET WAYPOINT FROM THE LIST. IF THE TARGET WAYPOINT IS EMPTY THEN RAISE AN ERROR AND CANCEL
                        # THIS SCENARIO
                        if len(critical_path_target) == 0:
                            raise ValueError("No target waypoints available for NPC vehicle")
                            # World.write_scenario_id_to_file(scenario_id)
                            # logging.error("No target waypoints available for NPC vehicle")
                            # return None

                        rerouted_target_waypoint = random.choice(critical_path_target)

                        # DEBUG DRAWING THE REROUTED TARGET WAYPOINT
                        draw_waypoint(
                            World.WORLD_STATE.WORLD, rerouted_target_waypoint, color=carla.Color(r=255, g=254, b=32),
                            mark=str(key)
                        )  # Yellow

                        # CREATE A ROUTE FROM THE NPC TO THE REROUTED TARGET WAYPOINT
                        normal_vehicle_route = World.create_shortest_path_normal_vehicle(
                            World.WORLD_STATE, critical_path_tuple[0].transform, rerouted_target_waypoint.transform
                        )

                        World.create_behavior_agent_and_set_global_plan_normal_vehicle(
                            World.WORLD_STATE,
                            normal_vehicle_route,
                            key,
                        )

                        agent_mode_vehicles.append(key)

    return agent_mode_vehicles


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- FUNCTIONS --------------------------------------------------------------------------------------------------
# ======================================================================================================================
def group_by_start_waypoint(critical_waypoints):
    """
    Groups critical waypoints by their starting locations.

    Parameters:
    - critical_waypoints (list): A list of tuples representing critical waypoints,
      where each tuple contains a start location and a target location.

    Returns:
    - list: A list of tuples representing grouped critical waypoints,
      where each tuple contains a start location and a list of corresponding target locations.
    """
    # Initialize an empty dictionary to store grouped critical waypoints
    grouped_list = {}

    # Iterate through each waypoint tuple in the input list
    for start, target in critical_waypoints:
        found_match = False
        # Check if the start location matches with an existing groupe
        for existing_start, end_list in grouped_list.items():
            if compare_locations(start.transform.location, existing_start.transform.location):
                end_list.append(target)
                found_match = True
                break

        # If no match is found, create a new group
        if not found_match:
            grouped_list[start] = [target]

    # Convert the grouped dictionary into a list of tuples
    result_list = [(start, end_list) for start, end_list in grouped_list.items()]

    return result_list


def get_critical_junction(route_to_anomaly):
    """
    Finds the critical junction in the given route to the anomaly.
    route_to_anomaly is a list of waypoints from ego_vehicle to anomaly spawnpoint
    We are trying to find the last junction before the anomaly spawnpoint. So we are searching backwards the next junction.
    """
    for waypoint in reversed(route_to_anomaly):
        if waypoint[0].get_junction():
            logging.info(f"found junction: {waypoint[0].get_junction()}")
            return waypoint[0].get_junction()
    return None


def extract_route_from_anomaly_to_junction(ego_vehicle_route, distance_to_anomaly):
    # Extract a sub-route from the ego_vehicle_route up to (distance_to_anomaly + 5)
    sub_route_to_anomaly = ego_vehicle_route[: distance_to_anomaly + 5]

    # Reverse the sub-route to anomaly for easier traversal
    reversed_sub_route_to_anomaly = sub_route_to_anomaly[::-1]

    # Find the index of the waypoint with a junction
    index_waypoint_with_junction = None
    for index, waypoint_info in enumerate(reversed_sub_route_to_anomaly[4:], start=4):
        if waypoint_info[0].get_junction():
            index_waypoint_with_junction = index + 5  # Adding 5 for safety
            break

    # Extract the route from the anomaly to the relevant junction
    route_from_anomaly_to_junction = reversed_sub_route_to_anomaly[:index_waypoint_with_junction]

    # Visualize the waypoints on the world map
    for waypoint_info in route_from_anomaly_to_junction:
        draw_waypoint(World.WORLD_STATE.WORLD, waypoint_info[0], color=carla.Color(r=0, g=0, b=255), mark="W")

    return route_from_anomaly_to_junction


def get_critical_waypoints(critical_junction):
    """
    Retrieves critical waypoints for a given junction.So waypoint[0] is the
    leading and waypoint[1] the outgoing waypoint. that means we have in a junction with 16 tuples (=16 lanes) we have 8
    leading and 8 outgoing waypoints.

    return a list of tuples. Start is the leading and End is the outgoing waypoints.
    """
    if critical_junction:
        critical_waypoints = critical_junction.get_waypoints(carla.LaneType.Driving)
        logging.info(f"found critical_waypoints: {critical_waypoints}")

        return critical_waypoints
    else:
        return None

# endregion
# ======================================================================================================================
