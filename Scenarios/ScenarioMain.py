"""This is the main file for scenarios. It contains the run_all_scenarios_from_configs() function, which is the entry
point. It includes functions to set up the simulation environment, spawn an ego vehicle, attach sensors,
run scenarios defined in configuration files, and collect output data, with a specific focus on anomaly detection
scenarios."""

import functools
import json
import logging
import time
from collections import namedtuple

from colorama import Fore, Style

import Definitions
from DataAnalysis import DataGenerator, BevGenerator
from DataAnalysis.Utils import (
    get_label_attributes,
)
from Definitions import AnomalyTypes
from FileStructureManager import save_sensor_setup
from Models.World import World
from Models.World.World import (
    deactivate_synchronous_mode_settings,
    compute_world_offset,
    start_movement_of_npcs, debug_route, )
from Scenarios import Util
from .AnomalyBehaviourDefinitions import (
    ANOMALY_BEHAVIORS,
)
from .ScenarioUtil import (
    construct_cameras_and_sensors,
    build_scenario_config,
    stop_sensors,
    start_listening_cameras_lidars,
    initialize_cameras_and_sensors_queues,
)
from .Util import (
    get_action_state_data,
    update_progress,
)


# ======================================================================================================================
# region -- 1. RUN_ALL_SCENARIOS_FROM_CONFIGS --------------------------------------------------------------------------
# ======================================================================================================================
def run_all_scenarios_from_configs(file_paths):
    """
    Runs all scenarios defined in configuration files. This function iterates over scenario configuration files,
    sets up the simulation environment, spawns an ego vehicle, attaches sensors, runs each scenario, and collects the
    output data.
    """

    World.create_world(synchronous_mode=False)
    scenario_config_files = file_paths

    outputs_as_dict = {}

    sensors = None
    coll_detec = None

    try:
        # Iterate over each scenario configuration file
        for scenario_config_file in scenario_config_files:
            scenario_definitions = Util.get_scenario_config(scenario_config_file)
            World.change_world(
                World.WORLD_STATE,
                scenario_definitions["scenario_definition"]["map"],
            )

            logging.debug(f"SCENARIO_CONFIG: {scenario_config_file}")
            logging.debug(f'SCENARIO_CONFIG_MAP: {scenario_definitions["scenario_definition"]["map"]}')

            # Iterate over each scenario defined in the configuration
            for scenario in scenario_definitions["scenario_definition"]["scenarios"]:
                try:
                    # SCENARIO STARTED PREPARATION
                    logging.info(f'Starting Scenario: {scenario["id"]}')
                    logging.debug(f"{json.dumps(scenario, sort_keys=True, indent=4)}")

                    # SETTING WEATHER
                    World.set_weather(
                        World.WORLD_STATE,
                        scenario["weather_preset"],
                    )

                    # SPAWNING EGO_VEHICLE
                    ego_spawnpoint = Util.get_transform(scenario["ego_spawnpoint"])
                    ego_vehicle = World.spawn_ego_vehicle_to_world(
                        World.WORLD_STATE,
                        vehicle_name=Definitions.EGO_VEHICLE,
                        spawn_points_num=ego_spawnpoint,
                    )

                    # ATTACHING ALL CAMERAS AND SENSORS TO EGO_VEHICLE
                    sensors, transforms = construct_cameras_and_sensors(ego_vehicle)
                    coll_detec = World.spawn_coll_detec_sensor(World.WORLD_STATE, ego_vehicle)

                    # BUILD SCENARIO CONFIG
                    scenario_config = build_scenario_config(scenario, ego_vehicle)

                    # SAVE SERVER SETUP JSON SPECIFICATION FILE
                    save_sensor_setup(scenario_id=scenario_config["scenario_id"], sensor_setup_data=sensors)

                    # RUN_SCENARIO
                    frame_datas_as_list = run_scenario(
                        scenario_config,
                        sensors,
                        coll_detec,
                        transforms
                    )

                    # ADDING SCENARIO OUTPUT TO OUTPUTS
                    # 1700mb per scenario without this line
                    outputs_as_dict[scenario_config["scenario_id"]] = frame_datas_as_list

                    # SCENARIO FINISHED
                    World.destroy_everything()
                    logging.info(f"\n{Fore.GREEN}Finished Scenario {scenario['id']}{Style.RESET_ALL}\n")

                except Exception:
                    logging.error(
                        "Exception, waiting 10 secs then continuing",
                        exc_info=True,
                    )
                    time.sleep(10)
                    stop_sensors(sensors)
                    coll_detec.stop()
                    World.destroy_everything()
                    time.sleep(3)
                    continue

    except Exception as e:
        logging.error(
            "Exception in scenario run",
            exc_info=True,
        )
    finally:
        logging.info("All Scenarios finished, now creating output zip")
        deactivate_synchronous_mode_settings(World.WORLD_STATE)


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- 2. RUN_SCENARIO --------------------------------------------------------------------------------------------
# ======================================================================================================================
def run_scenario(scenario_config, sensors, coll_detec, transforms):
    """
    Runs a scenario based on the provided scenario configuration and sensors.
    """
    frame_datas_as_list = []

    try:
        frame_datas_as_list = run_in_synchronous_mode(
            excecute_scenario_behavior=ANOMALY_BEHAVIORS[AnomalyTypes[scenario_config["anomaly_type"]]],
            scenario_config=scenario_config,
            sensors=sensors,
            coll_detec=coll_detec,
            transforms=transforms
        )
    except ValueError as e:
        World.write_scenario_id_to_file(scenario_config["scenario_id"])
        logging.error(f"An error occurred: {e}")
        raise e

    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
        logging.error(f"Unknown Scenario Type or Scenario: {e}")

    return frame_datas_as_list


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- 3. SYNCHRONOUS MODE ----------------------------------------------------------------------------------------
# ======================================================================================================================
def run_in_synchronous_mode(
        excecute_scenario_behavior,
        scenario_config,
        sensors,
        coll_detec,
        transforms
):
    """
    Run the scenario in synchronous mode.
    """

    frame_data_list = []
    World.activate_synchronous_mode_settings(World.WORLD_STATE)
    traffic_manager = World.activate_traffic_manager()

    World.move_spectator_behind_vehicle(World.WORLD_STATE, World.get_ego_vehicle())

    # CREATE SHORTEST ROUTE FOR EGO_VEHICLE
    ego_vehicle_route = World.create_shortest_path(
        World.WORLD_STATE,
        Util.get_transform(scenario_config["scenario"]["ego_spawnpoint"]),
        Util.get_transform(scenario_config["scenario"]["ego_end_spawnpoint"]),
    )
    logging.debug(f"created shortest path for the ego_vehicle")

    # CREATE AGENT FOR EGO_VEHICLE
    World.create_behavior_agent_and_set_global_plan(World.WORLD_STATE, ego_vehicle_route)

    # DEBUG EGO_VEHICLE_ROUTE ON SPECTATOR
    debug_route(World.WORLD_STATE, ego_vehicle_route)

    # COMPUTE MAP OFFSET FOR BEV ROUTE MAP
    compute_world_offset(World.WORLD_STATE)

    # CAMERAS AND SENSORS QUEUE
    image_lidar_queues = initialize_cameras_and_sensors_queues(sensors)

    # TICKING STARTED
    tick_count = 0

    # SPAWNING IN THE FIRST 15 TICKS
    frame_id, tick_count = update_progress(
        tick_count,
        Definitions.MAX_TICKCOUNT,
        "Scenario Progress",
    )  # tick_count = 1

    static_dict = {
        "junction_found": None,
        "critical_paths": None,
        "relevant_waypoint_road_ids_list": None,
    }

    result = None

    if scenario_config["anomaly_type"] == "NORMALITY":
        excecute_scenario_behavior(
            scenario_config,
            static_dict,
            sensors,
            image_lidar_queues,
            tick_count,
            Definitions.MAX_TICKCOUNT,
            frame_id,
        )
    else:
        (
            result
        ) = excecute_scenario_behavior(
            scenario_config,
            static_dict,
            sensors,
            image_lidar_queues,
            tick_count,
            Definitions.MAX_TICKCOUNT,
            frame_id,
        )

    anomaly_id = None

    if result:
        anomaly_object, anomaly_spawnpoint, static_dict = result
        anomaly_id = anomaly_object.id

    ego_vehicle_id = scenario_config["ego_vehicle"].id
    Instance_Label = namedtuple(
        "Instance_Label",
        [  # data structure storing all objects that need to be relabeled for ground truth data
            "label_type",
            "instance_id",
            "semantic_id",
        ],
    )

    frame_id, tick_count = update_progress(
        tick_count,
        Definitions.MAX_TICKCOUNT,
        "Scenario Progress",
    )  # tick_count = 2

    # SPAWNING NPCS (VEHICLES AND WALKERS)
    npc_walker_amount = scenario_config["scenario"]["npc_walker_amount"]
    npc_vehicle_amount = scenario_config["scenario"]["npc_vehicle_amount"]
    World.spawn_npcs_to_world(World.WORLD_STATE, npc_vehicle_amount, npc_walker_amount)

    while tick_count < 15:
        frame_id, tick_count = update_progress(
            tick_count,
            Definitions.MAX_TICKCOUNT,
            "Scenario Progress",
        )  # tick_count = 3 to 15

    # START LISTENING OF CAMERAS AND SENSORS
    start_listening_cameras_lidars(sensors, image_lidar_queues)

    # START MOVEMENT OF NPCS
    start_movement_of_npcs(traffic_manager.get_port())

    excecute_scenario_behavior(
        scenario_config,
        static_dict,
        sensors,
        image_lidar_queues,
        tick_count,
        Definitions.MAX_TICKCOUNT,
        frame_id,
    )

    instances_to_relabel = [Instance_Label(
        "ego_vehicle",
        ego_vehicle_id,
        get_label_attributes("name", "ego_vehicle", "id"),
    )
        # ego vehicle should be relabeled as unseen
    ]

    # if scenario_config["anomaly_type"] == "STATIC":
    #    instances_to_relabel.append(Instance_Label(
    #        "anomaly",
    #        anomaly_id,
    #        get_label_attributes("name", "anomaly", "id"),
    #    ))

    # -- region START-REAL-SCENARIO-TIME -------------------------------------------------------------------------------

    while tick_count < Definitions.MAX_TICKCOUNT:
        World.set_green_relevant_traffic_light()

        anomaly_type = scenario_config['anomaly_config']['anomalytype']
        World.ego_vehicle_apply_control_run_step(World.WORLD_STATE, anomaly_type)

        World.normal_vehicle_agent_apply_control_run_step(World.WORLD_STATE)

        if len(World.WORLD_STATE.EGO_VEHICLE_COLLISIONS) > 0:
            for collision in World.WORLD_STATE.EGO_VEHICLE_COLLISIONS:
                if 'walker.pedestrian' in collision.other_actor.type_id:
                    logging.error(f"Ego vehicle crashed into pedestrian. Ignore scenario")
                    raise ValueError('pedestrian_crash')
                    # write_scenario_id_to_file(scenario_config["scenario_id"])

        frame_id, tick_count = update_progress(
            tick_count,
            Definitions.MAX_TICKCOUNT,
            "Scenario Progress",
        )  # tick_count = 15 to Definitions.MAX_TICKCOUNT

        behavior_update = excecute_scenario_behavior(
            scenario_config,
            static_dict,
            sensors,
            image_lidar_queues,
            tick_count,
            Definitions.MAX_TICKCOUNT,
            frame_id,
        )

        if (
                Definitions.BREAKING_START <= tick_count <= Definitions.BREAKING_STOP) and anomaly_type == "SUDDEN_BREAKING_OF_VEHICLE_AHEAD":
            instances_to_relabel.append(Instance_Label(
                "anomaly",
                anomaly_id,
                get_label_attributes("name", "anomaly", "id"),
            ))

        if not (
                Definitions.BREAKING_START <= tick_count <= Definitions.BREAKING_STOP) and anomaly_type == "SUDDEN_BREAKING_OF_VEHICLE_AHEAD":
            instances_to_relabel.append(Instance_Label(
                "agent",
                anomaly_id,
                get_label_attributes("name", "agent_car", "id"),
            ))

        # behavior_update has values interesting for the data generation such as agent labels etc.
        if scenario_config["anomaly_type"] == "STATIC":
            actors_in_agent_mode = behavior_update.get("agent_mode_vehicles") or []

            for agent in actors_in_agent_mode:
                semantic_tag = agent.semantic_tags[0]
                agent_semantic_tag = semantic_tag + 100
                agent_instance_label = Instance_Label("agent", agent.id, agent_semantic_tag, )
                instances_to_relabel.append(agent_instance_label)

        if tick_count % Definitions.TICK_COUNT_MODULO_VALUE == 0:
            logging.debug(f"Current ego_vehicle location: {scenario_config['ego_vehicle'].get_location()}")

            # GETTING ACTION STATES
            logging.debug("GETTING ACTION STATES")
            action_state_dict = get_action_state_data(scenario_config["scenario_id"], frame_id,
                                                      scenario_config['anomaly_config']['anomalytype'])

            # GETTING FRAME DATA
            frame_data_object = DataGenerator.generate_data(
                scenario_id=scenario_config["scenario_id"],
                frame_id=frame_id,
                sensor_callbacks=[
                    {
                        "sensor": sensors[sensor_name]['sensor'],
                        "callback": functools.partial(
                            sensors[sensor_name]['callback'],
                            data_queue=image_lidar_queues[sensor_name],
                            sensor_name=sensor_name,
                            file_ending=sensors[sensor_name]['file_ending'],
                            dataformat=sensors[sensor_name]['dataformat'],
                            sensor_type=sensors[sensor_name]['sensor_type'],
                            location=sensors[sensor_name]['location'],
                            rotation=sensors[sensor_name]['rotation'],
                            save_data=sensors[sensor_name]['save_data']
                        )
                    } for sensor_name in sensors
                ],
                sensor_transforms=transforms,
                id_labels=instances_to_relabel,
                tick_count=tick_count,
                anomaly_type=scenario_config['anomaly_config']['anomalytype'],
            )

            frame_bev_object = BevGenerator.generate_data(
                scenario_config["scenario_id"],
                frame_id
            )

            frame_data_object.action_state_dict = action_state_dict
            if frame_data_object:
                frame_data_list.append(frame_data_object)

            frame_bev_object.action_state_dict = action_state_dict
            if frame_bev_object:
                frame_data_list.append(frame_bev_object)
        else:
            for queue in image_lidar_queues.values():
                queue.get()

    # endregion --------------------------------------------------------------------------------------------------------

    World.WORLD_STATE.anomalous_behavior_started = False  # for dynamic scenarios
    stop_sensors(sensors)
    coll_detec.stop()

    # delete frame data from memory
    del frame_data_list

    return True

# endregion
# ======================================================================================================================
