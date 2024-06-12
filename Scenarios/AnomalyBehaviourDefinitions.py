import logging

import Definitions
from Definitions import AnomalyTypes
from Models.World import World
from Scenarios import Util
from .Static import junction_prep, junction_case
from .Util import destructure_dict


# ======================================================================================================================
# region -- NORMAL SCENARIO BEHAVIOR ----------------------------------------------------------------------------------
# ======================================================================================================================


def normal_scenario_behavior(scenario_config,
                             static_dict,
                             sensors,
                             image_queues,
                             tick_count,
                             max_tickcount,
                             frame_id, ):
    # region -- INITIALIZATION -----------------------------------------------------------------------------------------
    anomaly_config = scenario_config["anomaly_config"]

    critical_paths = static_dict["critical_paths"]
    relevant_waypoint_road_ids_list = static_dict["relevant_waypoint_road_ids_list"]

    anomaly_bp_name = anomaly_config["anomaly_bp_name"]
    distance_to_waypoint = anomaly_config["distance_to_waypoint"]

    # endregion --------------------------------------------------------------------------------------------------------

    # region -- BEHAVIOR ----------------------------------------------------------------------------------------------
    if tick_count == 1:
        anomaly_spawnpoint = World.make_anomaly_spawnpoint(
            World.WORLD_STATE,
            distance_to_waypoint,
        )
        transformed_spawnpoint = anomaly_spawnpoint[0].transform
        transformed_spawnpoint.location.z += 2

        anomaly_actor = None
    else:
        # FIXME: Leftover from static scenario behavior
        behavior_update = {}
        return behavior_update

    # endregion --------------------------------------------------------------------------------------------------------


# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- STATIC SCENARIO BEHAVIOR ----------------------------------------------------------------------------------
# ======================================================================================================================


def static_scenario_behavior(
        scenario_config,
        static_dict,
        sensors,
        image_queues,
        tick_count,
        max_tickcount,
        frame_id,
):
    # region -- INITIALIZATION -----------------------------------------------------------------------------------------
    scenario_id = scenario_config["scenario_id"]
    anomaly_config = scenario_config["anomaly_config"]

    critical_paths = static_dict["critical_paths"]
    relevant_waypoint_road_ids_list = static_dict["relevant_waypoint_road_ids_list"]

    anomaly_bp_name = anomaly_config["anomaly_bp_name"]
    distance_to_waypoint = anomaly_config["distance_to_waypoint"]

    # endregion --------------------------------------------------------------------------------------------------------

    # region -- BEHAVIOR ----------------------------------------------------------------------------------------------
    if tick_count == 1:
        anomaly_spawnpoint = World.make_anomaly_spawnpoint(
            World.WORLD_STATE,
            distance_to_waypoint,
        )
        transformed_spawnpoint = anomaly_spawnpoint[0].transform
        transformed_spawnpoint.location.z += 2

        anomaly_actor = None

        # SPAWNING ANOMALY
        try:
            anomaly_actor = World.spawn_anomaly_to_world(
                World.WORLD_STATE,
                anomaly_name=anomaly_bp_name,
                spawn_point=transformed_spawnpoint,
            )

            logging.info(f"spawned anomaly: {anomaly_actor}\n")
        except Exception as e:
            logging.error(
                f"Could not spawn anomaly {e}",
                exc_info=True,
            )

        (
            critical_paths,
            relevant_waypoint_road_ids_list,
        ) = junction_prep(World.WORLD_STATE.EGO_VEHICLE_ROUTE, distance_to_waypoint)

        static_dict = {
            "critical_paths": critical_paths,
            "relevant_waypoint_road_ids_list": relevant_waypoint_road_ids_list,
        }

        return (
            anomaly_actor,
            transformed_spawnpoint,
            static_dict,
        )

    behavior_update = {}

    if tick_count > 1:
        if critical_paths:
            agent_mode_vehicles = junction_case(
                relevant_waypoint_road_ids_list,
                critical_paths, scenario_id,
            )
            behavior_update["agent_mode_vehicles"] = agent_mode_vehicles
        return behavior_update

    # endregion --------------------------------------------------------------------------------------------------------


# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- SUDDEN BRAKING OF VEHICLE AHEAD BEHAVIOR ------------------------------------------------------------------
# ======================================================================================================================


def sudden_braking_of_vehicle_ahead(
        scenario_config,
        static_dict,
        sensors,
        image_queues,
        tick_count,
        max_tickcount,
        frame_id,
):
    # region -- INITIALIZATION -----------------------------------------------------------------------------------------
    (
        anomaly_config,
        scenario_id,
        ego_vehicle,
        scenario,
    ) = destructure_dict(
        scenario_config,
        "anomaly_config",
        "scenario_id",
        "ego_vehicle",
        "scenario",
    )
    (
        anomaly_bp_name,
        approximate_dist_to_spawning_waypoint,
    ) = destructure_dict(
        anomaly_config,
        "anomaly_bp_name",
        "approximate_dist_to_spawning_waypoint",
    )

    # endregion --------------------------------------------------------------------------------------------------------

    # region -- BEHAVIOR ----------------------------------------------------------------------------------------------

    if tick_count == 1:

        max_attempt = 5
        attempts = 0

        while attempts < max_attempt:
            try:
                # FINDING SPAWNPOINT
                anomaly_spawnpoint = World.make_anomaly_spawnpoint(World.WORLD_STATE,
                                                                   approximate_dist_to_spawning_waypoint, )
                transformed_spawnpoint = anomaly_spawnpoint[0].transform
                transformed_spawnpoint.location.z += 0.7
                logging.debug(f"anomaly_spawnpoint: {anomaly_spawnpoint}")

                anomaly_actor = World.spawn_anomaly_vehicle_to_world(World.WORLD_STATE, anomaly_bp_name,
                                                                     transformed_spawnpoint, )
                logging.info(f"spawned anomaly: {anomaly_actor}\n")
                break
            except Exception as e:
                logging.error(f"Could not spawn anomaly {e}", exc_info=True)
                attempts += 1
                approximate_dist_to_spawning_waypoint += 1

        else:
            raise Exception("Failed to spawn anomaly after 5 attempts")

        # SETTING ANOMALY VEHICLE ROUTE
        anomaly_vehicle_route = World.create_shortest_path_anomaly(World.WORLD_STATE, transformed_spawnpoint,
                                                                   Util.get_transform(scenario_config["scenario"][
                                                                                          "ego_end_spawnpoint"]), )
        World.create_anomaly_behaviour_agent_and_set_global_plan(World.WORLD_STATE, anomaly_vehicle_route)

        return anomaly_actor, transformed_spawnpoint, None

    if 14 < tick_count < Definitions.BREAKING_START or tick_count >= Definitions.BREAKING_STOP:
        World.set_green_relevant_traffic_light("anomaly")
        World.anomaly_vehicle_apply_control_run_step(World.WORLD_STATE)

    elif Definitions.BREAKING_START <= tick_count < Definitions.BREAKING_STOP:
        World.anomaly_vehicle_apply_control_emergency_break()
        logging.debug("anomaly vehicle emergency brake done.")

    if tick_count > 1:
        # FIXME: Leftover from static scenario behavior
        behavior_update = {}
        return behavior_update

    # endregion


# endregion
# ======================================================================================================================

# ======================================================================================================================
# region -- ANOMALY_BEHAVIORS ------------------------------------------------------------------------------------------
# ======================================================================================================================
ANOMALY_BEHAVIORS = {
    AnomalyTypes.NORMALITY: normal_scenario_behavior,
    AnomalyTypes.STATIC: static_scenario_behavior,
    AnomalyTypes.SUDDEN_BREAKING_OF_VEHICLE_AHEAD: sudden_braking_of_vehicle_ahead,
}

# endregion
# ======================================================================================================================
