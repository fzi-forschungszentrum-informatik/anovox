"""
Welcome to AnoVOX

This is the main script to be executed when running a scenario.
This script initializes scenario configurations and runs simulations based on predefined scenarios and meanwhile it
generates data.
"""
import argparse
import logging
import traceback

from colorama import Fore, Style, init

from Definitions import (
    USED_MAPS,
    NBR_OF_SCENARIOS,
)
from FileStructureManager import (
    initialize_variables,
)
from Models.World import World
from Scenarios import (
    ScenarioMain,
    ScenarioDefinitionGenerator,
)

# initialize colorama
init(autoreset=True)


# ======================================================================================================================
# region -- SCENARIO CONFIG AND RUN SCENARIO ---------------------------------------------------------------------------
# ======================================================================================================================
def create_scenario_config(nbr_of_scenarios, maps):
    """
    Initializes variables and generates scenario configuration files.
    """
    initialize_variables()
    try:
        file_paths = ScenarioDefinitionGenerator.generate_all_scenario_config_files(
            nbr_of_scenarios=nbr_of_scenarios,
            maps=maps,
        )
        return file_paths
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(f"{Fore.RED}Error while generating scenario definitions: {e}{Style.RESET_ALL}")
        return False


def run_scenarios(file_paths):
    """
    Runs simulations based on the generated scenario configurations.
    """
    try:
        ScenarioMain.run_all_scenarios_from_configs(file_paths)
        return True
    except Exception as e:
        logging.error(f"{Fore.RED}Error while running scenarios: {e}{Style.RESET_ALL}")
        World.destroy_everything()
        return False


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- MAIN -------------------------------------------------------------------------------------------------------
# ======================================================================================================================
def main():
    """
    Orchestrates the scenario configuration and simulation process.
    """
    parser = argparse.ArgumentParser(description='Run scenarios.')
    parser.add_argument('--file_paths', nargs='*', default=None, help='Optional file paths for scenarios.')
    parser.add_argument('--run', action='store_true', help='Run the scenarios after creating the configuration.')
    args = parser.parse_args()

    if args.file_paths is None:
        file_paths = create_scenario_config(nbr_of_scenarios=NBR_OF_SCENARIOS, maps=USED_MAPS, )
    else:
        file_paths = args.file_paths

    if len(file_paths) == len(USED_MAPS):
        logging.info(f"{Fore.GREEN}Scenario configuration succeeded.{Style.RESET_ALL}")
        if args.run:
            logging.info("Running scenarios...")
            if run_scenarios(file_paths):
                logging.info(f"{Fore.GREEN}Simulation ran successfully. Exiting.{Style.RESET_ALL}")
            else:
                logging.error(f"{Fore.RED}Simulation failed. Exiting.{Style.RESET_ALL}")
    else:
        logging.error(f"{Fore.RED}Scenario configuration failed. Exiting.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

# endregion
# ======================================================================================================================
