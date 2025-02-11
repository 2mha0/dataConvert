import numpy as np
import open3d as o3d
import os
from glob import glob

# 设置数据目录
lidar_dir = "/home/zmh/Codes/nuscenesData/000/lidar"  # LiDAR 点云文件目录
pose_dir = "/home/zmh/Codes/nuscenesData/000/lidar_pose"  # 车辆姿态目录
output_ply = "merged_downsampled.ply"  # 输出文件
voxel_size = 0.1  # 体素大小

# 读取所有 .bin 和 .txt 文件，确保按顺序匹配
bin_files = sorted(glob(os.path.join(lidar_dir, "*.bin")))
pose_files = sorted(glob(os.path.join(pose_dir, "*.txt")))

assert len(bin_files) == len(pose_files), "点云文件数与姿态文件数不匹配！"

# 初始化 Open3D 点云对象
pcd = o3d.geometry.PointCloud()

# 读取点云和姿态数据并合并
for bin_file, pose_file in zip(bin_files, pose_files):
    # 读取点云数据
    points = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)[:, :3]  # 只取XYZ坐标

    # 读取车辆姿态（4×4 变换矩阵）
    pose_matrix = np.loadtxt(pose_file)  # 假设是 4×4 矩阵

    # 将点云转换为齐次坐标
    ones = np.ones((points.shape[0], 1))
    points_h = np.hstack((points, ones))  # [x, y, z, 1]

    # 应用姿态变换（转换到世界坐标系）
    points_global = (pose_matrix @ points_h.T).T[:, :3]

    # 生成 Open3D 点云
    frame_pcd = o3d.geometry.PointCloud()
    frame_pcd.points = o3d.utility.Vector3dVector(points_global)

    # 体素下采样减少点数
    frame_pcd = frame_pcd.voxel_down_sample(voxel_size=voxel_size)

    # 合并点云
    pcd += frame_pcd

# 再次对最终点云进行下采样
pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

# 保存到 .ply 文件
o3d.io.write_point_cloud(output_ply, pcd)

print(f"合并完成，已进行坐标变换和体素下采样，点云保存至 {output_ply}")
