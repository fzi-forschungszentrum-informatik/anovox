import fnmatch
import math
import os

import numpy as np
from numpy.matlib import repmat

import Definitions

color_palette = [(label.id, label.color) for label in Definitions.LABELS]


def frame_args(duration):
    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }


def find_directory(pattern, path):
    for root, dirs, files in os.walk(path):
        for name in dirs:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)
    return None


def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def get_last_output_dir(path):
    last_output_dir = None
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)) and file.startswith("Final_Output_"):
            last_output_dir = file
    if last_output_dir is None:
        raise Exception("No output directory found")
    return last_output_dir


def get_first_scenario(output_dir):
    scenario = None
    for file in os.listdir(output_dir):
        if os.path.isdir(os.path.join(output_dir, file)):
            return os.path.join(output_dir, file)
    raise Exception("No scenario found in the output directory")


def labels_to_cityscapes_palette(image):
    """
    Convert an image containing CARLA semantic segmentation labels to
    Cityscapes palette.
    """
    array = image[:, :, 0]
    result = np.zeros((array.shape[0], array.shape[1], 3))
    for id, value in color_palette:
        result[np.where(array == id)] = np.array(value)
    return result


def point_cloud_labels_to_cityscapes_palette(npy):
    """
    Convert an image containing CARLA semantic segmentation labels to
    Cityscapes palette.
    """
    array = npy[:, 3]
    result = np.zeros((npy.shape[0], 3))
    for key, value in color_palette:
        result[np.where(array == key)] = np.array(value)
    # print(result)
    return np.concatenate((npy[:, :3], result), axis=1)


def depth_to_local_point_cloud(image, color=None, max_depth=0.9):
    """
    Convert an image containing CARLA encoded depth-map to a 2D array containing
    the 3D position (relative to the camera) of each pixel and its corresponding
    RGB color of an array.
    "max_depth" is used to omit the points that are far enough.
    """
    far = 1000.0  # max depth in meters.
    image_fov = 90  # degrees

    normalized_depth = image
    image_height = image.shape[0]
    image_width = image.shape[1]

    # (Intrinsic) K Matrix
    k = np.identity(3)
    k[0, 2] = image_width / 2.0
    k[1, 2] = image_height / 2.0
    k[0, 0] = k[1, 1] = image_width / \
                        (2.0 * math.tan(image_fov * math.pi / 360.0))

    # 2d pixel coordinates
    pixel_length = image_width * image_height
    u_coord = repmat(np.r_[image_width - 1:-1:-1],
                     image_height, 1).reshape(pixel_length)
    v_coord = repmat(np.c_[image_height - 1:-1:-1],
                     1, image_width).reshape(pixel_length)
    if color is not None:
        color = color.reshape(pixel_length, 3)
    normalized_depth = np.reshape(normalized_depth, pixel_length)

    # Search for pixels where the depth is greater than max_depth to
    # delete them
    max_depth_indexes = np.where(normalized_depth > max_depth)
    normalized_depth = np.delete(normalized_depth, max_depth_indexes)
    u_coord = np.delete(u_coord, max_depth_indexes)
    v_coord = np.delete(v_coord, max_depth_indexes)
    if color is not None:
        color = np.delete(color, max_depth_indexes, axis=0)

    # pd2 = [u,v,1]
    p2d = np.array([u_coord, v_coord, np.ones_like(u_coord)])

    # P = [X,Y,Z]
    p3d = np.dot(np.linalg.inv(k), p2d)
    p3d *= normalized_depth * far

    # Formating the output to:
    # [[X1,Y1,Z1,R1,G1,B1],[X2,Y2,Z2,R2,G2,B2], ... [Xn,Yn,Zn,Rn,Gn,Bn]]
    # if color is not None:
    # np.concatenate((np.transpose(p3d), color), axis=1)
    # return sensor.PointCloud(
    #     image.frame_number,
    #     np.transpose(p3d),
    #     color_array=color)
    # [[X1,Y1,Z1],[X2,Y2,Z2], ... [Xn,Yn,Zn]]
    return np.transpose(p3d)


class AnimationButtons():
    def play(frame_duration=100, transition_duration=0):
        return dict(label="Play", method="animate", args=
        [None, {"frame": {"duration": frame_duration, "redraw": True},
                "mode": "immediate",
                "fromcurrent": True, "transition": {"duration": transition_duration, "easing": "linear"}}])

    def pause():
        return dict(label="Pause", method="animate", args=
        [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}])
