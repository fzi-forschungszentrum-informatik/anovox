import numpy as np
import open3d as o3d
import sys
import argparse
from numba import jit
import os
from PIL import Image
from tqdm import tqdm
from scipy import stats



bev_offset_forward = 0 # in px
bev_resolution = 0.2
offset_z = 0 # in px

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



def check_file_ending(path):
    file_ending = path.split(".")[-1]
    print("     ending", file_ending)
    return file_ending == "npy"


def collect_anovox_files(dataset_path, datatype):
    if datatype not in ['DEPTH_IMG', 'SEMANTIC_PCD', 'PCD']:
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


def transform_to_pcd(scores, depths, camera_fov, mask=None):
    height, width = depths.shape

    # camera_fov = args.camera_fov
    focal = width / (2.0 * np.tan(camera_fov * np.pi / 360.0))

    # In this case Fx and Fy are the same since the pixel aspect
    # ratio is 1
    cx = width / 2.0  # from camera projection matrix
    cy = height / 2.0

    # voxel_size = args.voxel_size

    point_list = []
    anomaly_score_list = []

    for i in range(height):
        for j in range(width):
            z = depths[i,j]
            if mask is not None and not mask[i][j]:
                continue
            anomaly_score = scores[i][j]
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
            # red, green, blue = (
            #     semantic_color[0],
            #     semantic_color[1],
            #     semantic_color[2],
            # )
            # point_color = [
            #     i / 255.0 for i in [red, green, blue]
            # ]  # format to o3d color values
            anomaly_score_list.append(anomaly_score)

    depth_pcloud = o3d.geometry.PointCloud()  # create point cloud object
    depth_pcloud.points = o3d.utility.Vector3dVector(
        point_list
    )  # set pcd_np as the point cloud points
    # depth_pcloud.colors = o3d.utility.Vector3dVector(color_list)
    # point cloud needs to be rotated to fit with lidar point cloud in the future
    r_matrix = depth_pcloud.get_rotation_matrix_from_xyz(
        (-np.pi / 2, np.pi / 2, 0)
    )  # rotation matrix
    depth_pcloud.rotate(
        r_matrix, center=(0, 0, 0)
    )  # rotate depth point cloud to fit lidar point cloud
    # o3d.visualization.draw_geometries([depth_pcloud])
    depth_points = np.asarray(depth_pcloud.points)
    anomaly_score_list = np.asarray(anomaly_score_list) # + 1
    # print(np.amin(anomaly_score_list))
    # print(np.amax(anomaly_score_list))
    anomaly_score_list = anomaly_score_list.reshape(-1,1) # np.reshape(np.array(anomaly_score_list), (len(anomaly_score_list), 1))

    voxel_colors = np.c_[anomaly_score_list, np.zeros((anomaly_score_list.size,2))]
    depth_pcloud.colors = o3d.utility.Vector3dVector(voxel_colors)
    #o3d.visualization.draw_geometries([depth_pcloud])
    return np.concatenate([depth_points, anomaly_score_list], axis=1)


def transform_pcd_o3d(depth_img_path, eval_img):
    # depth_img_pil = Image.open(depth_img_path)
    # height, width = depth_img_pil.height, depth_img_pil.width

    depth_img_array = np.load(depth_img_path)
    # depth_img_array = depth_img_array.astype(np.uint16)
    height, width = depth_img_array.shape
    print("dtype:", depth_img_array.dtype)
    # depth_img = o3d.io.read_image(depth_img_path)
    depth_img = o3d.geometry.Image(depth_img_array)


    camera_fov = args.camera_fov
    focal = width / (2.0 * np.tan(camera_fov * np.pi / 360.0))

    # In this case Fx and Fy are the same since the pixel aspect
    # ratio is 1
    cx = width / 2.0  # from camera projection matrix
    cy = height / 2.0

    intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, focal,focal, cx, cy)
    intrinsic.intrinsic_matrix = [[focal, 0, cx], [0, focal, cy], [0, 0, 1]]
    cam = o3d.camera.PinholeCameraParameters()
    cam.intrinsic = intrinsic

    # pcloud = o3d.geometry.PointCloud()
    #o3d.visualization.draw_geometries([depth_img])


    # cam.extrinsic = np.array([[0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 0., 0.], [0., 0., 0., 1.]])
    pcloud = o3d.geometry.PointCloud().create_from_depth_image(depth_img, cam.intrinsic)
    print(pcloud)
    #o3d.visualization.draw_geometries([pcloud])





def img2pcd(score_img, depth_img, mask, camera_fov, depth_preds:bool=False):
    eval_image = np.load(score_img)
    if depth_preds:
        depth_img_array = np.load(depth_img)
        pcloud = transform_to_pcd(eval_image, depth_img_array,  mask)
        # depth_img_ = o3d.io.read_image(depth_img)
        # transform_pcd_o3d(depth_img, eval_image)

    else:
        depth_img = Image.open(depth_img)

        depth_img_array = calculate_carla_depth(np.array(depth_img), np.zeros((depth_img.height, depth_img.width,)),
                                            depth_img.height, depth_img.width)

        pcloud = transform_to_pcd(eval_image, depth_img_array, camera_fov, mask)

    file_name = "image_voxel_scores" + os.path.basename(str(score_img))

    return pcloud, file_name





def voxelize_one(pcloud, save_name, voxel_resolution, voxel_grid_size, score_func='centerpoint'):
    offset_x = bev_offset_forward * bev_resolution
    offset_z = 0
    voxel_points, semantics = voxel_filter(pcloud, voxel_resolution, voxel_grid_size, [offset_x, 0, offset_z], score_func)
    data = np.concatenate([voxel_points, semantics], axis=1) # [:, None]
    np.save(f'{save_name}', data)
    return data
    # np.save(f'{save_path}/voxel_coo/voxel_coo_{name}.npy', csr_voxels)


def voxel_filter(pcloud, voxel_resolution, grid_size, offset, score_func):
    pcd = pcloud[:, :3]
    sem = pcloud[:, -1]
    grid_size = np.asarray(grid_size)
    offset = np.asarray(offset)
    offset += voxel_resolution * grid_size / 2
    pcd_b = pcd + offset
    idx = ((0 <= pcd_b) & (pcd_b < grid_size * voxel_resolution)).all(axis=1)
    pcd_b, sem_b = pcd_b[idx], sem[idx] # limit point cloud to voxel grid size

    Dx, Dy, Dz = grid_size
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
    semantics = np.zeros((n_f,1), dtype=np.float64)
    # points_f = np.zeros((n_f, 3))
    # road_idx = np.where((COLOR_PALETTE == (157, 234, 50)).all(axis = 1))[0][0] # roadline 24u
    # road_idx = np.where(LABEL_CLASS == 'roadlines')[0][0]
    # voxels = []
    # semantics = []
    # points_f = []
    for i in range(n_f):
        # idx_ = (h == h_n[i])
        idx_ = np.arange(indices[i], indices[i+1]) if i < n_f - 1 else np.arange(indices[i], n_all)
        if score_func=='centerpoint':
            dis = np.sum(hmod[idx_] ** 2, axis=1)
            # voxel_score = sem_b[idx_][np.argmin(dis)]  # if not np.isin(sem_b[idx_], road_idx).any() else road_idx
            # voxel_score = np.bincount(sem_b.squeeze()[idx_]).argmax()
            voxel_score = sem_b[idx_][np.argmin(dis)] # if not np.isin(sem_b[idx_], road_idx).any() else road_idx
        elif score_func=='mean':
            voxel_score = np.mean(sem_b[idx_])
        elif score_func=='median':
            voxel_score = np.median(sem_b[idx_])

        # semantic = sem_b[idx_][np.argmin(dis)]  # if not np.isin(sem_b[idx_], road_idx).any() else road_idx
        # semantic = np.bincount(sem_b.squeeze()[idx_]).argmax() if not np.isin(sem_b[idx_], road_idx).any() else road_idx
        voxels[i] = hxyz[idx_][0]
        semantics[i] = voxel_score
        # points_f[i][2] += center[2] / 2
        # voxels.append(hxyz[idx_][0])
        # semantics.append(semantic)
        # points_f.append(pcd_b[idx_].mean(axis=0) - center)
    # debug_set, counts = np.unique(semantics, return_counts=True)
    return voxels, semantics

def merge_preds_to_points(preds, points):
    preds = np.load(preds).reshape(-1,1)
    pcd = o3d.io.read_point_cloud(points)
    points = np.asarray(pcd.points)
    point_preds = np.concatenate([points, preds], axis=1)
    return point_preds


def main(args):
    # depth_img_dir = os.path.join(args.dataset_path, 'DEPTH_IMG')
    # scores_dir = '/home/tes_unreal/Desktop/BA/RbA/anomaly_scores/swin_b_1dl/anovox'

    scores_data = sorted(os.listdir(args.scores_dir))

    if os.path.exists(args.output_dir) == False:
        os.mkdir(args.output_dir)

    if args.datatype == 'image':
        fov = args.camera_fov
        if args.mask:
            mask = np.array(Image.open(args.mask))
        else:
            mask = None

        if args.depth_preds:
            depth_data = []
            for depth_pred in sorted(os.listdir(args.dataset_path)):
                depth_data.append(os.path.join(args.dataset_path, depth_pred))
        else:
            depth_data = collect_anovox_files(dataset_path=args.dataset_path, datatype='DEPTH_IMG')

        assert len(depth_data) == len(scores_data), "number of depth images does not match with number of score files"

        for i, score in enumerate(tqdm(scores_data)):
            score = os.path.join(args.scores_dir, score)
            depth_img = depth_data[i]
            image_point_cloud, file_name = img2pcd(score, depth_img, mask, fov)
            file_path = os.path.join(args.output_dir, file_name)

            grid = voxelize_one(image_point_cloud, file_path, args.voxel_resolution, args.voxel_grid_size)

    elif args.datatype == 'pointcloud':
        points_data = collect_anovox_files(dataset_path=args.dataset_path, datatype='PCD')
        assert len(points_data) == len(scores_data), "number of depth images does not match with number of score files"

        for i, score_file in enumerate(tqdm(scores_data)):
            score_file = os.path.join(args.scores_dir, score_file)
            anovox_pcd = points_data[i]
            pointcloud = merge_preds_to_points(score_file, anovox_pcd)
            file_name = "pcd_voxel_scores_{}.npy".format(str(i).rjust(6,'0'))
            file_path = os.path.join(args.output_dir, file_name)
            voxelize_one(pointcloud, file_path, args.voxel_resolution, args.voxel_grid_size, args.score_function)

    else:
        raise NameError('No data type selected. Choose between --images and --pointclouds')

    # output_path = '/home/tes_unreal/Desktop/BA/RbA/voxelpreds'





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OOD Evaluation')

    parser.add_argument('--dataset_path', type=str, # default='/home/lukasnroessler/Anomaly_Datasets/AnoVox',
                        help=""""path to anovox dataset""")

    parser.add_argument('--camera_fov', type=float, default=90.0,
                        help=""""Value for camera field of view""")

    parser.add_argument('--voxel_resolution', type=float, default=0.5,
                        help=""""size for a single voxel""")

    parser.add_argument('--voxel_grid_size', default=[1000,1000,64],
                        help="""world size in [x,y,z] format""")

    parser.add_argument('--depth_preds', default=False, action='store_true',
                        help="""""set true for separate depth prediction instead of carla ground truth""")

    parser.add_argument('--scores_dir', type=str, #default='scores/scores_softmax_2dummy_1_01_final_latest',
                        help="""directory where anomaly scores are stored. Files should be ordered after anovox frame id (number after data file)""")

    parser.add_argument('--output_dir', type=str, default='voxelpreds',
                        help="""directory where anomaly scores are stored. Files should be ordered after anovox frame id (number after data file)""")

    parser.add_argument('--mask', type=str, # default='roi.png',
                        help="""path of image to mask region of interest""")

    # subparser?
    parser.add_argument('--score_function', type=str, choices=["mean", "median", "centerpoint"], default="centerpoint",
                        help=""""determines, how the anomaly score for a single voxel is calculated. Choose between mean, median of all points in voxel, or anomaly score of the point closest to voxel center""")

    parser.add_argument('--datatype', type=str, choices=["image", "pointcloud"],
                        help=""""type of data that voxel grids were created from""")



    args = parser.parse_args()

    print("STARTING VOXELIZATION OF SCORES FOR {}".format((args.datatype).upper()))
    main(args)
    print("VOXEL SCORES STORED IN {}".format(args.output_dir))

