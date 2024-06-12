"""This Python module initializes global variables and provides functions to manage file paths and directories for a
program dealing with scenario configurations and data outputs. It ensures the existence of necessary directories,
generates timestamps, and constructs structured file paths based on specified parameters."""
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from Definitions import SENSOR_SETUP_FILE_NAME

ROOT_DATA_DIR = os.path.join(Path(__file__).parent, "Data")
ROOT_OUTPUTS_DIR = os.path.join(ROOT_DATA_DIR, "Outputs")
TIME_STAMP = None
THIS_OUTPUT_PATH = ""


def get_scenario_config_output_dir():
    """
    Returns the output directory for scenario configuration files.
    """
    global THIS_OUTPUT_PATH
    scenario_config_path = os.path.join(
        THIS_OUTPUT_PATH,
        "Scenario_Configuration_Files",
    )
    os.makedirs(scenario_config_path, exist_ok=True)
    return scenario_config_path


def initialize_variables():
    """
    Initialize the necessary variables for the program.
    """
    global ROOT_DATA_DIR, ROOT_OUTPUTS_DIR, TIME_STAMP, THIS_OUTPUT_PATH
    logging.info("Initializing variables...")

    # Ensure ROOT_DATA_DIR and ROOT_OUTPUTS_DIR exist
    os.makedirs(ROOT_DATA_DIR, exist_ok=True)
    os.makedirs(ROOT_OUTPUTS_DIR, exist_ok=True)

    # Generate TIME_STAMP and THIS_OUTPUT_PATH
    TIME_STAMP = datetime.now().strftime("%Y_%m_%d-%H_%M")
    THIS_OUTPUT_PATH = os.path.join(
        ROOT_OUTPUTS_DIR,
        f"Final_Output_{TIME_STAMP}",
    )
    os.makedirs(THIS_OUTPUT_PATH, exist_ok=True)

    logging.info(f"Initialized variables: TIME_STAMP={TIME_STAMP}, THIS_OUTPUT_PATH={THIS_OUTPUT_PATH}")


def create_file_name(frame_id, scenario_id, subfolder, file_ending, run_makedirs=True):
    """
    Create a file name based on the given parameters.
    """
    file_name = f"{subfolder}_{str(frame_id)}{file_ending}"  # RGB_IMG + 0123 + .png
    file_path = generate_path_in_scenario(scenario_id, subfolder, file_name, run_makedirs)
    return file_path


def generate_path_in_scenario(scenario_id, sensor_name, file_name, run_makedirs=True):
    """
    This method generates a path for a file in a given scenario and sensor.
    """
    scenario_path = os.path.join(
        THIS_OUTPUT_PATH,
        f"Scenario_{scenario_id}",
    )
    if run_makedirs:
        os.makedirs(scenario_path, exist_ok=True)
    sensor_path = os.path.join(scenario_path, f"{sensor_name}")
    if run_makedirs:
        os.makedirs(sensor_path, exist_ok=True)
    file_path = os.path.join(sensor_path, f"{file_name}")
    return file_path


def save_sensor_setup(scenario_id, sensor_setup_data):
    scenario_path = os.path.join(
        THIS_OUTPUT_PATH,
        f"Scenario_{scenario_id}",
    )
    os.makedirs(scenario_path, exist_ok=True)
    file_path = os.path.join(scenario_path, SENSOR_SETUP_FILE_NAME)

    json_data = {
        k: {
            sk: sv for sk, sv in v.items() if sk not in ('sensor', 'callback', 'dataformat')
        }
        for k, v in sensor_setup_data.items()
    }

    print('Sensor setup json file:')
    print(file_path)
    with open(file_path, 'w') as f:
        json.dump(json_data, f)
