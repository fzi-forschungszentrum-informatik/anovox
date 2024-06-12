import logging
import os
import sys

import numpy as np
import open3d as o3d

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Definitions import VOXEL_RESOLUTION_YC
from LabelUtils import get_label_attributes


def check_file_ending(path):
    """
    This function takes a file path as input and checks if the file has a '.npy' extension.
    """
    # Extract the file extension from the path
    file_ending = path.split(".")[-1]

    # Log the extracted file extension
    logging.info(f"File extension: {file_ending}")

    # Check if the file extension is 'npy'
    if file_ending == "npy":
        return True
    else:
        return False


def open_npy(file_path):
    try:
        # Load voxel data from file
        voxel_data = np.load(file_path)

        # Extract voxel points and colors
        voxel_points = voxel_data[:, :3]
        voxel_colors = voxel_data[:, 3:]

        # Retrieve colors for semantic labels
        colors = [get_label_color(semantic_label) for semantic_label in voxel_colors]
        voxel_colors = np.squeeze(colors) / 255.0

        # Create PointCloud object
        voxel_pcd = o3d.geometry.PointCloud()
        voxel_pcd.points = o3d.utility.Vector3dVector(voxel_points)
        voxel_pcd.colors = o3d.utility.Vector3dVector(voxel_colors)

        # Create VoxelGrid from PointCloud
        voxel_world = o3d.geometry.VoxelGrid.create_from_point_cloud(voxel_pcd, VOXEL_RESOLUTION_YC)

        # Visualize the voxel world
        o3d.visualization.draw_geometries([voxel_world])

    except Exception as e:
        # Log error if file cannot be opened
        logging.error(f"Could not open file: {file_path}", exc_info=True)


def get_label_color(label_id):
    # Assuming you have a function to retrieve color for a given label ID
    return get_label_attributes("id", label_id, "color")


if __name__ == "__main__":
    inputs = sys.argv[1:]
    for input in inputs:
        logging.info(f"## Opening {input} ##")
        if check_file_ending(input):
            open_npy(input)
        else:
            logging.info("     --> wrong filetype")
