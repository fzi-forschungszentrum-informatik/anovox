import json
import logging
import random
import shutil
import uuid

import Definitions
from Definitions import (
    AnomalyTypes,
    WeatherPresets,
    selected_anomaly_types,
    TOWN_CONFIGS,
)
from FileStructureManager import (
    get_scenario_config_output_dir,
)
from Models.World import World
from Scenarios import Util


# ======================================================================================================================
# region -- GENERATE ALL SCENARIO CONFIG FILES -------------------------------------------------------------------------
# ======================================================================================================================


def generate_all_scenario_config_files(nbr_of_scenarios, maps):
    # Step 1: Initialize variables
    town_nbr_scenarios_allocation = {map: 0 for map in maps}
    nbr_scenarios_to_be_allocated = nbr_of_scenarios
    average_nbr_scenarios_per_map = nbr_of_scenarios // len(maps)

    # Step 2: Allocate scenarios to maps
    for index, map in enumerate(maps):
        if index == len(maps) - 1:
            town_nbr_scenarios_allocation[map] = nbr_scenarios_to_be_allocated
            break

        town_nbr_scenarios_allocation[map] = average_nbr_scenarios_per_map
        nbr_scenarios_to_be_allocated -= average_nbr_scenarios_per_map

    # Step 3: Log allocation
    logging.info(f"Allocated: {town_nbr_scenarios_allocation} Scenarios")

    # Step 4: Clear previous configuration files
    shutil.rmtree(get_scenario_config_output_dir())

    file_paths = []
    # Step 5: Generate scenario definition for each map
    for (map_name, allocated_scenarios,) in town_nbr_scenarios_allocation.items():
        World.change_world(World.WORLD_STATE, map_name)
        logging.info(f"TOWN_NBR_SCENARIOS_ALLOCATION[{map_name}]: {allocated_scenarios}")
        file_path = generate_scenario_definition(
            allocated_scenarios,
            map_name=map_name,
            selected_anomaly_types=selected_anomaly_types,
        )

        # Append the file path to the list
        file_paths.append(file_path)

    # Return the list of file paths
    return file_paths


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- GENERATE SCENARIO DEFINITION -------------------------------------------------------------------------------
# ======================================================================================================================
def generate_scenario_definition(amount, map_name, selected_anomaly_types):
    # Mapping anomaly types to corresponding generator functions
    anomaly_configs = {
        AnomalyTypes.NORMALITY: generate_normal_config,
        AnomalyTypes.STATIC: generate_static_config,
        AnomalyTypes.SUDDEN_BREAKING_OF_VEHICLE_AHEAD: generate_sudden_breaking_config,
    }

    data = {
        "scenario_definition": {
            "map": map_name,
            "scenarios": [],
        },
    }

    # Get configuration data for the map
    town_config = TOWN_CONFIGS[map_name]

    for i in range(amount):
        # Selecting a random anomaly type
        anomaly_type = random.choice(selected_anomaly_types)
        generator = anomaly_configs[anomaly_type]
        anomaly_config = generator()

        logging.info(anomaly_config)

        # Generating random spawn points for ego vehicle
        list_of_spawnpoints = World.get_world().get_map().get_spawn_points()

        ego_start_spawnpoint, ego_end_spawnpoint, ego_vehicle_route = Util.get_valid_route(list_of_spawnpoints)

        # Generate scenario template based on anomaly config, spawn points, and route
        scenario_template = generate_scenario_template(
            anomaly_config,
            ego_start_spawnpoint,
            ego_end_spawnpoint,
            ego_vehicle_route,
            town_config
        )

        # Append the scenario template to the list of scenarios
        data["scenario_definition"]["scenarios"].append(scenario_template)

    # Save the generated scenarios to a JSON file
    file_path = f"{get_scenario_config_output_dir()}/scenario_config_map_{map_name}.json"
    with open(file_path, "w") as outfile:
        json.dump(data, outfile, indent=4)

    return file_path


def load_blueprint_id(blueprint_list):
    return f"{random.choice(blueprint_list).id}"


def generate_normal_config():
    return {
        "anomalytype": "NORMALITY",
        "anomaly_bp_name": "---",
        "distance_to_waypoint": 0,
        "rotation": 0
    }


def generate_static_config():
    categories = Definitions.categories
    static_blueprints = []

    for category in categories:
        blueprint_list = [bp for bp in World.get_world().get_blueprint_library().filter(f"static.prop.o_*_{category}")]
        static_blueprints.extend(blueprint_list)

    return {
        "anomalytype": AnomalyTypes.STATIC.name,
        "anomaly_bp_name": load_blueprint_id(static_blueprints),
        "distance_to_waypoint": random.randint(
            Definitions.DISTANCE_INTERVAL[0],
            Definitions.DISTANCE_INTERVAL[1],
        ),
        "rotation": random.uniform(0, 360),
    }


def generate_sudden_breaking_config():
    vehicle_blueprints = [bp for bp in World.get_world().get_blueprint_library().filter("vehicle.*")]
    non_car_keywords = ['bike', 'ambulance', 'firetruck', 'police', 'carlacola', 'fusorosa', 'vespa', 'harley-davidson',
                        'kawasaki', 'yamaha', 'bh', 'diamondback', 'gazelle', 'volkswagen']
    cars_only = [vehicle for vehicle in vehicle_blueprints if
                 all(keyword not in vehicle.id for keyword in non_car_keywords)]

    return {
        "anomalytype": AnomalyTypes.SUDDEN_BREAKING_OF_VEHICLE_AHEAD.name,
        "anomaly_bp_name": load_blueprint_id(cars_only),
        "approximate_dist_to_spawning_waypoint": random.randint(
            Definitions.DISTANCE_INTERVAL_SUDDEN_BREAKING[0],
            Definitions.DISTANCE_INTERVAL_SUDDEN_BREAKING[1],
        ),
    }


def generate_scenario_template(
        anomaly_config,
        ego_spawnpoint,
        ego_end_spawnpoint,
        ego_vehicle_route,
        town_config,
):
    return {
        "anomaly_config": {**anomaly_config},
        "id": f"{uuid.uuid4()}",
        "ego_spawnpoint": {
            "location": {
                "x": ego_spawnpoint.location.x,
                "y": ego_spawnpoint.location.y,
                "z": ego_spawnpoint.location.z,
            },
            "rotation": {
                "pitch": ego_spawnpoint.rotation.pitch,
                "yaw": ego_spawnpoint.rotation.yaw,
                "roll": ego_spawnpoint.rotation.roll,
            },
        },
        "ego_end_spawnpoint": {
            "location": {
                "x": ego_end_spawnpoint.location.x,
                "y": ego_end_spawnpoint.location.y,
                "z": ego_end_spawnpoint.location.z,
            },
            "rotation": {
                "pitch": ego_end_spawnpoint.rotation.pitch,
                "yaw": ego_end_spawnpoint.rotation.yaw,
                "roll": ego_end_spawnpoint.rotation.roll,
            },
        },
        "ego_route": {
            "locations": [
                {
                    "x": point[0].transform.location.x,
                    "y": point[0].transform.location.y,
                    "z": point[0].transform.location.z,
                }
                for point in ego_vehicle_route
            ]
        },
        "weather_preset": f"{random.choice(list(WeatherPresets)).name}",
        "npc_vehicle_amount": town_config["npc_vehicle_amount"],
        "npc_walker_amount": town_config["npc_walker_amount"],

    }

# endregion
# ======================================================================================================================
