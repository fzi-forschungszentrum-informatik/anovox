"""this code orchestrates the generation and processing of sensor data, including lidar and camera data,
for a simulated scenario. It involves callbacks for different sensor types, data relabeling, and various coordinate
transformations to produce and save sensor data in different formats."""
import logging

import numpy as np

import Definitions
from EgoVehicleSetup import SEMANTIC_CAM_TYPE, SEMANTIC_LIDAR_TYPE, INSTANCE_CAM_TYPE
from FileStructureManager import create_file_name
from Models.Models import FrameData


# ======================================================================================================================
# region -- GENERATE DATA ----------------------------------------------------------------------------------------------
# ======================================================================================================================
def generate_data(
        scenario_id,
        frame_id,
        sensor_callbacks,
        sensor_transforms,
        id_labels,
        tick_count,
        anomaly_type
):
    """
    Generate data for a given scenario and frame.
    """
    logging.debug("Start Generating Data")

    frame_data = FrameData(frame_id, scenario_id)
    logging.debug(f"Frame Number: {frame_data.frame_id}")

    # unpack sensor callbacks
    for sensor_callback_dict in sensor_callbacks:
        logging.debug(f'Generating Data for Sensor Type: {sensor_callback_dict["sensor"]}')
        try:
            sensor_callback_dict["callback"](frame_data)
            logging.debug("Data Generation Successful")
        except Exception as e:
            logging.error(
                "Exception while generating raw sensor data\n%s",
                e,
            )
            return

    for location_rotation in sensor_transforms:
        camera_transform = sensor_transforms[location_rotation]['camera']
        lidar_transform = sensor_transforms[location_rotation]['lidar']

        # unpack transformation matrices for the sensors
        camera_transform_inverse = camera_transform.get_inverse_matrix()
        lidar_transform = lidar_transform.get_matrix()

        semantic_img_arr = frame_data.sensor_data[location_rotation][SEMANTIC_CAM_TYPE]['data']

        semantic_pcd = None
        for label in id_labels:
            pcd_mask = get_lidar_mask(
                label.instance_id,
                frame_data.sensor_data[location_rotation][SEMANTIC_LIDAR_TYPE]['point_ids']
            )
            semantic_img_arr = relabel_semantic_img(
                semantic_img_arr,
                frame_data.sensor_data[location_rotation][INSTANCE_CAM_TYPE]['data'],
                pcd_mask,
                camera_transform_inverse,
                lidar_transform,
                label.semantic_id,
                tick_count,
                label.label_type,
                anomaly_type
            )
            semantic_pcd = relabel_pcd(
                frame_data.sensor_data[location_rotation][SEMANTIC_LIDAR_TYPE]['data'],
                frame_data.sensor_data[location_rotation][SEMANTIC_LIDAR_TYPE]['point_ids'],
                label.instance_id,
                label.semantic_id,
                tick_count
            )
        frame_data.sensor_data[location_rotation][SEMANTIC_CAM_TYPE]['data'] = semantic_img_arr
        frame_data.sensor_data[location_rotation][SEMANTIC_LIDAR_TYPE]['point_ids'] = semantic_pcd
    frame_data.save_files()

    logging.debug("Data Generation Successful")
    return frame_data


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- CALLBACK_FUNCTIONS -----------------------------------------------------------------------------------------
# ======================================================================================================================


def image_callback(
        frame_data: FrameData, data_queue, sensor_name, file_ending, dataformat, sensor_type, location, rotation,
        save_data
):
    """
    This method, `image_callback`, is used to process image data received from a frame.
    """
    file_path = create_file_name(
        frame_data.frame_id,
        frame_data.scenario_id,
        sensor_name,
        file_ending,
        run_makedirs=save_data
    )
    image = data_queue.get()
    if save_data:
        image.save_to_disk(file_path)
    # array of bgra pixel
    pixel_array = np.reshape(image.raw_data, (image.height, image.width, 4), )[:, :, :3][:, :,
                  ::-1]  # remove alpha channel and reverse order of channels to rgb

    if sensor_type == SEMANTIC_CAM_TYPE:
        pixel_array = pixel_array[:, :, 0]  # only first channel used to store semantic labels
    frame_data.set_data(file_path, pixel_array, sensor_type, location, rotation, save_data)


def lidar_callback(
        frame_data: FrameData, data_queue, sensor_name, file_ending, dataformat, sensor_type, location, rotation,
        save_data
):
    """
    Callback method for lidar data.
    """
    logging.debug("Lidar callback called")
    logging.debug(data_queue.qsize())

    point_cloud = data_queue.get()
    data = np.frombuffer(
        point_cloud.raw_data,
        dtype=np.dtype(
            [
                ("x", np.float32),
                ("y", np.float32),
                ("z", np.float32),
                ("intensity", np.float32),
            ]
        ),
    )

    # negate y for correct open3d coordinate system
    points = np.array([data["x"], -data["y"], data["z"]]).T
    intensities = np.array(data["intensity"]).reshape(-1, 1)
    pcd = np.concatenate([points, intensities], axis=1)
    file_path = create_file_name(
        frame_data.frame_id,
        frame_data.scenario_id,
        sensor_name,
        file_ending,
        run_makedirs=save_data
    )
    frame_data.set_data(file_path, pcd, sensor_type, location, rotation, save_data)


def semantic_lidar_callback(
        frame_data: FrameData, data_queue, sensor_name, file_ending, dataformat, sensor_type, location, rotation,
        save_data
):
    """
    Callback method that processes the semantic lidar data.
    """
    logging.debug(data_queue.qsize())

    point_cloud = data_queue.get()
    data = np.frombuffer(
        point_cloud.raw_data,
        dtype=np.dtype(
            [
                ("x", np.float32),
                ("y", np.float32),
                ("z", np.float32),
                ("CosAngle", np.float32),
                ("ObjIdx", np.uint32),
                ("ObjTag", np.uint32),
            ]
        ),
    )

    # We're negating the y to correctly visualize a world that matches
    # what we see in Unreal since Open3D uses a right-handed coordinate system
    points = np.array([data["x"], -data["y"], data["z"]]).T

    # Colorize the point cloud based on the City-Scape color palette
    ids = np.array(data["ObjIdx"]).reshape(-1, 1)
    labels = np.array(data["ObjTag"]).reshape(-1, 1)  # semantic ids for every class found in pcd
    point_ids = np.concatenate([points, ids], axis=1)  # instance ids for every object found in pcd
    semantic_pcd = np.concatenate([points, labels], axis=1)

    file_path = create_file_name(
        frame_data.frame_id,
        frame_data.scenario_id,
        sensor_name,
        file_ending,
        run_makedirs=save_data
    )

    frame_data.set_data(
        file_path,
        semantic_pcd,
        sensor_type,
        location,
        rotation,
        save_data
    )
    frame_data.set_point_ids(point_ids, location, rotation)


# endregion
# ======================================================================================================================


# ======================================================================================================================
# region -- RELABELING -------------------------------------------------------------------------------------------------
# ======================================================================================================================


def get_lidar_mask(object_id, lidar_data):
    """
    This method takes in an object ID and lidar data as parameters. It creates a lidar mask by filtering the lidar
    points based on the given object ID and removing any anomaly points. The * method returns the lidar points that
    pass the mask.
    """
    lidar_points = np.array(lidar_data[:, :3])
    idx = lidar_data[:, 3:]
    id_mask = np.isin(idx, [object_id])
    id_mask = id_mask.reshape(
        id_mask.size,
    )
    id_mask = np.logical_not(id_mask)  # only anomaly points have true boolean value in this array
    masked_lidar_points = np.delete(lidar_points, id_mask, axis=0)

    return masked_lidar_points


def relabel_pcd(
        semantic_pcd,
        instance_pcd_data,
        instance_id,
        new_label,
        tick_count
):
    """
    Relabels the instances in the semantic point cloud data with new labels.
    """
    pcd_points = semantic_pcd[:, :3]
    pcd_labels = semantic_pcd[:, -1:]
    idx = instance_pcd_data[:, -1:]
    id_mask = np.isin(idx, instance_id)
    id_mask = id_mask.reshape((id_mask.size,))
    pcd_labels[id_mask] = new_label
    new_pcd = np.concatenate([pcd_points, pcd_labels], axis=1)
    return new_pcd


def relabel_semantic_img(
        camera_data,
        instance_data,
        pcd_mask,
        camera_inverse_trans,
        lidar_trans,
        new_color,
        tick_count,
        label_type,
        anomaly_type
):
    """
    Relabels the semantic image based on the lidar data and camera parameters.
    """
    camera_data = np.copy(camera_data)  # for some reason this doesn't work without copying the image array
    instance_data = np.copy(instance_data)
    camera_matrix = np.identity(3)  # calibration matrix for camera
    camera_matrix[0, 0] = camera_matrix[1, 1] = Definitions.FOCAL
    camera_matrix[0, 2] = Definitions.IMAGE_WIDTH / 2.0
    camera_matrix[1, 2] = Definitions.IMAGE_HEIGHT / 2.0

    local_points = pcd_mask.T
    # Add an extra 1.0 at the end of each 3d point, so it becomes of
    # shape (4, p_cloud_size) and it can be multiplied by a (4, 4) matrix.
    local_points = np.r_[
        local_points,
        [np.ones(local_points.shape[1])],
    ]

    # Transform the points from lidar space to world space.
    world_points = np.dot(lidar_trans, local_points)

    # This (4, 4) matrix transforms the points from world to sensor coordinates.
    world_2_camera = np.array(camera_inverse_trans)

    # Transform the points from world space to camera space.
    sensor_points = np.dot(world_2_camera, world_points)

    # Now we must change from UE4's coordinate system to a "standard"
    # camera coordinate system (the same used by OpenCV):

    # ^ z                       . z
    # |                        /
    # |              to:      +-------> x
    # | . x                   |
    # |/                      |
    # +-------> y             v y

    # This can be achieved by multiplying by the following matrix:
    # [[ 0,  1,  0 ],
    #  [ 0,  0, -1 ],
    #  [ 1,  0,  0 ]]

    # Or, in this case, is the same as swapping:
    # (x, y ,z) -> (y, -z, x)
    point_in_camera_coords = np.array(
        [
            sensor_points[1] * -1,
            sensor_points[2] * -1,
            sensor_points[0],
        ]
    )

    # Finally we can use our K matrix to do the actual 3D -> 2D.
    points_2d = np.dot(camera_matrix, point_in_camera_coords)

    # Remember to normalize the x, y values by the 3rd value.
    points_2d = np.array(
        [
            points_2d[0, :] / points_2d[2, :],
            points_2d[1, :] / points_2d[2, :],
            points_2d[2, :],
        ]
    )

    # At this point, points_2d[0, :] contains all the x and points_2d[1, :]
    # contains all the y values of our points. In order to properly
    # visualize everything on a screen, the points that are out of the screen
    # must be discarded, the same with points behind the camera projection plane.
    # print("points 2d shape before",points_2d.shape)
    points_2d = points_2d.T
    points_in_canvas_mask = (
            (points_2d[:, 0] > 0.0)
            & (points_2d[:, 0] < Definitions.IMAGE_WIDTH)
            & (points_2d[:, 1] > 0.0)
            & (points_2d[:, 1] < Definitions.IMAGE_HEIGHT)
            & (points_2d[:, 2] > 0.0)
    )
    points_2d = points_2d[points_in_canvas_mask]

    # Extract the screen coords (uv) as integers.
    u_coord = points_2d[:, 0].astype(np.int32)
    v_coord = points_2d[:, 1].astype(np.int32)

    instance_pixels = instance_data[v_coord, u_coord]

    if instance_pixels.size == 0:  # if no target pixels were found
        return camera_data
    instance_id, counts = np.unique(
        instance_pixels,
        return_counts=True,
        axis=0,
    )
    # get the instance color of the segment in the image that has most of the projected lidar points in it
    instance_id = instance_id[counts.argmax()]
    instance_id = np.squeeze(instance_id)
    logging.debug(f"anomaly instance color: {instance_id}")

    _anomaly_mask = np.all(
        instance_data == instance_id,
        axis=-1,
    )  # get all pixels with the anomaly id color

    camera_data[_anomaly_mask] = new_color

    return camera_data

# endregion
# ======================================================================================================================
