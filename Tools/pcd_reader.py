import logging
import os
import sys

import numpy as np
import open3d as o3d

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LabelUtils import get_label_attributes


def is_semantic(file_path):
    file_name = os.path.basename(file_path)
    return "SEMANTIC" in file_name


def check_file_ending(path):
    file_ending = path.split(".")[-1]
    logging.info(f" checking file ending: {file_ending}")
    return file_ending == "pcd" or file_ending == "ply" or file_ending == "npy"


def open_file(file_path, semantic=False):
    try:
        pcd = np.load(file_path)
        points = pcd[:, :3]
        meta_data = pcd[:, 3:]
        vis_pcd = o3d.geometry.PointCloud()
        vis_pcd.points = o3d.utility.Vector3dVector(points)
        unique_label = set()
        if semantic:
            colors = [get_label_attributes("id", semantic_label, "color") for semantic_label in meta_data]
            unique_label.add(tuple(colors))  # Convert the list to a tuple
            print(unique_label)
            vis_pcd.colors = o3d.utility.Vector3dVector(np.array(colors) / 255.0)  # for open3d
        o3d.visualization.draw_geometries([vis_pcd])
    except Exception as e:
        logging.error(
            f"Could not open file: {file_path}",
            exc_info=True,
        )


if __name__ == "__main__":
    inputs = sys.argv[1:]
    for input in inputs:
        logging.info(f"## Opening {input} ##")
        if check_file_ending(input):
            semantic = is_semantic(input)
            open_file(input, semantic)
        else:
            logging.info("     --> wrong filetype")
