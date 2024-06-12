import numpy as np
from sklearn.metrics import roc_curve, auc, average_precision_score, f1_score, confusion_matrix, precision_score, recall_score, precision_recall_curve
# import open3d as o3d
import argparse

gt_path = "<...>/Anomaly_Datasets/AnoVox/Scenario_911ef0ea-bec9-4f78-aa3b-a3b83ef07319/VOXEL_GRID/VOXEL_GRID_413.npy"
pred_path = "<...>/RbA/voxelpreds/voxelarray_score_0000000011.npy"


COLOR_PALETTE = (
        np.array(
            [
                (0, 0, 0),          # unlabeled     =   0u
                (128, 64, 128),     # road          =   1u
                (244, 35, 232),     # sidewalk      =   2u
                (70, 70, 70),       # building      =   3u=         bin_preds =
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
                (81, 0, 81),        # ground        =  25u
                (150, 100, 100),    # bridge        =  26u
                (230, 150, 140),    # rail track    =  27u
                (180, 165, 180),    # guard rail    =  28u
                (245,  0,  0),      # home          =  29u
                (255, 36, 0),       # animal        =  30u
                (224, 17, 95),      # nature        =  31u
                (184, 15, 10),      # special       =  32u
                (245, 0, 0),        # airplane      =  33u
                (245, 0, 0),        # falling       =  34u
            ]
        )
)


# DOUBLECHECKING

def mask_intersect_new(preds, gts):
    """""
    double check method whether voxels are fed into the evaluation script in the same order
    edit: Results did not change when testing on individual voxel grids but slightly did when testing on the entire benchmark. This approach definitely keeps the correct order of voxels
    """
    # preds_, gts_ = voxelgrid_intersect(preds, gts)
    preds_scores, gts_scores = voxelgrid_intersect_new(preds, gts)
    preds_scores, gts_scores = np.array(preds_scores), np.array(gts_scores)

    # preds_scores, gts_scores = preds_[:,-1:], gts_[:,-1:]
    # preds_scores, gts_scores = np.squeeze(preds_scores), np.squeeze(gts_scores)

    ood_mask, ind_mask = mask_anomaly_voxels(gts_scores)
    val_label = np.zeros((len(gts_scores),))
    val_label[ood_mask] = 1
    val_out = np.array(preds_scores)
    # ood_out = preds_scores[ood_mask]
    # ind_out = preds_scores[ind_mask]

    # ood_label = np.ones(len(ood_out))
    # ind_label = np.zeros(len(ind_out))

    # val_out = np.concatenate((ind_out, ood_out))
    # val_label = np.concatenate((ind_label, ood_label))

    return val_out, val_label

def voxelgrid_intersect_new(preds,gts):
    gt_labels = gts[:,-1:].astype(np.float64) # to match pred voxels and values
    gt_voxels = gts[:,:3].astype(np.float64)

    pred_scores = preds[:,-1:]
    pred_voxels = preds[:,:3] #.astype(np.uint16)

    # size, dim = gt_voxels.shape

    intersect_indices = np.where((gt_voxels==pred_voxels[:,None]).all(-1))[1]

    intersect_grid = gt_voxels[intersect_indices]
    intersect_labels = []# np.c_[intersect_grid, np.zeros((intersect_grid.shape[0],1))]
    intersect_preds = []# np.copy(intersect_labels)

    for i, coordinate in enumerate(intersect_grid):
        pred_voxel_index = np.where((np.isclose(pred_voxels, coordinate)).all(axis=1))[0]
        if pred_voxel_index.size != 0: # if this voxel is also in the predictions grid
            anomaly_score = pred_scores[pred_voxel_index][0]
            # intersect_preds[i][3] = anomaly_score # set the voxel value to the prediction score
            intersect_preds.extend(anomaly_score)

        gts_voxel_index = np.where((np.isclose(gt_voxels, coordinate)).all(axis=1))[0]
        if gts_voxel_index.size != 0:
            gt_id = gt_labels[gts_voxel_index][0]
            # intersect_labels[i][3] = gt_id
            intersect_labels.extend(gt_id)
    return intersect_preds, intersect_labels

# DOUBLECHECKING END


def mask_intersect(preds, gts):
    preds_, gts_ = voxelgrid_intersect(preds, gts)

    preds_scores, gts_scores = preds_[:,-1:], gts_[:,-1:]
    preds_scores, gts_scores = np.squeeze(preds_scores), np.squeeze(gts_scores)

    ood_mask, ind_mask = mask_anomaly_voxels(gts_scores)
    print("AMOUNT OF ANOMALOUS VOXELS:", np.count_nonzero(ood_mask))

    # taken from rba evaluate ood for double checking results
    ood_out = preds_scores[ood_mask]
    ind_out = preds_scores[ind_mask]

    ood_label = np.ones(len(ood_out))
    ind_label = np.zeros(len(ind_out))

    val_out = np.concatenate((ind_out, ood_out))
    val_label = np.concatenate((ind_label, ood_label))
    # rba snippet finish

    return val_out, val_label


def calculate_auroc(preds, gts):

    fpr, tpr, threshold = roc_curve(gts, preds)
    roc_auc = auc(fpr, tpr)
    fpr_best = 0
    # print('Started FPR search.')
    for i, j, k in zip(tpr, fpr, threshold):
        if i > 0.95:
            fpr_best = j
            break
    # print(k)
    return roc_auc, fpr_best, k


def calculate_fpr95(preds,gts):
    FPR95 = None
    for threshold in np.arange(1, -0.01, -0.01):  # Start with high threshold and go down
        preds_bin = np.where(preds > threshold, 1, 0)
        cm_values = confusion_matrix(gts, preds_bin).ravel()
        tn, fp, fn, tp = cm_values
        print(tn,fp,fn,tp)
        TPR = tp / (tp + fn)
        if TPR >= 0.95:
            FPR = fp / (fp + tn)
            FPR95 = FPR
            break
    return FPR95 


def calculate_specificity(preds, gts,  normality, thresholds: list=[0.5]):
    specificity_scores = []
    for i, threshold in enumerate(thresholds):
        preds_bin = np.where(preds > threshold, 1, 0)
        cm_values = confusion_matrix(gts, preds_bin).ravel()
        if normality and len(cm_values) == 1: # if no anomalies to be detected and preds are all zero
            specificity_scores.append(1)
        else:
            tn, fp, fn, tp = cm_values
            specificity = tn / (tn+fp)
            specificity_scores.append(specificity)
    return np.mean(specificity_scores)


def calculate_threshold_from_prc(preds, gts):
    precision, recall, thresholds = precision_recall_curve(gts, preds)
    # minimize distance between precision and recall scores
    optimal_threshold = sorted(list(zip(np.abs(precision - recall), thresholds)), key=lambda i: i[0], reverse=False)[0][1]
    return optimal_threshold


def mask_anomaly_voxels(gts, anomaly_id=33): # original label is in sample is 29, label in intersected gt grids is 33.
    # gt_array = np.copy(gts)
    anomaly_mask = (gts == anomaly_id)# or gts == 34)
    inlier_mask = (gts != anomaly_id)#and gts != 34)
    # anomaly_mask = (gts == 29)
    # inlier_mask = (gts != 29)


    return anomaly_mask, inlier_mask



def voxelgrid_intersect(preds, gts): # only grid of prediction is relevant for evaluation
    gt_labels = gts[:,-1:].astype(np.float64) # to match pred voxels and values
    gt_voxels = gts[:,:3].astype(np.float64)

    pred_scores = preds[:,-1:]
    pred_voxels = preds[:,:3] #.astype(np.uint16)

    size, dim = gt_voxels.shape

    intersect_indices = np.where((gt_voxels==pred_voxels[:,None]).all(-1))[1]

    intersect_grid = gt_voxels[intersect_indices]
    intersect_labels = np.c_[intersect_grid, np.zeros((intersect_grid.shape[0],1))]
    intersect_preds = np.copy(intersect_labels)

    for i, coordinate in enumerate(intersect_grid):
        pred_voxel_index = np.where((np.isclose(pred_voxels, coordinate)).all(axis=1))[0]
        if pred_voxel_index.size != 0: # if this voxel is also in the predictions grid
            anomaly_score = pred_scores[pred_voxel_index][0]
            intersect_preds[i][3] = anomaly_score # set the voxel value to the prediction score

        gts_voxel_index = np.where((np.isclose(gt_voxels, coordinate)).all(axis=1))[0]
        if gts_voxel_index.size != 0:
            gt_id = gt_labels[gts_voxel_index][0]
            intersect_labels[i][3] = gt_id
    return intersect_preds, intersect_labels


def anomaly_included(gts, anomaly_label=1):
    return np.isin(gts, anomaly_label).any()

def intersect_grids(pred_path, gt_path, front_only:bool=False, return_anomaly_detectable:bool=True):# , iteration):
    gt = np.load(gt_path)
    pred = np.load(pred_path)
    if front_only:
        # x < 500 is behind ego vehicle
        front_voxels = np.where(gt[:,0] > 500)
        gt = gt[front_voxels]
    pred_bin, gt_bin = mask_intersect(pred, gt)
    return (pred_bin, gt_bin, anomaly_included(gt_bin)) if return_anomaly_detectable else (pred_bin, gt_bin)



def compute_metrics(preds, gts, ignore=[]):
    ap = average_precision_score(gts, preds)
    auroc, fpr, _ = calculate_auroc(preds, gts)
    fpr = calculate_fpr95(preds,gts)
    smiyc_thresholds = np.arange(start=0.25, stop=0.75, step=0.05)
    prc_threshold = calculate_threshold_from_prc(preds, gts)

    def catch_division_by_zero(n,d):
        return n / d if d else 0
    specificity = calculate_specificity(preds, gts, normality=max(gts), thresholds=np.array([prc_threshold]))
    precision_scores = []
    f1_scores = []
    # for i, threshold in enumerate(smiyc_thresholds):
    for i, threshold in enumerate(smiyc_thresholds):
        preds_bin = np.where(preds > threshold, 1, 0)
        tn, fp, fn, tp = confusion_matrix(gts, preds_bin).ravel()
        # tn, fp, fn, tp = confusion_matrix(gts, preds_bin).ravel()
        # specificity_i = tn / (tn+fp)
        # specificity_scores.append(specificity_i)
        precision_i = catch_division_by_zero(tp, (tp + fp))
        precision_scores.append(precision_i)
        f1_i = f1_score(gts, preds_bin)
        f1_scores.append(f1_i)
    # specificity = np.mean(specificity_scores)
    precision_score = np.mean(precision_scores)
    f1 = np.mean(f1_scores)
    # specificity = calculate_specificity(preds, gts, [prc_threshold])
    result = {
        'auroc': float(auroc),
        'aupr': float(ap),
        'fpr95': float(fpr),
        'specificity': float(specificity),
        'f1_score': float(f1),
        'ppv': float(precision_score),
    }
    return result


if __name__ == "__main__":
    """""use this if you want to evaluate for a single voxel grid"""
    # first voxel grid in AnoVox sample: <...>/Anovox_Sample/AnoVox/Scenario_bfc1d392-fb70-4d51-a915-2b238690eb5d/VOXEL_GRID/VOXEL_GRID_5496.npy
    parser = argparse.ArgumentParser(description='Evaluation')

    parser.add_argument('--score_prediction', type=str, # default='<...>/Anomaly_Datasets/AnoVox',
                        help=""""score file""")

    parser.add_argument('--groundtruth_file', type=str, # default='<...>/Anomaly_Datasets/AnoVox',
                        help=""""ground truth file""")

    # parser.add_argument('--output', type=str, default='imagevoxels',
    #                     help="""file where anomaly scores are stored""")






    args = parser.parse_args()
    gt = np.load(args.groundtruth_file)
    pred = np.load(args.score_prediction)

    pred_bin, gt_bin = mask_intersect_new(pred, gt)
    # gts = gt[:,-1]
    # outlier_mask, inlier_mask = mask_anomaly_voxels(gts)
    # pred_bin = pred[:,-1]
    # gt_bin = np.zeros(gts.shape)
    # gt_bin[outlier_mask] = 1

    # print(pred_bin.shape)

    result = compute_metrics(pred_bin, gt_bin)
    for key in result.keys():
        print(key, ": ", result[key])
    # for input in inputs:
    #     print(f"## Opening {input} ##")
    #     if check_file_ending(input):
    #         transform_npy(input)
    #     else:
    #         print("     --> wrong filetype")