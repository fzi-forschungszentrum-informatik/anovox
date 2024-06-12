import json
import os
import sys


def get_json_files(folder_path):
    json_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files


def get_unique_anomaly_names(json_files):
    anomaly_names = set()  # Using a set to automatically remove duplicates
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
            for scenario in data['scenario_definition']['scenarios']:
                anomaly_names.add(scenario['anomaly_config']['anomaly_bp_name'])
    return list(anomaly_names)


def main():
    if len(sys.argv) != 2:
        print("Usage: python anomaly_json_reader.py <folder_path>")
        return

    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        print("Error: Folder path does not exist.")
        return

    json_files = get_json_files(folder_path)
    if not json_files:
        print("No JSON files found in the specified folder and its subfolders.")
        return

    anomaly_names = get_unique_anomaly_names(json_files)

    with open('anomaly_names.txt', 'w') as f:
        for name in anomaly_names:
            f.write(name + '\n')

    print("Anomaly names have been saved to anomaly_names.txt")


if __name__ == "__main__":
    main()
