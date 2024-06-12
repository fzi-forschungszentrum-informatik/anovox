import os
import open3d as o3d
import numpy as np
import argparse


class PointCloudVoxelizer:
    def __init__(self, voxel_resolution, voxel_grid_size) -> None:
        self.voxel_resolution = voxel_resolution
        self.voxel_grid_size = voxel_grid_size
        self.point_cloud_predictions = []
        # self.voxel_grid_predictions = []

    def create_voxel_grids(self):
        os.mkdir("PCD_Voxel_Preds")
        for i, point_cloud in enumerate(self.point_cloud_predictions):
            pcd_name = os.path.join("PCD_Voxel_Preds", "pred{}".format(str(i)))
            self.voxelize_one(point_cloud, pcd_name)

    def collect_data(self, prediction_path, ground_truth_path):
        def sorter(file_path):
            identifier = (os.path.basename(file_path).split('.')[0]).split('_')[-1]
            return int(identifier)

        predictions = sorted(os.listdir(prediction_path))
        point_cloud_paths = []
        for scenario in os.listdir(ground_truth_path):
            if scenario == 'Scenario_Configuration_Files':
                continue
            pcd_dir = os.path.join(ground_truth_path, scenario, 'PCD')
            for pcd in os.listdir(pcd_dir):
                pcd_path = os.path.join(pcd_dir, pcd)
                point_cloud_paths.append(pcd_path)
        point_cloud_paths.sort(key=sorter)
        return predictions, point_cloud_paths


    def create_pcd_predictions(self, pred_value_paths, pcd_paths):
        assert len(pred_value_paths) != len(pcd_paths), "number of prediction files and point cloud files do not match"
        for i, prediction_path in enumerate(pred_value_paths):
            predictions = np.load(prediction_path)
            point_cloud_path = pcd_paths[i]
            point_cloud = o3d.io.read_point_cloud(point_cloud_path)
            points = np.array(point_cloud.points)

            # assert points.size != predictions.size, "number of points and predictions do not match in {}".format(str(i))

            points = points[:,:3]
            predictions.reshape(-1, 1)

            pcd_prediction = np.concatenate([points, predictions], axis=1)
            self.point_cloud_predictions.append(pcd_prediction)
        return self.point_cloud_predictions


    def voxelize_one(self, pcloud, save_name, pipe=None):
        bev_offset_forward = 0 # in px
        bev_resolution = 0.2
        offset_z = 0 # in px

        offset_x = bev_offset_forward * bev_resolution
        offset_z = 0
        voxel_points, semantics = self.voxel_filter(pcloud, self.voxel_resolution, self.voxel_grid_size, [offset_x, 0, offset_z])
        data = np.concatenate([voxel_points, semantics], axis=1) # [:, None]
        # voxels = np.zeros(shape=cfg.voxel_size, dtype=np.uint8)
        # voxels[voxel_points[:, 0], voxel_points[:, 1], voxel_points[:, 2]] = semantics
        # csr_voxels = sp.csr_matrix(voxels.reshape(voxels.shape[0], -1))
        np.save(f'{save_name}', data)
        # np.save(f'{save_path}/voxel_coo/voxel_coo_{name}.npy', csr_voxels)

        if pipe is not None:
            pipe.send(['x'])


    def voxel_filter(self, pcloud, voxel_resolution, grid_size, offset):
        # pcd = np.asarray(pcloud.points)
        # sem = (np.asarray(pcloud.colors) * 255.0).astype(np.uint8)
        pcd = pcloud[:, :3]
        sem = pcloud[:, -1]
        # new_sem = np.arange(len(sem))
        # for i, value in enumerate(sem): #
        #     color_index = np.where((COLOR_PALETTE == value).all(axis = 1))
        #     # print(value)
        #     # for color in COLOR_PALETTE:
        #     #     if (value == color).all():
        #     #         new_sem[i] = np.where((COLOR_PALETTE == value))[0][0]
        #     # print(color_index)
        #     new_sem[i] = color_index[0][0]
        # sem = new_sem
        # unique, counts = np.unique(sem, return_counts = True)
        # print(dict(zip(unique, counts)))
        grid_size = np.asarray(grid_size)
        offset = np.asarray(offset)
        offset += voxel_resolution * grid_size / 2
        pcd_b = pcd + offset
        idx = ((0 <= pcd_b) & (pcd_b < grid_size * voxel_resolution)).all(axis=1)
        pcd_b, sem_b = pcd_b[idx], sem[idx] # limit point cloud to voxel grid size

        Dx, Dy, Dz = grid_size
        # compute index for every point in a voxel
        hxyz, hmod = np.divmod(pcd_b, voxel_resolution)
        h = hxyz[:, 0] + hxyz[:, 1] * Dx + hxyz[:, 2] * Dx * Dy

        # h_n = np.nonzero(np.bincount(h.astype(np.int32)))
        h_idx = np.argsort(h)
        h, hxyz, sem_b, pcd_b, hmod = h[h_idx], hxyz[h_idx], sem_b[h_idx], pcd_b[h_idx], hmod[h_idx]
        h_n, indices = np.unique(h, return_index=True)
        n_f = h_n.shape[0]
        n_all = h.shape[0]
        voxels = np.zeros((n_f, 3), dtype=np.uint16)
        semantics = np.zeros((n_f,1), dtype=np.float64)
        # points_f = np.zeros((n_f, 3))
        # road_idx = np.where((COLOR_PALETTE == (157, 234, 50)).all(axis = 1))[0][0] # roadline 24u
        # road_idx = np.where(LABEL_CLASS == 'roadlines')[0][0]
        # voxels = []
        # semantics = []
        # points_f = []
        for i in range(n_f):
            # idx_ = (h == h_n[i])
            idx_ = np.arange(indices[i], indices[i+1]) if i < n_f - 1 else np.arange(indices[i], n_all)
            # dis = np.sum(hmod[idx_] ** 2, axis=1)

            avg_score = np.mean(sem_b[idx_])

            # semantic = sem_b[idx_][np.argmin(dis)]  # if not np.isin(sem_b[idx_], road_idx).any() else road_idx
            # semantic = np.bincount(sem_b.squeeze()[idx_]).argmax() if not np.isin(sem_b[idx_], road_idx).any() else road_idx
            voxels[i] = hxyz[idx_][0]
            semantics[i] = avg_score
            # points_f[i][2] += center[2] / 2
            # voxels.append(hxyz[idx_][0])
            # semantics.append(semantic)
            # points_f.append(pcd_b[idx_].mean(axis=0) - center)
        # debug_set, counts = np.unique(semantics, return_counts=True)
        return voxels, semantics

    def anomalous_instance_in_point_cloud(self, gt_pcd):
        labels = gt_pcd[:,:3] # bullshit
        # return np.isin(29, labels)
        return np.isin(33, labels) or np.isin(34, labels)


def merge_preds_to_points(preds, points):
    preds = np.load(preds).reshape(-1,1)
    print("max:", preds.max())
    print("min:", preds.min())
    pcd = o3d.io.read_point_cloud(points)
    points = np.asarray(pcd.points)
    point_preds = np.concatenate([points, preds], axis=1)
    return point_preds

def main(args):
    return

if __name__ == "__main__":
    # voxelizer = PointCloudVoxelizer(voxel_resolution=0.2, voxel_grid_size=(1000,1000,64))
    parser = argparse.ArgumentParser(description='OOD Evaluation')
    parser.add_argument('--predictions', type=str, #default='/home/lukasnroessler/Projects/RbA/voxelpreds',
                        help=""""path to folder storing predictions in voxel format.""")
    parser.add_argument('--anovox_datapath', type=str, #default='/home/lukasnroessler/Anomaly_Datasets/AnoVox',
                        help=""""path to anovox root""")
    # parser.add_argument('--intersect_grids', action='store_true',
    #                     help=""""set to false if you already have ground truth voxel grids that match the size of the prediction voxel grids""")
    # parser.add_argument('--gt_grids_dir', type=str,
    #                     help=""""only needed if gt grids are already intersected or not in anovox. Not to be used
    #                     if you want to use original gt grids from anovox""")

    args = parser.parse_args()


    # main(args)
    # predictions, pcd_paths = voxelizer.collect_data()
    preds = "voxelscores_12frame/pcd_voxel_scores_000000.npy"
    points = "/media/tes_unreal/Samsung_T5/BA/BackupDatasets/AnomalyDatasets/AnoVox/Scenario_c8d20e26-7eaf-425b-8f86-c26bdd4ba365/PCD/PCD_271.pcd"
    merged_pcd = merge_preds_to_points(preds, points)
    np.save("score12pcd.npy", merged_pcd)
