import os
import shutil


# Function to delete folder by ID
def delete_folders_with_ids(folder_path, ids_file):
    # Read scenario IDs from file
    with open(ids_file, 'r') as file:
        scenario_ids = file.read().splitlines()

    # Iterate through folders
    for folder_name in os.listdir(folder_path):
        # Check if folder name starts with 'Scenario_' and ends with a valid UUID
        if folder_name.startswith('Scenario_') and '-' in folder_name:
            folder_id = folder_name.split('_')[-1]
            if folder_id in scenario_ids:
                # Delete folder
                folder_to_delete = os.path.join(folder_path, folder_name)
                print(f"Deleting folder: {folder_to_delete}")
                try:
                    shutil.rmtree(folder_to_delete)
                    print(f"Folder {folder_name} deleted successfully.")
                except OSError as e:
                    print(f"Error deleting folder {folder_name}: {e}")


def main():
    # Directory containing scenario folders
    folder_path = 'folder_path'

    # Input file containing scenario IDs
    ids_file = 'scenario_id_fails.txt'

    # Call function to delete folders
    delete_folders_with_ids(folder_path, ids_file)


if __name__ == "__main__":
    main()
