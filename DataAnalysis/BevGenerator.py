"""This code orchestrates the generation and processing of bev data.
Adapted from https://github.com/zhejz/carla-roach/ CC-BY-NC 4.0 license,
and https://github.com/wayveai/mile MIT license."""

import logging

import cv2 as cv
import numpy as np

import Definitions
from FileStructureManager import create_file_name
from Models.Models import FrameData
from Models.World import World


# ======================================================================================================================
# region -- GENERATE DATA ----------------------------------------------------------------------------------------------
# ======================================================================================================================
def generate_data(
        scenario_id,
        frame_id
):
    """
    Generate data for a given scenario and frame.
    """
    logging.debug("Start Generating BEV")

    frame_data = FrameData(frame_id, scenario_id)
    logging.debug(f"Frame Number: {frame_data.frame_id}")

    frame_data.route_map = route_map()
    dataformat = Definitions.DataFormat.ROUTE_MAP
    file_path = create_file_name(
        frame_id=frame_data.frame_id,
        scenario_id=frame_data.scenario_id,
        subfolder=dataformat.name,
        file_ending=dataformat.value
    )

    frame_data.set_route_map(file_path, frame_data.route_map)
    frame_data.save_route_map()

    logging.debug("BEV Generation Successful")
    return frame_data


def route_map():
    """
    This method creates a black & white mask of the planned path of the ego vehicle.
    """
    ev_transform = World.WORLD_STATE.EGO_VEHICLE.get_transform()
    ev_loc = ev_transform.location
    ev_rot = ev_transform.rotation
    M_warp = _get_warp_transform(ev_loc, ev_rot)

    # Route Mask
    route_mask = np.zeros([Definitions.BEV_WIDTH, Definitions.BEV_WIDTH], dtype=np.uint8)
    route_in_pixel = np.array([[_world_to_pixel(wp.transform.location)]
                               for wp, _ in World.WORLD_STATE.EGO_VEHICLE_ROUTE])
    route_warped = cv.transform(route_in_pixel, M_warp)
    cv.polylines(route_mask, [np.round(route_warped).astype(np.int32)], False, 1, thickness=16)
    route_mask = route_mask.astype(bool)
    return route_mask


def _world_to_pixel(location, projective=False):
    """Converts the world coordinates to pixel coordinates"""
    x = Definitions.BEV_PIXELS_PER_METER * (location.x - World.WORLD_STATE.world_offset[0])
    y = Definitions.BEV_PIXELS_PER_METER * (location.y - World.WORLD_STATE.world_offset[1])

    if projective:
        p = np.array([x, y, 1], dtype=np.float32)
    else:
        p = np.array([x, y], dtype=np.float32)
    return p


def _get_warp_transform(ev_loc, ev_rot):
    """Calculates the affine transformation matrix from world coordinates to pixel coordinates."""
    ev_loc_in_px = _world_to_pixel(ev_loc)
    yaw = np.deg2rad(ev_rot.yaw)

    forward_vec = np.array([np.cos(yaw), np.sin(yaw)])
    right_vec = np.array([np.cos(yaw + 0.5 * np.pi), np.sin(yaw + 0.5 * np.pi)])

    bottom_left = ev_loc_in_px - Definitions.BEV_PIXELS_EV_TO_BOTTOM * forward_vec - (
            0.5 * Definitions.BEV_WIDTH) * right_vec
    top_left = ev_loc_in_px + (Definitions.BEV_WIDTH - Definitions.BEV_PIXELS_EV_TO_BOTTOM) * forward_vec - (
            0.5 * Definitions.BEV_WIDTH) * right_vec
    top_right = ev_loc_in_px + (Definitions.BEV_WIDTH - Definitions.BEV_PIXELS_EV_TO_BOTTOM) * forward_vec + (
            0.5 * Definitions.BEV_WIDTH) * right_vec

    src_pts = np.stack((bottom_left, top_left, top_right), axis=0).astype(np.float32)
    dst_pts = np.array([[0, Definitions.BEV_WIDTH - 1],
                        [0, 0],
                        [Definitions.BEV_WIDTH - 1, 0]], dtype=np.float32)
    return cv.getAffineTransform(src_pts, dst_pts)

# endregion
# ======================================================================================================================
