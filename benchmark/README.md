# anomaly_benchmark

This repo includes evaluation scripts for anomaly detection methods.
Evaluation is currently possible for images, point clouds and voxel grids.

## Environments
Separate requirement files for RbA and rest

## Relabeling to Cityscapes
    python convert_dataset/convet_images --dataset_path /path/to/traindata --cityscapes_format

## Retraining
Training Datasets were generated using the voxelworld repo () with branch "normaldata"
RbA:

    ```
    export DETECTRON2_DATASETS=/path/to/parentdir/of/anovox
    cd RbA
    python train_net.py --config-file configs/cityscapes/semantic-segmentation/swin/single_decoder_layer/maskformer2_swin_base_IN21k_384_bs16_90k_1dl.yaml --num-gpus 2 OUTPUT_DIR training_out
    ```

ReaL:

    ```
    cd Open_world_3D_semantic_segmentation/semantickittiscripts
    python train_cylinder_asym_ood_basic.py --config_path /path/to/configdir/config/anovox_train.yaml
    ```


## Evaluation

RbA:
    - Place pickle file with model_final.pth in ckpts/swin_b_1dl

    - For evaluation scores:

    ```
    cd RbA
    evaluate_ood.py  --out_path ood_out --models_folder ckpts/ --model_mode selective --selected_models swin_b_1dl --datasets_folder /path/to/parentdir/  --dataset_mode selective --selected_dataset anovox --roi roi.png
    ```

    - For extracting anomaly scores to voxelize:

    ```
    cd RbA
    evaluate_ood.py  --out_path /home/tes_unreal/Desktop/BA/RbA/ood_out --models_folder ckpts/ --model_mode selective --selected_models swin_b_1dl --datasets_folder /home/tes_unreal/Downloads/Anovox_Sample/  --dataset_mode selective --selected_dataset anovox --store_anomaly_scores
    ```

    - Scores are stored in anomaly_scores/swin_b_1dl/anovox/arrays

ReaL:
    - make sure that path to pt file and path to AnoVox dataset is set in anovox_val.yaml file
    - change path for uncertainty_path in main() method

    ```
    cd Open_world_3D_semantic_segmentation/semantickittiscripts
    python val_cylinder_asym_ood_anovox.py --config_path /path_to_config_dir/config/anovox_val.yaml
    ```

## Voxelization and Evaluation
    Image:
        evaluate_voxelized_imagescores.sh
    Pointcloud:
        evaluate_voxelized_pcdscores.sh

    - metrics.mask_intersect_new results differed from the ones from old eval script by 0.75% max.


