import numpy as np
from decimal import Decimal
from scipy.spatial.transform import Rotation as R
import os
import torch
from tqdm import trange
import open3d as o3d

class WaymoPointCloudMerger:
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

    def save_point_cloud(self, points, filename="points3D.ply"):
        """
        Save the merged point cloud to a .ply file.
        """
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        o3d.io.write_point_cloud(filename, pcd)
        print(f"Point cloud saved to {filename}")

    def merge_and_downsample(
            self,
            voxel_size: float = 0.1,
            save_path: str = '/home/zmh/Codes/dataConvert/test/data/points3D.ply'
        ):
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
        self.save_point_cloud(np.asarray(pcd_downsampled.points), filename = save_path)
        print(f"Downsampled point cloud saved.")

# 通过四元数计算旋转矩阵
def quaternion_to_rotation_matrix(q):
    qw, qx, qy, qz = q

    # 计算旋转矩阵
    R = np.array([
        [1 - 2 * (qy**2 + qz**2), 2 * (qx*qy - qz*qw), 2 * (qx*qz + qy*qw)],
        [2 * (qx*qy + qz*qw), 1 - 2 * (qx**2 + qz**2), 2 * (qy*qz - qx*qw)],
        [2 * (qx*qz - qy*qw), 2 * (qy*qz + qx*qw), 1 - 2 * (qx**2 + qy**2)]
    ])
    return R

# 通过旋转矩阵计算四元数
# 计算四元数
def rotation_matrix_to_quaternion(_R):
    rot = R.from_matrix(_R)
    quaternion = rot.as_quat()
    qw = quaternion[3]
    qx = quaternion[0]
    qy = quaternion[1]
    qz = quaternion[2]
    return np.array([qw, qx, qy, qz], dtype=object)  # 仍然保持 Decimal

def index_transform(index):
    """将“0、1、2、3”等索引转换为[0,1,2,3]

    Args:
        index (str): 字符串索引，格式为数字+顿号，例如'0、2、3'，不能带非数字，也不能有相同数字

    Returns:
        list: 整数列表。
    """
    # 使用 split 方法按 "、" 分割字符串，生成字符串列表
    str_list = index.split("、")

    # 用于存储已遇到的数字
    seen_numbers = set()

    # 将字符串列表中的每个元素转换为整数，生成整数列表，并添加判断逻辑
    int_list = []
    for item in str_list:
        try:
            num = int(item)
        except ValueError:
            raise ValueError(f"非数字字符 '{item}' 在输入字符串中发现。")
        
        if num in seen_numbers:
            raise ValueError(f"重复的数字 {num} 在输入字符串中发现。")
        
        seen_numbers.add(num)
        int_list.append(num)
    return int_list