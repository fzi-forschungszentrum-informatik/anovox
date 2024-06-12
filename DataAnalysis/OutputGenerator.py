"""This module facilitates output management by generating CSV files and zipping output directories in a
scenario-based system."""
import logging

import Definitions
from FileStructureManager import create_file_name


# ======================================================================================================================
# region -- CSV_FILES---------------------------------------------------------------------------------------------------
# ======================================================================================================================


def generate_action_csv(action_obj):
    """
    Generate a CSV file for the given action object.
    """
    file_path = create_file_name(
        frame_id=action_obj.frame_id,
        scenario_id=action_obj.scenario_id,
        subfolder=Definitions.DataFormat.ACTION.name,
        file_ending=Definitions.DataFormat.ACTION.value,
    )
    logging.debug(f"file_path: {file_path}")

    with open(file_path, "w") as f:
        for key, value in action_obj.action_dict.items():
            f.write(f"{key} ; {value}\n")


def generate_anomaly_csv(action_obj):
    """
    Generates a CSV file containing anomaly data based on the provided action object.
    """
    file_path = create_file_name(
        frame_id=action_obj.frame_id,
        scenario_id=action_obj.scenario_id,
        subfolder=Definitions.DataFormat.ANOMALY.name,
        file_ending=Definitions.DataFormat.ANOMALY.value,
    )

    logging.debug(f"file_path: {file_path}")

    with open(file_path, "w") as f:
        for key, value in action_obj.anomaly_dict.items():
            f.write(f"{key} ; {value}\n")

# endregion
# =====================================================================================================================
