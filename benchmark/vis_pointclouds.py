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

labels_text = {
  0: "unlabeled",
  1: "car",
  2: "bicycle",
  3: "motorcycle",
  4: "truck",
  5: "other-vehicle",
  6: "person",
  7: "traffic-sign", #"bicyclist",
  8: "motorcyclist",
  9: "road",
  10: "pole", #"parking",
  11: "sidewalk",
  12: "other-ground",
  13: "building",
  14: "fence",
  15: "vegetation",
  16: "terrain", #"trunk",
  #17: "terrain",
  #18: "pole",
  #19: "traffic-sign"
}

color_map = {
  0: [0, 0, 0],
  1: [128, 64, 128],
  2: [244, 35, 232],
  3: [70, 70, 70],
  4: [102, 102, 156],
  5: [190, 153, 153],
  6: [153, 153, 153],
  7: [250, 170, 30],
  8: [220, 220, 0],
  9: [107, 142, 35],
  10: [152, 251, 152],
  11: [70, 130, 180],
  12: [220, 20, 60],
  13: [255, 0, 0],
  14: [0, 0, 142],
  15: [0, 0, 70],
  16: [0, 60, 100],
  17: [0, 80, 100],
  18: [0, 0, 230],
  19: [119, 11, 32],
  20: [110, 190, 160],
  21: [170, 120, 50],
  22: [55, 90, 80],
  23: [45, 60, 150],
  24: [157, 234, 50],
  25: [81, 0, 81],
  26: [150, 100, 100],
  27: [230, 150, 140],
  28: [180, 165, 180],
  29: [250, 128, 114],
  30: [255, 36, 0],
  31: [224, 17, 95],
  33: [184, 15, 10],
  34: [245, 0, 0],
}

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

            #c = [color_map[int(label)] for label in pointcloud[:, 3]]
            #fig = plt.figure()
            #ax = fig.add_subplot(111, projection='3d')
            #ax.scatter(x, y, z, c=c, s=1)
            #plt.savefig('output_{}.png'.format(i))

            # Create the plot
            labels = pointcloud[:, 3]

            global_range = [min(np.min(x), np.min(y), np.min(z)), max(np.max(x), np.max(y), np.max(z))]
            
            data = []
            for label in set(labels):
                if int(label) not in occured_classes:
                    occured_classes.append(int(label))
                if int(label) == 0:
                    print("ANOMALY")
                    print(anovox_pcd)
                x_label = [x[i] for i in range(len(labels)) if labels[i] == label]
                y_label = [y[i] for i in range(len(labels)) if labels[i] == label]
                z_label = [z[i] for i in range(len(labels)) if labels[i] == label]
                trace = go.Scatter3d(
                    x=x_label,
                    y=y_label,
                    z=z_label,
                    mode='markers',
                    marker=dict(
                        size=2,
                        color='rgb' + str(tuple(color_map[int(label)])),  # use color from color_map
                        opacity=0.8
                    ),
                    name=str(labels_text[int(label)])
                )
                data.append(trace)

            fig = go.Figure(data=data)

            fig.update_layout(
                scene=dict(
                    xaxis=dict(range=global_range),
                    yaxis=dict(range=global_range),
                    zaxis=dict(range=global_range),
                    aspectmode='cube'
                )
            )

            # Save the plot
            fig.write_html('output_vis/output_{}.html'.format(i))
        
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

