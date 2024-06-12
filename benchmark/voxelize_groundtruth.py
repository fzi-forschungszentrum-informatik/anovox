import numpy as np
import open3d as o3d
from PIL import Image
import os
from tqdm import tqdm
import argparse
from numba import jit


bev_offset_forward = 0 # in px
bev_resolution = 0.2
offset_z_ = 0 # in px

COLOR_PALETTE = (
        np.array(
            [
                (0, 0, 0),          # unlabeled     =   0u
                (128, 64, 128),     # road          =   1u
                (244, 35, 232),     # sidewalk      =   2u
                (70, 70, 70),       # building      =   3u
                (102, 102, 156),    # wall          =   4u
                (190, 153, 153),    # fence         =   5u
                (153, 153, 153),    # pole          =   6u
                (250, 170, 30),     # traffic light =   7u
                (220, 220, 0),      # traffic sign  =   8u
                (107, 142, 35),     # vegetation    =   9u
                (152, 251, 152),    # terrain       =  10u
                (70, 130, 180),     # sky           =  11u
                (220, 20, 60),      # pedestrian    =  12u
                (255, 0, 0),        # rider         =  13u
                (0, 0, 142),        # Car           =  14u
                (0, 0, 70),         # truck         =  15u
                (0, 60, 100),       # bus           =  16u
                (0, 80, 100),       # train         =  17u
                (0, 0, 230),        # motorcycle    =  18u
                (119, 11, 32),      # bicycle       =  19u
                (110, 190, 160),    # static        =  20u
                (170, 120, 50),     # dynamic       =  21u
                (55, 90, 80),       # other         =  22u
                (45, 60, 150),      # water         =  23u
                (157, 234, 50),     # road line     =  24u
                (81, 0, 81),        # ground         = 25u
                (150, 100, 100),    # bridge        =  26u
                (230, 150, 140),    # rail track    =  27u
                (180, 165, 180),    # guard rail    =  28u
                (250, 128, 114),    # home          =  29u
                (255, 36, 0),       # animal        =  30u
                (224, 17, 95),      # nature        =  31u
                (184, 15, 10),      # special       =  32u
                (245, 0, 0),        # airplane      =  33u
                (245, 0, 0),        # falling       =  34u
            ]
        )
)


def collect_anovox_files(dataset_path, datatype):
    if datatype not in ['DEPTH_IMG', 'SEMANTIC_PCD', 'PCD', 'SEMANTIC_IMG']:
        raise NameError('data type {} does not exist'.format(datatype))

    file_list = []

    for scenario in os.listdir(dataset_path):
        if scenario == 'Scenario_Configuration_Files':
            continue
        data_dir = os.path.join(dataset_path, scenario, datatype)
        for image in os.listdir(data_dir):
            file_list.append(os.path.join(data_dir, image))

    def sorter(file_paths):
        identifier = (os.path.basename(file_paths).split('.')[0]).split('_')[-1]
        return int(identifier)
    file_list.sort(key=sorter)

    return file_list# [:5]



@jit(nopython=True)  # Compile the function with Numba
def calculate_carla_depth(depth_img, new_depth, height, width):
    # depth_img = Image.open(depth_img)
    depth_img_arr = new_depth
    # height, width, _  = depth_img_arr.shape
    # Get the dimensions of the image
    # depth_img_arr = np.zeros((depth_img.height, depth_img.width,))
    # Loop through each pixel in the depth_img
    for row in range(height):
        for col in range(width):
            pixel = depth_img[row, col]
            depth_img_arr[row, col] = 1000 * (pixel[0] + pixel[1] * 256 + pixel[2] * 256 * 256) / (
                256 * 256 * 256 - 1
            )
    return depth_img_arr


def img2pcd(score_img, depth_img, mask, camera_fov, depth_preds:bool=False):
    eval_image = np.array(Image.open(score_img))
    if depth_preds:
        depth_img_array = np.array(Image.open(depth_img))
        pcloud = transform_to_pcd(eval_image, depth_img_array, mask)
        # depth_img_ = o3d.io.read_image(depth_img)
        # transform_pcd_o3d(depth_img, eval_image)

    else:
        depth_img = Image.open(depth_img)

        depth_img_array = calculate_carla_depth(np.array(depth_img), np.zeros((depth_img.height, depth_img.width,)),
                                            depth_img.height, depth_img.width)

        pcloud = transform_to_pcd(eval_image, depth_img_array, camera_fov, mask)


    return pcloud

def transform_to_pcd(scores, depths, camera_fov, mask=None):
    if mask is not None:
        mask = np.asarray(Image.open(mask))
    height, width = depths.shape

    # camera_fov = args.camera_fov
    focal = width / (2.0 * np.tan(camera_fov * np.pi / 360.0))

    # In this case Fx and Fy are the same since the pixel aspect
    # ratio is 1
    cx = width / 2.0  # from camera projection matrix
    cy = height / 2.0

    # voxel_size = args.voxel_size

    point_list = []
    color_list = []

    for i in range(height):
        for j in range(width):
            z = depths[i,j]
            if mask is not None and not mask[i][j]:
                continue
            semantic_color = scores[i][j]
            # depth encoded in rgb values. For further information take a look at carla docs
            # depth_color[2] = B
            # depth_color[1] = G
            # depth_color[0] = R

            x, y = (j - cx) * z / focal, (i - cy) * z / focal
            coordinate = [x,y,z]

            if np.linalg.norm(coordinate) > 100:
                continue
            else:
                point_list.append(coordinate)
                red, green, blue = (
                    semantic_color[0],
                    semantic_color[1],
                    semantic_color[2],
                )
                point_color = [
                    i / 255.0 for i in [red, green, blue]
                ]  # format to o3d color values
                color_list.append(point_color)
    depth_pcloud = o3d.geometry.PointCloud()  # create point cloud object
    depth_pcloud.points = o3d.utility.Vector3dVector(
        point_list
    )  # set pcd_np as the point cloud points
    depth_pcloud.colors = o3d.utility.Vector3dVector(color_list)
    # o3d.visualization.draw_geometries([depth_pcloud])
    # point cloud needs to be rotated to fit with lidar point cloud in the future
    r_matrix = depth_pcloud.get_rotation_matrix_from_xyz(
        (-np.pi / 2, np.pi / 2, 0)
    )  # rotation matrix
    depth_pcloud.rotate(
        r_matrix, center=(0, 0, 0)
    )  # rotate depth point cloud to fit lidar point cloud
    return depth_pcloud


def voxelize_one(merged_pcd, save_name, voxel_resolution, grid_size):
    offset_x = bev_offset_forward * bev_resolution
    offset_z = offset_z_ * voxel_resolution
    voxel_points, semantics = voxel_filter(merged_pcd, voxel_resolution, grid_size, [offset_x, 0, offset_z])
    data = np.concatenate([voxel_points, semantics], axis=1) # [:, None]
    # voxels = np.zeros(shape=cfg.voxel_size, dtype=np.uint8)
    # voxels[voxel_points[:, 0], voxel_points[:, 1], voxel_points[:, 2]] = semantics
    # csr_voxels = sp.csr_matrix(voxels.reshape(voxels.shape[0], -1))
    np.save(f'{save_name}', data)
    # np.save(f'{save_path}/voxel_coo/voxel_coo_{name}.npy', csr_voxels)


def voxel_filter(pcloud, voxel_resolution, voxel_size, offset):
    pcd = np.asarray(pcloud.points)
    sem = (np.asarray(pcloud.colors) * 255.0).astype(np.uint8)
    new_sem = np.arange(len(sem))
    for i, value in enumerate(sem): #
        color_index = np.where((COLOR_PALETTE == value).all(axis = 1))
        # print(value)
        # for color in COLOR_PALETTE:
        #     if (value == color).all():
        #         new_sem[i] = np.where((COLOR_PALETTE == value))[0][0]
        # print(color_index)
        new_sem[i] = color_index[0][0]
    sem = new_sem
    # unique, counts = np.unique(sem, return_counts = True)
    # print(dict(zip(unique, counts)))
    voxel_size = np.asarray(voxel_size)
    offset = np.asarray(offset)
    offset += voxel_resolution * voxel_size / 2
    pcd_b = pcd + offset
    idx = ((0 <= pcd_b) & (pcd_b < voxel_size * voxel_resolution)).all(axis=1)
    pcd_b, sem_b = pcd_b[idx], sem[idx]

    Dx, Dy, Dz = voxel_size
    # compute index for every point in a voxel
    hxyz, hmod = np.divmod(pcd_b, voxel_resolution)
    h = hxyz[:, 0] + hxyz[:, 1] * Dx + hxyz[:, 2] * Dx * Dy

    # h_n = np.nonzero(np.bincount(h.astype(np.int32)))
    h_idx = np.argsort(h)
    h, hxyz, sem_b, pcd_b, hmod = h[h_idx], hxyz[h_idx], sem_b[h_idx], pcd_b[h_idx], hmod[h_idx]
    h_n, indices = np.unique(h, return_index=True)
    n_f = h_n.shape[0]
    n_all = h.shape[0]
    voxels = np.zeros((n_f, 3), dtype=np.uint16)
    semantics = np.zeros((n_f, 1), dtype=np.uint8)
    # points_f = np.zeros((n_f, 3))
    road_idx = np.where((COLOR_PALETTE == (157, 234, 50)).all(axis = 1))[0][0] # roadline 24u
    # road_idx = np.where(LABEL_CLASS == 'roadlines')[0][0]
    # voxels = []
    # semantics = []
    # points_f = []
    for i in range(n_f):
        # idx_ = (h == h_n[i])
        idx_ = np.arange(indices[i], indices[i+1]) if i < n_f - 1 else np.arange(indices[i], n_all)
        dis = np.sum(hmod[idx_] ** 2, axis=1)
        semantic = sem_b[idx_][np.argmin(dis)] if not np.isin(sem_b[idx_], road_idx).any() else road_idx
        # semantic = np.bincount(sem_b.squeeze()[idx_]).argmax() if not np.isin(sem_b[idx_], road_idx).any() else road_idx
        voxels[i] = hxyz[idx_][0]
        semantics[i] = semantic
        # points_f[i] = pcd_b[idx_].mean(axis=0) - center
        # points_f[i][2] += center[2] / 2
        # voxels.append(hxyz[idx_][0])
        # semantics.append(semantic)
        # points_f.append(pcd_b[idx_].mean(axis=0) - center)
    return voxels, semantics

def main(args):
    resolution, dataset = args.voxel_resolution, args.dataset_path
    # output_dir = '{dataset}_gt_voxels_resolution_{resolution}'.format(dataset=os.path.basename(dataset), resolution=resolution)
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if args.datatype == 'image':
        semantic_images = collect_anovox_files(dataset, 'SEMANTIC_IMG')
        depth_images = collect_anovox_files(dataset, 'DEPTH_IMG')
        for i, sem_img in enumerate(tqdm(semantic_images)):
            depth_img = depth_images[i]
            file_name = "image_voxel_gt_" + str(i).rjust(6,'0')
            file_path = os.path.join(output_dir, file_name)
            if args.mask:
                pcd = img2pcd(sem_img, depth_img, mask=args.mask, camera_fov=args.camera_fov)
            else:
                pcd = img2pcd(sem_img, depth_img, None, camera_fov=args.camera_fov)
            voxelize_one(pcd, file_path, resolution, args.grid_size)
    elif args.datatype == 'pointcloud':
        semantic_pointclouds = collect_anovox_files(dataset, 'SEMANTIC_PCD')
        for i, sem_pcd in enumerate(tqdm(semantic_pointclouds)):
            file_name = "image_voxel_gt_" + str(i)
            file_path = os.path.join(output_dir, file_name)
            sem_pcd = o3d.io.read_point_cloud(sem_pcd)
            # r_matrix = pcd.get_rotation_matrix_from_xyz(
            #     (-np.pi / 2, np.pi / 2, 0)
            # )  # rotation matrix
            # pcd.rotate(
            #     r_matrix, center=(0, 0, 0)
            # )  # rotate depth point cloud to fit lidar point cloud
            voxelize_one(sem_pcd, file_path, resolution, args.grid_size)
    else:
        raise NameError('data type does not exist')




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OOD Evaluation')

    parser.add_argument('--dataset_path', type=str, default='/home/lukasnroessler/Anomaly_Datasets/AnoVox',
                        help=""""path to anovox dataset""")

    parser.add_argument('--camera_fov', type=float, default=90.0,
                        help=""""Value for camera field of view""")

    parser.add_argument('--voxel_resolution', type=float, default=0.5,
                        help=""""size for a single voxel""")

    parser.add_argument('--grid_size', default=[1000,1000,64],
                        help="""world size in [x,y,z] format""")

    parser.add_argument('--output_dir', type=str, default='imagevoxels',
                        help="""directory where anomaly scores are stored. Files should be ordered after anovox frame id (number after data file)""")

    parser.add_argument('--mask', type=str, # default='roi.png',
                        help="""path of image to mask region of interest""")

    # subparser?
    parser.add_argument('--datatype', type=str, choices=['image', 'pointcloud'])





    args = parser.parse_args()


    print("VOXELIZING GROUND TRUTH VOXEL GRIDS FOR SENSOR {}".format((args.datatype).upper()))
    main(args)
    print("GROUND TRUTH VOXELS STORED AT {}".format(args.output_dir))