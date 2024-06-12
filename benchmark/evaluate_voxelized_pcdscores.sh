identifier="lidar4"
voxel_resolution=0.5
score_function=centerpoint # selection between centerpoint, mean, median

python3 voxelize_sensor_scores.py --scores_dir ./../ano_benchmark/preds_uncertainty --dataset_path ./../Anovox_Sample/Anovox --score_function centerpoint --datatype pointcloud --voxel_resolution $voxel_resolution --output_dir $identifier"_"$voxel_resolution"_"$score_function &&
python3 voxelize_groundtruth.py --dataset_path ./../Anovox_Sample/Anovox --voxel_resolution $voxel_resolution --output_dir ./../Anovox_Sample/voxelized --datatype pointcloud &&
python3 eval/evaluate_voxels.py --predictions "./"$identifier"_"$voxel_resolution"_"$score_function --anovox_datapath ./../Anovox_Sample/Anovox  --intersect_gt_datapath ./../Anovox_Sample/voxelized --datatype pointcloud --output_file $identifier"_"$voxel_resolution"_"$score_function"_results"