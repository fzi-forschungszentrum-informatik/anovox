import sys
import open3d as o3d
import numpy as np

voxel_resolution = 0.5


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
                (245, 0, 0),    # home          =  29u
                (255, 36, 0),       # animal        =  30u
                (224, 17, 95),      # nature        =  31u
                (184, 15, 10),      # special       =  32u
                (245, 0, 0),        # airplane      =  33u
                (245, 0, 0),        # falling       =  34u
            ]
        )
)  # normalize each channel [0-1] since this is what Open3D uses

def check_file_ending(path):
    file_ending = path.split(".")[-1]
    print("     ending", file_ending)
    if file_ending == "npy":
        return True
    return False


def open_ply(file_path):
    try:
        o3d.visualization.draw_geometries([o3d.io.read_voxel_grid(file_path)])
    except Exception as e:
        print("Could not open file:", file_path)
        print(e)

# def open_npy(file_path):
#     voxel_array = np.load(file_path)
#     voxel_coors = voxel_array[:, :3]
#     voxel_colors = voxel_array[:, 3:]
#     print(voxel_coors)
#     print(voxel_colors)

def open_npy(file_path):
    try:
        voxel_data = np.load(file_path).astype(int)
        voxel_points = voxel_data[:,:3]
        voxel_colors = voxel_data[:,3:]
        unique_colors = np.unique(voxel_colors)
        print("voxel colors:", unique_colors)
        print("number of voxels:", voxel_colors.size)
        print("number of anomaly voxels:", np.count_nonzero((voxel_colors==29)))
        scores, counts = np.unique(voxel_colors, return_counts=True)
        if np.squeeze(voxel_colors).any() < 0:
            voxel_colors = voxel_data[:,3:] + 1
            voxel_colors = np.c_[voxel_colors, np.zeros((voxel_colors.size,2))]

        else :
            # voxel_colors[voxel_colors==29] = 33
            voxel_colors = np.squeeze(COLOR_PALETTE[voxel_colors]) / 255.0
        # print(voxel_colors)
        voxel_pcd = o3d.geometry.PointCloud()
        voxel_pcd.points = o3d.utility.Vector3dVector(voxel_points)
        voxel_pcd.colors = o3d.utility.Vector3dVector(voxel_colors)
        voxel_world = o3d.geometry.VoxelGrid.create_from_point_cloud(voxel_pcd, voxel_resolution)
        o3d.visualization.draw_geometries([voxel_world])
    except Exception as e:
        print("Could not open file:", file_path)
        print(e)

if __name__ == "__main__":
    inputs = sys.argv[1:]
    for input in inputs:
        print(f"## Opening {input} ##")
        if check_file_ending(input):
            open_npy(input)
        else:
           print("     --> wrong filetype")