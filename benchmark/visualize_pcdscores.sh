identifier="lidar4"
voxel_resolution=0.5
score_function=centerpoint # selection between centerpoint, mean, median

python3 vis_pointclouds.py --scores_dir ./../ano_benchmark/preds --dataset_path ./../Anovox_Sample/Anovox --score_function centerpoint --datatype pointcloud --voxel_resolution $voxel_resolution --output_dir $identifier"_"$voxel_resolution"_"$score_function
python3 vis_pointclouds_uncertainty.py --scores_dir ./../ano_benchmark/preds_uncertainty --dataset_path ./../Anovox_Sample/Anovox --score_function centerpoint --datatype pointcloud --voxel_resolution $voxel_resolution --output_dir $identifier"_"$voxel_resolution"_"$score_function