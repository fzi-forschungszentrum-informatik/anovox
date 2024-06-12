import numpy as np
import open3d as o3d
import argparse
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
import plotly.graph_objects as go

bev_offset_forward = 0 # in px
bev_resolution = 0.2
offset_z = 0 # in px

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

def merge_preds_to_points(preds, points):
    preds = np.load(preds).reshape(-1,1)
    #print(preds)
    pcd = o3d.io.read_point_cloud(points)
    points = np.asarray(pcd.points)
    point_preds = np.concatenate([points, preds], axis=1)
    return point_preds

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def main(args):
    occured_classes = []
    global color_map
    scores_data = sorted(os.listdir(args.scores_dir))
    #color_map = [[color[0]/255, color[1]/255, color[2]/255] for color in color_map]
    #color_map_hex = [rgb_to_hex(color) for color in color_map]

    if args.datatype == 'pointcloud':
        points_data = collect_anovox_files(dataset_path=args.dataset_path, datatype='PCD')
        assert len(points_data) == len(scores_data), "number of depth images does not match with number of score files"

        for i, score_file in enumerate(tqdm(scores_data)):
            score_file = os.path.join(args.scores_dir, score_file)
            anovox_pcd = points_data[i]
            pointcloud = merge_preds_to_points(score_file, anovox_pcd)

            x = pointcloud[:, 0]
            y = pointcloud[:, 1]
            z = pointcloud[:, 2]

            # Create the plot
            uncertainty = pointcloud[:, 3]

            global_range = [min(np.min(x), np.min(y), np.min(z)), max(np.max(x), np.max(y), np.max(z))]
            
            trace = go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode='markers',
                marker=dict(
                    color = uncertainty,
                    colorscale='Viridis',
                    size=2,
                    opacity=0.8,
                    colorbar=dict(title='Uncertainty')  # add a colorbar with title
                ),
            )

            fig = go.Figure(data=[trace])

            fig.update_layout(
                scene=dict(
                    xaxis=dict(range=global_range),
                    yaxis=dict(range=global_range),
                    zaxis=dict(range=global_range),
                    aspectmode='cube'
                )
            )

            # Save the plot
            fig.write_html('output_vis/output_uncert_{}.html'.format(i))
        
        print(occured_classes)

    else:
        raise NameError('No data type selected. Choose between --images and --pointclouds')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OOD Evaluation')

    parser.add_argument('--dataset_path', type=str, # default='<...>/Anomaly_Datasets/AnoVox',
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
    main(args)

