"""
In this module we want to voxelize the files seperated from the main script and increase the perfomance and
 stability of the framework
"""
import itertools
import json
import logging
import os
import sys
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
from PIL import Image
from colorama import Fore, Style

from Definitions import (
    VOXEL_RESOLUTION_YC,
    VOXEL_SIZE_YC,
    BEV_OFFSET_FORWARD_YC,
    BEV_RESOLUTION_YC,
    OFFSET_Z_YC,
    SENSOR_SETUP_FILE_NAME,
)
from EgoVehicleSetup import DEPTH_CAM_TYPE, SEMANTIC_CAM_TYPE, SEMANTIC_LIDAR_TYPE
from Tools.LabelUtils import get_label_attributes

COUNTER_TEST = 0
LENGHT_FILES = 0

# ======================================================================================================================
# region -- LOGGING ----------------------------------------------------------------------------------------------------
# ======================================================================================================================

# Configure logging
logging.basicConfig(
    filename="logfile.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s: %(message)s",
    filemode="a",
)


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- HELPER FUNCTIONS -------------------------------------------------------------------------------------------
# ======================================================================================================================

def visualize_point_clound(point_cloud):
    # https://stackoverflow.com/questions/62433465/how-to-plot-3d-point-clouds-from-an-npy-file
    x = point_cloud[:, 0]
    y = point_cloud[:, 1]
    z = point_cloud[:, 2]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x, y, z)
    plt.show()
    return


def rotate_point_cloud(point_cloud, rotation):
    """
    point_cloud: <numpy.ndarray> of shape (<number of points>, 4), containg x, y, z and color, respectively.
    rotation: (<float>, <float>, <float>) containing x, y, and z rotations, respectively, in degrees.

    This function receives a numpy point cloud of shape (<number of points>, 4), and returns, a numpy point cloud
    of the same shape, with rotated coordinates.
    """

    # Create a point cloud object and set its points
    o3d_pcd = o3d.geometry.PointCloud()
    o3d_pcd.points = o3d.utility.Vector3dVector(point_cloud[:, :-1])

    # Rotate the point cloud to fit with lidar point cloud
    gradians = tuple(np.pi * (deg / 180) for deg in rotation)
    r_matrix = o3d_pcd.get_rotation_matrix_from_xyz(gradians)
    o3d_pcd.rotate(r_matrix, center=(0, 0, 0))

    # Combine the point cloud coordinates and colors into a single array
    point_cloud = np.concatenate([np.asarray(o3d_pcd.points), np.array(point_cloud[:, -1]).reshape(-1, 1)], axis=1)

    return point_cloud


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- PROCESS GENERATE VOXEL -------------------------------------------------------------------------------------
# ======================================================================================================================


def _parse_sensor_data_json(sensor_data_json_path):
    with open(sensor_data_json_path) as f:
        sensor_description_dict = json.load(f)

    sensor_list = list()
    for sensor_name in sensor_description_dict:
        sensor_dict = sensor_description_dict[sensor_name]
        sensor_dict['location'] = tuple(sensor_dict['location'])
        sensor_dict['rotation'] = tuple(sensor_dict['rotation'])
        sensor_dict['name'] = sensor_name
        sensor_list.append(sensor_dict)

    # we need a sorted list for groupby
    sensor_list.sort(key=lambda d: (d['location'], d['rotation']))

    sensor_groups = list()
    for location_rotation, sensors in itertools.groupby(sensor_list, key=lambda d: (d['location'], d['rotation'])):
        sensor_groups.append({
            'sensors': list(sensors),
            'location': location_rotation[0],
            'rotation': location_rotation[1]
        })

    return sensor_groups


def _get_sensors_by_type(sensor_list, *types):
    output = dict()
    for sensor in sensor_list:
        type_match = [sensor['sensor_type'] for t in types if sensor['sensor_type'] == t]
        if type_match:
            output[type_match[0]] = {
                'name': sensor['name'],
                'file_ending': sensor['file_ending']
            }
            if type_match[0] == DEPTH_CAM_TYPE:
                for key in ('image_width', 'image_height', 'camera_fov'):
                    output[type_match[0]][key] = sensor['args'][key]

    return output


def _get_files_from_one_scenario(scenario_root, scenario_sensor_setup_json_path):
    sensor_groups = _parse_sensor_data_json(scenario_sensor_setup_json_path)
    file_paths = list()

    # We will open a reference sensor, to get frame ids, etc.
    # It does not matter which one we open, because we only want to consider frames
    # for which we have data from every sensor. 
    ref_sensor_name = sensor_groups[0]['sensors'][0]['name']
    ref_sensor_frames = os.listdir(os.path.join(scenario_root, ref_sensor_name))
    ref_sensor_frames = [rsf for rsf in ref_sensor_frames if rsf[-len('.png'):] == '.png']
    ref_sensor_frames.sort()

    frame_numbers = [rsf[:-len('.png')].split('_')[-1] for rsf in ref_sensor_frames]

    for frame_number in frame_numbers:
        frame_dict = {
            'frame_number': frame_number,
            DEPTH_CAM_TYPE: dict(),
            SEMANTIC_CAM_TYPE: dict(),
            SEMANTIC_LIDAR_TYPE: dict(),
            'scenario_root': scenario_root
        }
        for group in sensor_groups:
            sensors = _get_sensors_by_type(group['sensors'], DEPTH_CAM_TYPE, SEMANTIC_CAM_TYPE, SEMANTIC_LIDAR_TYPE)
            for sensor_type in sensors:
                data_file_path = os.path.join(
                    scenario_root, sensors[sensor_type]['name'],
                    '{}_{}{}'.format(sensors[sensor_type]['name'], frame_number, sensors[sensor_type]['file_ending'])
                )
                if os.path.isfile(data_file_path):
                    frame_dict[sensor_type][(group['location'], group['rotation'])] = {
                        'path': data_file_path,
                    }
                    if sensor_type == DEPTH_CAM_TYPE:
                        frame_dict[sensor_type][(group['location'], group['rotation'])]['image_width'] = \
                        sensors[sensor_type]['image_width']
                        frame_dict[sensor_type][(group['location'], group['rotation'])]['image_height'] = \
                        sensors[sensor_type][
                            'image_height']
                        frame_dict[sensor_type][(group['location'], group['rotation'])]['camera_fov'] = \
                        sensors[sensor_type]['camera_fov']

        file_paths.append(frame_dict)

    return file_paths


def get_file_paths(root_folder):
    file_paths = list()

    for dirpath, dirnames, filenames in os.walk(root_folder):
        cur = dirpath.split('/')[-1]
        if cur[:len('Scenario_')] == 'Scenario_' and [f for f in filenames if f == SENSOR_SETUP_FILE_NAME]:
            files_from_scenario = _get_files_from_one_scenario(
                scenario_root=dirpath,
                scenario_sensor_setup_json_path=os.path.join(dirpath,
                                                             [f for f in filenames if f == SENSOR_SETUP_FILE_NAME][0])
            )
            file_paths += files_from_scenario

    global LENGHT_FILES
    LENGHT_FILES = len(file_paths)

    return file_paths


def process_file(args):
    # Unpack the arguments
    i, files = args

    update_progress()

    # Load data from files
    point_clouds = list()
    data = dict()
    location_rotations = set()
    for sensor_type in (DEPTH_CAM_TYPE, SEMANTIC_CAM_TYPE, SEMANTIC_LIDAR_TYPE):
        data[sensor_type] = dict()
        for location_rotation in files[sensor_type]:
            location_rotations.add(location_rotation)
            if sensor_type in (DEPTH_CAM_TYPE, SEMANTIC_CAM_TYPE):
                data[sensor_type][location_rotation] = np.array(
                    Image.open(files[sensor_type][location_rotation]['path']))
            else:
                data[sensor_type][location_rotation] = np.load(files[sensor_type][location_rotation]['path'])

    # Handle data loaded from files
    point_clouds = list()
    for location_rotation in location_rotations:
        location, rotation = location_rotation

        if data.get(DEPTH_CAM_TYPE) is not None and data[DEPTH_CAM_TYPE].get(location_rotation) is not None \
                and data.get(SEMANTIC_CAM_TYPE) is not None and data[SEMANTIC_CAM_TYPE].get(
            location_rotation) is not None:
            depth_image_point_cloud = depth_to_pcd(
                depth_img_data=data[DEPTH_CAM_TYPE][location_rotation],
                semantic_img_data=data[SEMANTIC_CAM_TYPE][location_rotation],
                image_width=files[DEPTH_CAM_TYPE][location_rotation]['image_width'],
                image_height=files[DEPTH_CAM_TYPE][location_rotation]['image_height'],
                camera_fov=files[DEPTH_CAM_TYPE][location_rotation]['camera_fov']
            )
        else:
            depth_image_point_cloud = None
        if data.get(SEMANTIC_LIDAR_TYPE) is not None and data[SEMANTIC_LIDAR_TYPE].get(location_rotation) is not None:
            semantic_lidar_point_cloud = data[SEMANTIC_LIDAR_TYPE][location_rotation]
        else:
            semantic_lidar_point_cloud = None

        negative_rotation = tuple(-v for v in rotation)
        for point_cloud in [pc for pc in (depth_image_point_cloud, semantic_lidar_point_cloud) if pc is not None]:
            point_cloud = rotate_point_cloud(point_cloud=point_cloud, rotation=negative_rotation)
            for i, v in enumerate(location):
                point_cloud[:, i] -= v
        point_clouds.append(point_cloud)

    merged_point_cloud = np.concatenate(point_clouds, axis=0)
    # visualize_point_clound(merged_point_cloud)
    file_number = files["frame_number"]
    file_name = f"VOXEL_GRID_{file_number}"

    # Create a separate Voxel Grid folder for each subfolder
    voxel_grid_folder = os.path.join(files["scenario_root"], "VOXEL_GRID")
    os.makedirs(voxel_grid_folder, exist_ok=True)

    # Voxelize the merged point cloud
    voxel_data = voxelize_one(merged_point_cloud)
    logging.debug(f"Processed file {i}/{200}: created voxel world")

    # Save voxel grid data
    output_voxel_grid_path = os.path.join(voxel_grid_folder, file_name)
    np.save(output_voxel_grid_path, voxel_data)


def process_files_parallel(file_paths, num_processes=10):
    # Create a multiprocessing Pool with the specified number of processes
    pool = Pool(processes=num_processes)

    # Prepare arguments for the process_file function
    # Each argument is a tuple (index, files) for parallel processing

    args_list = []
    for i, files in enumerate(file_paths):
        args_list.append((i, files))

    # Execute the process_file function in parallel using the Pool
    pool.map(process_file, args_list)

    # Close the pool to prevent any more tasks from being submitted
    pool.close()

    # Wait for all worker processes to finish
    pool.join()


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- PROGRESS BAR -----------------------------------------------------------------------------------------------
# ======================================================================================================================
def update_progress():
    global COUNTER_TEST
    global LENGHT_FILES
    COUNTER_TEST += 20
    print_progress_bar(COUNTER_TEST, LENGHT_FILES)


def print_progress_bar(index, total):
    n_bar = 30  # Modern progress display with 30 blocks
    progress = index / total
    num_blocks = int(n_bar * progress)
    num_spaces = n_bar - num_blocks
    progress_percent = int(progress * 100)

    if progress_percent == 100:
        # At 100%, change the color to Green
        color = Fore.GREEN
    elif progress_percent >= 75:
        # At 75% and above, change the color to Yellow
        color = Fore.LIGHTYELLOW_EX
    elif progress_percent >= 30:
        # At 50% and above, change the color to Orange
        color = Fore.LIGHTYELLOW_EX
    else:
        # For everything else, stay at Red
        color = Fore.RED

    # Progress display with the corresponding color
    progress_bar = f"generating data: [{color}{'█' * num_blocks}{' ' * num_spaces}{Style.RESET_ALL}] {progress_percent}%"

    # Improved formatting for brackets and scenario progress
    sys.stdout.write("\r" + progress_bar.ljust(60) + f"({index}/{total})")
    sys.stdout.flush()


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- VOXELIZE ---------------------------------------------------------------------------------------------------
# ======================================================================================================================


def depth_to_pcd(depth_img_data, semantic_img_data, image_width, image_height, camera_fov):
    """Converts a depth image into a point cloud. Each point is colored based on the semantic image."""

    # Initialize lists to store point coordinates and colors
    point_list = []
    color_list = []

    # Calculate focal length based on fov
    focal = image_width / (2.0 * np.tan(camera_fov * np.pi / 360.0))

    # Define center of the image
    cx = image_width / 2.0  # from camera projection matrix
    cy = image_height / 2.0

    # Calculate true depth data
    true_depth_data = calculate_depth(depth_img_data, image_width, image_height)

    # Iterate over each pixel in the image
    for i in range(image_height):
        for j in range(image_width):
            # Get depth value at current pixel
            z = true_depth_data[i, j]

            # Perform depth projection
            x, y = (j - cx) * z / focal, (i - cy) * z / focal
            coordinate = [x, y, z]

            # If the coordinate is too far away, skip it
            if np.linalg.norm(coordinate) > 100:
                continue

            # Otherwise, add the coordinate and its corresponding color to the lists
            point_list.append(coordinate)
            point_label = semantic_img_data[i][j]
            color_list.append(point_label)

    depth_pcloud = rotate_point_cloud(
        point_cloud=np.concatenate([np.asarray(point_list), np.array(color_list).reshape(-1, 1)], axis=1),
        rotation=(-90, 90, 0)
    )

    return depth_pcloud


# @numba.jit(nopython=True)  # Compile the function with Numba
def calculate_depth(depth_img, image_width, image_height):
    # Get the dimensions of the image
    true_depth_img = np.zeros(
        (
            image_height,
            image_width,
        )
    )
    rows, cols, channels = depth_img.shape
    # Loop through each pixel in the depth_img
    for row in range(rows):
        for col in range(cols):
            # Get the RGB values of the current pixel
            pixel = depth_img[row, col]

            # Calculate the true depth value based on the RGB values
            # The formula used here is specific to the way depth is encoded in the RGB values
            true_depth_value = 1000 * (pixel[0] + pixel[1] * 256 + pixel[2] * 256 * 256) / (256 * 256 * 256 - 1)

            # Assign the true depth value to the corresponding position in the true depth image
            true_depth_img[row, col] = true_depth_value

    # Return the true depth image
    return true_depth_img


def merge_gt_pointclouds(lidar_pcd, depth_pcd):
    """
    This function merges lidar point cloud and depth point cloud.
    It also down samples the merged point cloud for voxelization.
    """

    # Initialize lists to store new points and labels
    newpoints = []
    newlabels = []

    # Extract the coordinates (first three columns) from the lidar point cloud and add them to the newpoints list
    newpoints.extend(np.asarray(lidar_pcd[:, :3]))
    logging.debug(f"Amount of lidar points: {len(newpoints)}")

    # Extract the coordinates (first three columns) from the depth point cloud and add them to the newpoints list
    newpoints.extend(np.asarray(depth_pcd[:, :3]))

    # Extract the labels (last column) from the lidar point cloud and add them to the newlabels list
    newlabels.extend(np.asarray(lidar_pcd[:, -1:]))

    # Extract the labels (last column) from the depth point cloud and add them to the newlabels list
    newlabels.extend(np.asarray(depth_pcd[:, -1:]))

    # Combine the new points and labels into a single array
    new_pcd = np.concatenate([newpoints, newlabels], axis=1)

    # Return the merged point cloud
    return new_pcd


def voxelize_one(merged_pcd):
    """
    This function takes a merged point cloud and voxelizes it.
    It first calculates the offsets in the x and z directions.
    Then, it applies a voxel filter to the merged point cloud.
    Finally, it concatenates the voxel points and semantics into a single array and returns it.
    """

    # Calculate the offset in the x direction
    offset_x = BEV_OFFSET_FORWARD_YC * BEV_RESOLUTION_YC

    # Calculate the offset in the z direction
    offset_z = OFFSET_Z_YC * VOXEL_RESOLUTION_YC

    # Apply a voxel filter to the merged point cloud
    voxel_points, semantics = voxel_filter(
        merged_pcd,  # The merged point cloud
        VOXEL_RESOLUTION_YC,  # The voxel resolution
        VOXEL_SIZE_YC,  # The voxel size
        [offset_x, 0, offset_z],  # The offset
    )

    # Concatenate the voxel points and semantics into a single array
    data = np.concatenate([voxel_points, semantics], axis=1)

    # Return the voxelized point cloud data
    return data


def voxel_filter(pcloud, voxel_resolution, voxel_size, offset):
    """
    This function applies a voxel filter to a point cloud.
    It first calculates the offsets in the x, y, and z directions.
    Then, it applies a voxel filter to the point cloud.
    Finally, it concatenates the voxel points and semantics into a single array and returns it.

    """
    # Split the point cloud into coordinates and semantics
    pcd, sem = pcloud[:, :3], pcloud[:, -1:]

    # Convert voxel size and offset to numpy arrays
    voxel_size, offset = np.asarray(voxel_size), np.asarray(offset)

    # Adjust the offset based on voxel resolution and size
    offset += voxel_resolution * voxel_size / 2

    # Adjust the point cloud based on the offset
    pcd_b = pcd + offset

    # Create a mask for points within the voxel grid
    idx = ((0 <= pcd_b) & (pcd_b < voxel_size * voxel_resolution)).all(axis=1)

    # Apply the mask to the point cloud and semantics
    pcd_b, sem_b = pcd_b[idx], sem[idx]

    # Compute index for every point in a voxel
    Dx, Dy, Dz = voxel_size
    hxyz, hmod = np.divmod(pcd_b, voxel_resolution)
    h = hxyz[:, 0] + hxyz[:, 1] * Dx + hxyz[:, 2] * Dx * Dy

    # Sort the indices based on h
    h_idx = np.argsort(h)
    h, hxyz, sem_b, pcd_b, hmod = h[h_idx], hxyz[h_idx], sem_b[h_idx], pcd_b[h_idx], hmod[h_idx]

    # Get unique values of h and their indices
    h_n, indices = np.unique(h, return_index=True)

    # Initialize arrays for voxels and semantics
    n_f = h_n.shape[0]
    voxels = np.zeros((n_f, 3), dtype=np.uint16)
    semantics = np.zeros((n_f, 1), dtype=np.uint8)

    # Define the road index
    road_idx = road_idx = get_label_attributes("color", (157, 234, 50), "id")

    # Loop over each unique value of h
    for i in range(n_f):
        # Get the indices for the current value of h
        idx_ = np.arange(indices[i], indices[i + 1]) if i < n_f - 1 else np.arange(indices[i], h.shape[0])

        # Calculate the distance for each point in the voxel
        dis = np.sum(hmod[idx_] ** 2, axis=1)

        # Determine the semantic label for the voxel
        semantic = sem_b[idx_][np.argmin(dis)] if not np.isin(sem_b[idx_], road_idx).any() else road_idx

        # Assign the voxel coordinates and semantic label
        voxels[i] = hxyz[idx_][0]
        semantics[i] = semantic

    # Return the voxelized point cloud data
    return voxels, semantics


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- MAIN ------------------------------------------------------------------------------------------------------
# ======================================================================================================================


def main():
    if len(sys.argv) != 2:
        logging.info("Usage: python3 main.py <input_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    for input_folder in input_folder:
        logging.info(f"{Fore.YELLOW}Starting getting file_paths ...{Style.RESET_ALL}")
        file_paths = get_file_paths(input_folder)
        print('file_paths', len(file_paths))

        logging.info(f"{Fore.GREEN}Finished getting file_paths{Style.RESET_ALL}")

        logging.info(f"{Fore.YELLOW}Starting generating data ...{Style.RESET_ALL}")

        # Process files in parallel with a specified number of processes
        process_files_parallel(file_paths, num_processes=20)
        logging.info(f"{Fore.GREEN}Finished{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

# endregion
# ======================================================================================================================
