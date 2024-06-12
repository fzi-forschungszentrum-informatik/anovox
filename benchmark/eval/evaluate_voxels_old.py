import metrics
import csv
import numpy as np
import yaml
# from natsort import os_sorted
from collections import defaultdict
from tqdm import tqdm
from time import sleep
from PIL import Image
import argparse
import os
import shutil
from pathlib import Path
import random
from dataclasses import dataclass, field
import open3d as o3d




class Evaluator:
    def __init__(self) -> None:
        pass

def get_anomaly_attributes(scenario_root): # find name of object and size. CSV File in AnoVox is sideways
    csv_path = os.path.join(scenario_root, "ANOMALY")
    anomaly_csv = random.choice(os.listdir(csv_path))
    attributes = {}
    with open(os.path.join(csv_path, anomaly_csv)) as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        for attribute in reader:
            if attribute[0][:-1] == "anomaly_type_id":
                attributes["anomaly_type_id"] = attribute[1][1:]
            elif attribute[0][:-1] == "size":
                attributes["size"] = attribute[1][1:]
    return attributes


@dataclass # struct equivalent
class ScenarioData:

    anomaly_attributes: dict
    scenario_id: str # maybe unnecessary
    preds_total: field(default_factory=lambda: [])
    gts_total: field(default_factory=lambda: [])
    anormal_frame: field(default_factory=lambda: []) # store bool values for each frame


def collect_data(pred_dir, gts_dir, data_type):
    def sorter(file_path):
        if isinstance(file_path, tuple):
            file_path = file_path[0]
        identifier = (os.path.basename(file_path).split('.')[0]).split('_')[-1]
        return int(identifier)

    gt_grids = []


    scenario_dict = defaultdict(dict)
    for scenario in os.listdir(gts_dir):
        if scenario == 'Scenario_Configuration_Files':
            continue
        voxel_dir = os.path.join(gts_dir, scenario, 'VOXEL_GRID')
        for grid in os.listdir(voxel_dir):
            voxel_path = os.path.join(voxel_dir, grid)
            #gt_grids.append(os.path.join(voxel_dir, grid))
            if data_type == 'image':
                image_path = voxel_path.replace('VOXEL_GRID', 'SEMANTIC_IMG').replace('npy', 'png')
                # path_split = image_path.split('.')
                anomaly_found = anomaly_detectable_for_camera(image_path)
            elif data_type == 'pointcloud':
                pcd_path = voxel_path.replace('VOXEL_GRID', 'SEMANTIC_PCD').replace('npy', 'pcd')
                anomaly_found = anomaly_detectable_for_lidar(pcd_path)

            gt_grids.append((voxel_path, anomaly_found))

        attributes = get_anomaly_attributes(os.path.join(gts_dir, scenario))
        scenario_dict[scenario] = attributes




    gt_grids.sort(key=sorter)
    pred_root = pred_dir
    pred_grids = [os.path.join(pred_root, pred_grid) for pred_grid in os.listdir(pred_root)]
    pred_grids.sort(key=sorter)

    return pred_grids, gt_grids, scenario_dict


def anomaly_detectable_for_camera(semantic_image):
    image_array = np.array(Image.open(semantic_image))
    anomaly_color = [245,0,0]
    anomaly_in_image = (image_array==anomaly_color).all(-1).max()
    return anomaly_in_image

def anomaly_detectable_for_lidar(semantic_pcd):
    pcd = o3d.io.read_point_cloud(semantic_pcd)
    score_colors = np.asarray(pcd.colors) * 255.0
    score_colors = score_colors.astype(np.uint16)
    anomaly_color = [245,0,0]
    anomaly_in_pcd = (score_colors==anomaly_color).all(-1).max()
    return anomaly_in_pcd




destructure_dict = lambda dict, *args: (dict[arg] for arg in args)

def initialize_results_dict(scenario_dict: dict) -> dict:
    results_dict = {}
    for _, scenario_id in enumerate(scenario_dict.keys()):
        # results_dict[scenario_id] = {"results": [], "anomaly_attributes": {}, "results_anomaly": []}

        scenario_data = ScenarioData(
            anomaly_attributes=scenario_dict[scenario_id],
            scenario_id=scenario_id,
            preds_total=[],
            gts_total=[],
            anormal_frame=[]
        )
        results_dict[scenario_id] = scenario_data
    return results_dict


def compute_scenario_yaml_dict(scenario: ScenarioData):
    yaml_dict = {}

    detectable_gts = np.squeeze(scenario.gts_total[scenario.anormal_frame])
    detectable_preds = np.squeeze(scenario.preds_total[scenario.anormal_frame])
    detectable_results = metrics.compute_metrics(detectable_preds, detectable_gts)

    total_gts, total_preds = np.squeeze(scenario.gts_total), np.squeeze(scenario.preds_total)
    total_results = metrics.compute_metrics(total_preds, total_gts)

    yaml_dict["Anomaly_Properties"] = scenario.anomaly_attributes
    yaml_dict["scenarios_results_detectable"] = detectable_results
    yaml_dict["scenarios_results_total"] = total_results

    return yaml_dict


def initialize_anomaly_size_dict():
    values_dict = lambda: {"preds": [], "gts": []}

    anomaly_size_dict = defaultdict(values_dict)
    return anomaly_size_dict

def create_size_detection_dict(anomaly_size_dict):
    yaml_dict = {}
    for size in anomaly_size_dict.keys():
        preds = anomaly_size_dict[size]["preds"]
        gts = anomaly_size_dict[size]["gts"]
        yaml_dict[size] = metrics.compute_metrics(preds, gts)
    return yaml_dict



def main(args):
    voxelpred_dir, anovox_dir, datatype =  args.predictions, args.anovox_datapath, args.datatype


    pred_grids, anovox_gt_grids, scenario_dict = collect_data(voxelpred_dir, anovox_dir, args.datatype)
    anovox_gt_grids, anomaly_in_view = [x[0] for x in anovox_gt_grids], [y[1] for y in anovox_gt_grids]
    if args.intersect_gt_datapath:
        gt_grids = sorted(os.listdir(args.intersect_gt_datapath))
        gt_grids = [os.path.join(args.intersect_gt_datapath, gt_grid) for gt_grid in gt_grids]
    else:
        gt_grids = anovox_gt_grids
    assert len(pred_grids) == len(gt_grids), "amount of predictions and ground truth files not matching"

    scenario_data = initialize_results_dict(scenario_dict)

    for i, pred_grid in enumerate(tqdm(pred_grids)):

        anomaly_detectable = anomaly_in_view[i]
        gt_grid = gt_grids[i]
        anovox_gt_grid = anovox_gt_grids[i]

        if args.intersect_gt_datapath:
            preds, gts = np.load(pred_grid), np.load(gt_grid)

            gts = gts[:,-1]
            outlier_mask, inlier_mask = metrics.mask_anomaly_voxels(gts)
            preds_i = preds[:,-1]
            gts_i = np.zeros(gts.shape)
            gts_i[outlier_mask] = 1
            anomaly_in_voxel_grid = metrics.anomaly_included(gts_i, anomaly_label=1)
            assert preds_i.size == gts_i.size, 'Sizes of grids in {iteration} does not match. Size preds: {preds}, Size gts: {gts}'.format(iteration=i, preds=preds_i.size, gts=gts_i.size)
        else:
            preds_i, gts_i, anomaly_in_voxel_grid = metrics.intersect_grids(pred_grid, gt_grid, front_only=(args.datatype=='image'), return_anomaly_detectable=True)

        scenario_path = os.path.normpath(anovox_gt_grid)
        scenario_path = scenario_path.split(os.sep)
        scenario = scenario_path[-3]
        scenario_data[scenario].preds_total.append(preds_i)
        scenario_data[scenario].gts_total.append(gts_i)
        scenario_data[scenario].anormal_frame.append(anomaly_detectable and anomaly_in_voxel_grid) # anomaly must be viewable in data type and labeled as anomaly in voxel grid
    anomaly_size_dict = initialize_anomaly_size_dict()
    total_dict = defaultdict(list)


    for scenario in scenario_data.keys():
        scenario_i = scenario_data[scenario]
        anomaly_size = scenario_i.anomaly_attributes["size"]
        detectable_frames = scenario_i.anormal_frame
        for i, anormal_frame in enumerate(detectable_frames):
            if anormal_frame:
                preds_array = np.array(scenario_i.preds_total[i])# .squeeze()
                gts_array = np.array(scenario_i.gts_total[i])# .squeeze()
                anomaly_size_dict[anomaly_size]["preds"].extend(preds_array)
                anomaly_size_dict[anomaly_size]["gts"].extend(gts_array)
                total_dict["detectable_preds"].extend(preds_array)
                total_dict["detectable_gts"].extend(gts_array)

        preds_total = [pred for val_arr in scenario_i.preds_total for pred in val_arr]
        gts_total = [label for gt_arr in scenario_i.gts_total for label in gt_arr]

        total_dict["total_preds"].extend(preds_total)
        total_dict["total_gts"].extend(gts_total)

    if args.store_final_values:
        value_folder = args.output_file + "_values"
        if os.path.exists(value_folder):
            shutil.rmtree(value_folder)
        os.mkdir(value_folder)
        for key in total_dict.keys():
            value_list = total_dict[key]
            np.save(os.path.join(value_folder, key), value_list)


    print("anomaly voxels in all voxel grids with anomalies in it:", np.count_nonzero(total_dict["detectable_gts"]))
    print("total of voxels of voxel grids where anomaly is detectable:",len(total_dict["detectable_gts"]))
    print("all voxels in total:", len(total_dict["total_gts"]))
    yaml_dict = dict(
        Normality_Included = metrics.compute_metrics(total_dict["total_preds"], total_dict["total_gts"]),
        Anomalies_Only = metrics.compute_metrics(total_dict["detectable_preds"], total_dict["detectable_gts"]),
        Detection_Results_by_Anomaly_Size = create_size_detection_dict(anomaly_size_dict)
    )

    results_dir = "results"
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    output_file = os.path.join(results_dir, '{}.yaml'.format(args.output_file))
    with open(output_file, 'w') as yaml_file:
        yaml.dump(yaml_dict, yaml_file, default_flow_style=False)
    print("Results stored at {}".format(output_file))











if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OOD Evaluation')
    """This uses the old evaluation method that assumes sorted voxel grids for evaluation"""
    parser.add_argument('--predictions', type=str,
                        help=""""path to folder storing predictions in voxel format.""")
    parser.add_argument('--anovox_datapath', type=str,
                        help=""""path to anovox root""")
    parser.add_argument('--intersect_gt_datapath', type=str,
                        help=""""path to root of sorted directory with voxel grids intersected""")
    parser.add_argument('--store_final_values', action='store_true',
        help=""""store the final arrays with prediction and ground truth values to be evaluated. For testing purposes""")

    parser.add_argument('--output_file', type=str, default='results')


    parser.add_argument('--datatype', type=str, choices=["image", "pointcloud"],
                        help=""""type of data that voxel grids were created from""")

    args = parser.parse_args()

    print("EVALUATING {}".format(args.predictions) + " ON {}".format(args.anovox_datapath))
    main(args)