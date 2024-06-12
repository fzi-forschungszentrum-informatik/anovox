# currently: Training5 Centerpoint on 0.5 for double checkup
identifier=cam5_90k
voxel_resolution=0.5
score_function=centerpoint



python3 voxelize_sensor_scores.py --scores_dir <...>/RbA/anomaly_scores/swin_b_1dl/anovox/ --dataset_path <...>/Anomaly_Datasets/goodresultsAnovox/AnoVox/ --score_function centerpoint --datatype image --voxel_resolution 0.5 --output_dir oneimageresult &&
# python3 voxelize_groundtruth.py --dataset_path <...>/Anomaly_Datasets/AnoVox --voxel_resolution 0.5 --datatype image --output_dir gt_anovox_05res &&
python3 eval/evaluate_voxels.py --predictions <...>/anovox/benchmark/2imageresults --anovox_datapath <...>/Anomaly_Datasets/goodresultsAnovox/AnoVox/  --datatype image --output_file lastoneimageresults # --intersect_gt_datapath gt_anovox_05res/