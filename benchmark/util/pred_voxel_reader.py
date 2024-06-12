import sys
import open3d as o3d
import numpy as np

voxel_resolution = 0.5

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

NORMALIZE_COLORS = True

def open_npy(file_path):
    try:
        voxel_pcd = o3d.geometry.PointCloud()

        voxel_data = np.load(file_path)
        voxel_points = voxel_data[:,:3]
        voxel_colors = voxel_data[:,3:] # + 1
        print("number of voxels:", voxel_colors.size)
        scores, counts = np.unique(voxel_colors, return_counts=True)        # voxel_colors = np.squeeze(Definitions.COLOR_PALETTE[voxel_colors]) / 255.0
        
        if NORMALIZE_COLORS:
            min_color = np.min(voxel_colors)
            max_color = np.max(voxel_colors)
            voxel_colors = (voxel_colors - min_color) / (max_color - min_color)
        
        voxel_colors = np.c_[voxel_colors, np.zeros((voxel_colors.size,2))]
        voxel_pcd.colors = o3d.utility.Vector3dVector(voxel_colors)
        voxel_pcd.points = o3d.utility.Vector3dVector(voxel_points)
        voxel_world = o3d.geometry.VoxelGrid.create_from_point_cloud(voxel_pcd, voxel_resolution)

        # Calculate the centroid of the voxel grid
        centroid = np.mean(voxel_points, axis=0)

        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(voxel_world)
        view_control = vis.get_view_control()
        view_control.set_lookat(centroid)  # Set the position of the camera to the centroid
        view_control.set_up([0, 0, 1])  # Set the up direction of the camera
        view_control.set_front([0, -1, 0])  # Set the front direction of the camera
        vis.run()
        vis.destroy_window()
        #o3d.visualization.draw_geometries([voxel_world])
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