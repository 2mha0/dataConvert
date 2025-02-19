import os
import numpy as np
import torch
from tqdm import trange
# from omegaconf import OmegaConf
import open3d as o3d

class PointCloudMerger:
    def __init__(
        self,
        data_path: str,
        start_timestep: int,
        end_timestep: int,
        device: torch.device = torch.device("cpu"),
        truncated_max_range: float = None,
        truncated_min_range: float = None,
        only_use_top_lidar: bool = True,
    ):
        self.data_path = data_path
        self.start_timestep = start_timestep
        self.end_timestep = end_timestep
        self.device = device
        self.truncated_max_range = truncated_max_range
        self.truncated_min_range = truncated_min_range
        self.only_use_top_lidar = only_use_top_lidar
        self.create_all_filelist()
        self.load_calibrations()

    def create_all_filelist(self):
        """
        Create a list of all the lidar files in the dataset.
        """
        lidar_filepaths = []
        for t in range(self.start_timestep, self.end_timestep):
            lidar_filepaths.append(
                os.path.join(self.data_path, "lidar", f"{t:03d}.bin")
            )
        self.lidar_filepaths = np.array(lidar_filepaths)

    def load_calibrations(self):
        """
        Load the calibration files (ego pose) for transforming LiDAR to world coordinates.
        """
        lidar_to_worlds = []
        ego_to_world_start = np.loadtxt(
            os.path.join(self.data_path, "ego_pose", f"{self.start_timestep:03d}.txt")
        )
        for t in range(self.start_timestep, self.end_timestep):
            ego_to_world_current = np.loadtxt(
                os.path.join(self.data_path, "ego_pose", f"{t:03d}.txt")
            )
            lidar_to_world = np.linalg.inv(ego_to_world_start) @ ego_to_world_current
            lidar_to_worlds.append(lidar_to_world)

        self.lidar_to_worlds = torch.from_numpy(np.stack(lidar_to_worlds, axis=0)).float()

    def load_lidar(self):
        """
        Load the lidar data from the files and transform them into the world coordinate system.
        """
        points_all = []
        for t in trange(self.start_timestep, self.end_timestep, desc="Loading lidar", dynamic_ncols=True):
            lidar_info = np.memmap(self.lidar_filepaths[t - self.start_timestep], dtype=np.float32, mode="r").reshape(-1, 14)

            # Select top lidar based on the laser ID if necessary
            if self.only_use_top_lidar:
                lidar_info = lidar_info[lidar_info[:, 13] == 0]

            lidar_origins = torch.from_numpy(lidar_info[:, :3]).float()
            lidar_points = torch.from_numpy(lidar_info[:, 3:6]).float()

            # Apply ego pose transformation
            lidar_points = (
                self.lidar_to_worlds[t - self.start_timestep][:3, :3] @ lidar_points.T
                + self.lidar_to_worlds[t - self.start_timestep][:3, 3:4]
            ).T

            # Optionally filter based on truncated range
            valid_mask = torch.ones_like(lidar_points[:, 0]).bool()
            if self.truncated_max_range is not None:
                valid_mask = lidar_points[:, 0] < self.truncated_max_range
            if self.truncated_min_range is not None:
                valid_mask = valid_mask & (lidar_points[:, 0] > self.truncated_min_range)

            lidar_points = lidar_points[valid_mask]
            points_all.append(lidar_points)

        # Concatenate all points into one large tensor
        all_points = torch.cat(points_all, dim=0)

        return all_points

    def save_point_cloud(self, points, filename="merged_pointcloud.ply"):
        """
        Save the merged point cloud to a .ply file.
        """
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        o3d.io.write_point_cloud(filename, pcd)
        print(f"Point cloud saved to {filename}")

    def merge_and_downsample(self, voxel_size: float = 0.1):
        """
        Merge all point clouds and perform voxel downsampling.
        """
        points_all = self.load_lidar()

        # Voxel downsampling
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points_all.numpy())

        # Perform voxel downsampling
        pcd_downsampled = pcd.voxel_down_sample(voxel_size)

        # Save the downsampled point cloud
        self.save_point_cloud(np.asarray(pcd_downsampled.points), filename="points3D.ply")
        print(f"Downsampled point cloud saved.")
# 配置文件路径、时间步长范围等
data_path = "/home/zmh/data/waymo/processed/training/023"
start_timestep = 0
end_timestep = 198  # 根据你的需要选择合适的范围

# 创建并合并点云
merger = PointCloudMerger(data_path, start_timestep, end_timestep)
merger.merge_and_downsample(voxel_size=0.1)