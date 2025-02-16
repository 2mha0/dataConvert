import numpy as np
import os
from decimal import Decimal
from PIL import Image
import re
from glob import glob
import open3d as o3d
from utils import index_transform, get_files_by_camera_index

import sys
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import get_file_paths_in_directory
from utils import rotation_matrix_to_quaternion

def getExtrinsics_all(input_file, output_file):
    """生成所有摄像头的相机外参:extrinsics目录转换为images.txt文件

    Args:
        input_file (str): 数据的输入路径，例如/home/zmh/Codes/nuscenesData/000,
        在该目录下有dynamic_masks  extrinsics  fine_dynamic_masks  humanpose  images  
        instances  intrinsics  lidar  lidar_pose  sky_masks这些目录。
        output_file (str): images.txt文件写入路径,例如/home/zmh/Codes/dataConvert/exp/data/images.txt。
    """
    extrinsics_dir = input_file + '/extrinsics'
    extrinsics_name = get_file_paths_in_directory(extrinsics_dir)
    lines = [] # 记录数据
    for idx, extrinsics_file in enumerate(extrinsics_name, start=1):
        # print("------  读取外参文件：" + str(extrinsics_file) + "  ---------")
        # 读取外参矩阵
        extrinsics_matrix_str = np.loadtxt(extrinsics_file, dtype=str)
        # 将字符串转换为 Decimal 数值类型
        extrinsics_matrix = np.array([[Decimal(value) for value in row] for row in extrinsics_matrix_str], dtype=object).astype(float)

        # 这里需要计算 extrinsics_matrix 的逆矩阵
        extrinsics_matrix_inv = np.linalg.inv(extrinsics_matrix)

        # 提取逆矩阵中的旋转部分
        R = extrinsics_matrix_inv[:3, :3]
        # 计算四元数
        quaternion = rotation_matrix_to_quaternion(R)

        # print("四元数 (w, x, y, z):")
        # print([float(q) for q in quaternion])  # 转换回 float 进行打印
        quaternion = [float(q) for q in quaternion]
        # print(quaternion)

        # 提取平移向量 (最后一列的前三行)
        T = extrinsics_matrix_inv[:3, 3]
        T = [float(t) for t in T]
        # print("平移向量:")
        # print(T)

        filename = os.path.basename(extrinsics_file)
        filename_wo_ext = os.path.splitext(filename)[0]
        imgname = filename_wo_ext + '.jpg'

        line = f"{idx} {' '.join(map(str, quaternion))} {' '.join(map(str, T))} {idx} {imgname}\n"
        lines.append(line)

    # 将所有数据写入 images.txt
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"所有摄像头的相机外参数据已写入 {output_file}")
        
def getIntrinsics_all(input_file, output_file):
    """生成所有摄像头的相机内参:intrinsics目录转换为cameras.txt文件

    Args:
        input_file (str): 数据的输入路径，例如/home/zmh/Codes/nuscenesData/000,
        在该目录下有dynamic_masks  extrinsics  fine_dynamic_masks  humanpose  images  
        instances  intrinsics  lidar  lidar_pose  sky_masks这些目录。
        output_file (str): cameras.txt文件写入路径,例如/home/zmh/Codes/dataConvert/exp/data/cameras.txt。
    """
    extrinsics_dir = input_file + '/extrinsics'
    intrinsics_dir = input_file + '/intrinsics'
    img_dir = input_file + '/images'
    extrinsics_name = get_file_paths_in_directory(extrinsics_dir)
    # 先读取内参
    intrinsics_names = get_file_paths_in_directory(intrinsics_dir)
    intrinsics = []
    lines = [] # 记录数据
    for name in intrinsics_names:
        # 只读取前四行
        _intrinsics = np.loadtxt(name, max_rows=4)
        intrinsics.append(_intrinsics)
    # print(intrinsics)

    # 使用外参的文件名来遍历循环：
    for idx, extrinsics_file in enumerate(extrinsics_name, start=1):
        filename = os.path.basename(extrinsics_file)
        filename_wo_ext = os.path.splitext(filename)[0]
        # print(filename_wo_ext) # "190_0", "190_1", "190_2"等

        # 使用正则表达式来匹配 "_" 后面的数字
        pattern = r'_(\d+)'
        numbers = re.search(pattern, filename_wo_ext).group(1)
        # 通过后面的数字来确定是哪个摄像头，从而知道这一行使用哪一个内参文件
        _intrinsics = intrinsics[int(numbers)] # 文件命名是从0开始

        img_path = img_dir + '/' + filename_wo_ext + '.jpg'
        img = Image.open(img_path)
        # 获取图片分辨率 (宽度, 高度)
        width, height = img.size

        line = f"{idx} {'PINHOLE'} {width} {height} {' '.join(map(str, _intrinsics))}"
        lines.append(line)

    # 将所有数据写入 images.txt
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"所有摄像头的相机内参数据已写入 {output_file}")

def mergePointClouds(input_file, output_ply, voxel_size=0.1):
    """点云合并

    Args:
        input_file (str): 数据的输入路径，例如/home/zmh/Codes/nuscenesData/000,
        在该目录下有dynamic_masks  extrinsics  fine_dynamic_masks  humanpose  images  
        instances  intrinsics  lidar  lidar_pose  sky_masks这些目录。
        output_ply (str): points3D.ply文件写入路径,例如./data/points3D.ply。
        voxel_size (float):体素大小,默认为0.1
    """
    lidar_dir = input_file + "/lidar"  # LiDAR 点云文件目录
    pose_dir = input_file + "/lidar_pose"  # 车辆姿态目录
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

def getExtrinsics_by_index(input_file, output_file, index):
    """生成指定索引的摄像头的相机外参:extrinsics目录转换为images.txt文件

    Args:
        input_file (str): 数据的输入路径，例如/home/zmh/Codes/nuscenesData/000,
        在该目录下有dynamic_masks  extrinsics  fine_dynamic_masks  humanpose  images  
        instances  intrinsics  lidar  lidar_pose  sky_masks这些目录。
        output_file (str): images.txt文件写入路径,例如/home/zmh/Codes/dataConvert/exp/data/images.txt。
        index (str): 摄像头索引字符串，例如'0、1、2'，当然也可以只传入一个'0'
    """
    lines = [] # 记录数据
    idx = 1
    extrinsics_dir = input_file + '/extrinsics'
    # 用户输入的字符串索引转换为int类型的列表
    int_list = index_transform(index)
    for cameraIndex in int_list:
        files = get_files_by_camera_index(extrinsics_dir, cameraIndex)
        for extrinsics_file in files:
            # print(extrinsics_file)
            # 读取外参矩阵
            extrinsics_matrix_str = np.loadtxt(extrinsics_file, dtype=str)
            # 将字符串转换为 Decimal 数值类型
            extrinsics_matrix = np.array([[Decimal(value) for value in row] for row in extrinsics_matrix_str], dtype=object).astype(float)

            # 计算 extrinsics_matrix 的逆矩阵
            extrinsics_matrix_inv = np.linalg.inv(extrinsics_matrix)

            # 提取逆矩阵中的旋转部分
            R = extrinsics_matrix_inv[:3, :3]
            # 计算四元数
            quaternion = rotation_matrix_to_quaternion(R)
            quaternion = [float(q) for q in quaternion]

            # 提取平移向量 (最后一列的前三行)
            T = extrinsics_matrix_inv[:3, 3]
            T = [float(t) for t in T]

            filename = os.path.basename(extrinsics_file)
            filename_wo_ext = os.path.splitext(filename)[0]
            imgname = filename_wo_ext + '.jpg'

            line = f"{idx} {' '.join(map(str, quaternion))} {' '.join(map(str, T))} {idx} {imgname}\n"
            lines.append(line)
            idx += 1
    # 将所有数据写入 images.txt
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"{index}摄像头的相机外参数据已写入 {output_file}")       

def getIntrinsics_by_index(input_file, output_file, index):
    """生成指定索引的摄像头的相机内参:intrinsics目录转换为cameras.txt文件

    Args:
        input_file (str): 数据的输入路径，例如/home/zmh/Codes/nuscenesData/000,
        在该目录下有dynamic_masks  extrinsics  fine_dynamic_masks  humanpose  images  
        instances  intrinsics  lidar  lidar_pose  sky_masks这些目录。
        output_file (str): images.txt文件写入路径,例如/home/zmh/Codes/dataConvert/exp/data/images.txt。
        index (str): 摄像头索引字符串，例如'0、1、2'，当然也可以只传入一个'0'
    """
    extrinsics_dir = input_file + '/extrinsics'
    intrinsics_dir = input_file + '/intrinsics'
    img_dir = input_file + '/images'
    
    # 先读取内参
    intrinsics_names = get_file_paths_in_directory(intrinsics_dir)
    intrinsics = []
    idx = 1
    lines = [] # 记录数据
    for name in intrinsics_names:
        # 只读取前四行
        _intrinsics = np.loadtxt(name, max_rows=4)
        intrinsics.append(_intrinsics)
    # print(intrinsics)

    # 用户输入的字符串索引转换为int类型的列表
    int_list = index_transform(index)
    for cameraIndex in int_list:
        files = get_files_by_camera_index(extrinsics_dir, cameraIndex)
        for extrinsics_file in files:
            # print(extrinsics_file)
            filename = os.path.basename(extrinsics_file)
            filename_wo_ext = os.path.splitext(filename)[0]
            # print(filename_wo_ext)

            # 使用正则表达式来匹配 "_" 后面的数字
            pattern = r'_(\d+)'
            numbers = re.search(pattern, filename_wo_ext).group(1)
            # 通过后面的数字来确定是哪个摄像头，从而知道这一行使用哪一个内参文件
            _intrinsics = intrinsics[int(numbers)] # 文件命名是从0开始

            img_path = img_dir + '/' + filename_wo_ext + '.jpg'
            img = Image.open(img_path)
            # 获取图片分辨率 (宽度, 高度)
            width, height = img.size

            line = f"{idx} {'PINHOLE'} {width} {height} {' '.join(map(str, _intrinsics))}"
            lines.append(line)
            idx += 1
    # 将所有数据写入 images.txt
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"{index}摄像头的相机内参数据已写入 {output_file}")