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
from utils import WaymoPointCloudMerger

# 在drivestudio的处理数据中，waymo数据集和nuscenes数据集有很多不同：
# 1. waymo数据集的外参在每个场景中只有0.txt  1.txt  2.txt  3.txt  4.txt这5个文件，不同帧是通过ego_pose来偏转的
# （摄像头摄像头之间是固定的，只要知道一个主摄像头每一帧的情况，就可以算出其他摄像头相对于主摄像头每一帧的情况
# 2.雷达点云的合成也不一样，这里我参考了drivestudio项目的waymo_sourceloader.py中的点云合成代码，详见：
# https://github.com/ziyc/drivestudio/blob/main/datasets/waymo/waymo_sourceloader.py

class WaymoDataConvert:
    def __init__(
        self,
        data_path: str,
        output_path: str,
        cam_index: str,
    ):
        self.data_path = data_path
        self.output_path = output_path
        self.cam_index = cam_index

    def merge_lidar(
            self,
            start_timestep: int = 0,
            end_timestep: int = 198
        ):
        # 创建并合并点云
        merger = WaymoPointCloudMerger(self.data_path, start_timestep, end_timestep)
        merger.merge_and_downsample(voxel_size=0.1, save_path = self.output_path + '/points3D.ply')


    def data_convert(self):
        # 合并雷达点云
        self.merge_lidar()
        # 转换内参cameras.txt文件
        getWaymoIntrinsics_index(self.data_path, self.output_path, self.cam_index)
        # 转换外参images.txt文件
        getWaymoExtrinsics_index(self.data_path, self.output_path, self.cam_index)

# OpenCV to Dataset coordinate transformation
# opencv coordinate system: x right, y down, z front
# waymo coordinate system: x front, y left, z up
OPENCV2DATASET = np.array(
    [[0, 0, 1, 0], [-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, 1]]
)

def getWaymoIntrinsics_index(input_file, output_file, index):
    output_file = output_file + "/cameras.txt"
    # extrinsics_dir = input_file + '/extrinsics'
    intrinsics_dir = input_file + '/intrinsics'
    img_dir = input_file + '/images'
    img_name = get_file_paths_in_directory(img_dir)

    # 先读取内参
    intrinsics_names = get_file_paths_in_directory(intrinsics_dir)
    intrinsics = []
    lines = [] # 记录数据
    for name in intrinsics_names:
        # 只读取前四行
        _intrinsics = np.loadtxt(name, max_rows=4)
        intrinsics.append(_intrinsics)
    # print(intrinsics)
    _idx = 1

    # 用户输入的字符串索引转换为int类型的列表
    int_list = index_transform(index)
    # 使用图片文件名来循环遍历：
    for img_file in img_name:
        filename = os.path.basename(img_file)
        filename_wo_ext = os.path.splitext(filename)[0]
        # print(filename_wo_ext) # "190_0", "190_1", "190_2"等

        # 使用正则表达式来匹配 "_" 后面的数字
        pattern = r'_(\d+)'
        numbers = re.search(pattern, filename_wo_ext).group(1)
        # print(numbers)
        # print(int_list)
        if int(numbers) in int_list:
            # print("------------------------")
            # print(f"========={numbers}=========")
            # 通过后面的数字来确定是哪个摄像头，从而知道这一行使用哪一个内参文件
            _intrinsics = intrinsics[int(numbers)] # 文件命名是从0开始

            img_path = img_dir + '/' + filename_wo_ext + '.jpg'
            img = Image.open(img_path)
            # 获取图片分辨率 (宽度, 高度)
            width, height = img.size

            # line = f"{_idx} {'PINHOLE'} {width} {height} {' '.join(map(str, _intrinsics))} {img_path}"
            line = f"{_idx} {'PINHOLE'} {width} {height} {' '.join(map(str, _intrinsics))}"
            _idx += 1
            lines.append(line)
    # 将所有数据写入 images.txt
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"所有数据已写入 {output_file}")

def getWaymoExtrinsics_index(input_file, output_file, index):
    output_file = output_file + "/images.txt"
    # 先读取外参:外参只有5个文件
    extrinsics_dir = input_file + '/extrinsics'
    extrinsics_names = get_file_paths_in_directory(extrinsics_dir)
    ego_pose_dir = input_file + '/ego_pose'
    # ego_pose_name = get_file_paths_in_directory(ego_pose_dir)
    extrinsics = []
    idx = 1
    lines = [] # 记录数据
    for name in extrinsics_names:
        # 只读取前四行
        _extrinsics = np.loadtxt(name)
        extrinsics.append(_extrinsics)

    img_dir = input_file + '/images'
    img_name = get_file_paths_in_directory(img_dir)
    # ego_pose_dir = input_file + '/ego_pose'
    # ego_pose_name = get_file_paths_in_directory(ego_pose_dir)

    # 用户输入的字符串索引转换为int类型的列表
    int_list = index_transform(index)
    ego_to_world_start = np.loadtxt(ego_pose_dir + '/000.txt', dtype=str)
    ego_to_world_start = np.array([[Decimal(value) for value in row] for row in ego_to_world_start], dtype=object).astype(float)
    # 使用图片文件名来循环遍历：
    for img_file in img_name:
    # for idx, ego_pose_file in enumerate(ego_pose_name, start=1):
        filename = os.path.basename(img_file)
        filename_wo_ext = os.path.splitext(filename)[0]

        # 使用正则表达式来匹配 "_" 后面的数字
        pattern_suf = r'_(\d+)'
        numbers_suf = re.search(pattern_suf, filename_wo_ext).group(1)

        # if判断来筛选用户填写的相机索引
        if int(numbers_suf) in int_list:
            # 使用正则表达式来匹配 "_" 前面的数字
            pattern_pre = r'(\d+)_.*'
            numbers_pre = re.search(pattern_pre, filename_wo_ext).group(1)
            ego_pose_current_name = ego_pose_dir + '/' + numbers_pre + '.txt'
            # print(f"------------{ego_pose_current_name}------------")
            # print(f"------------{numbers_suf}------------")
            cam_to_ego = extrinsics[int(numbers_suf)] @ OPENCV2DATASET

            ego_to_world_current = np.loadtxt(ego_pose_current_name, dtype=str)
            ego_to_world_current = np.array([[Decimal(value) for value in row] for row in ego_to_world_current], dtype=object).astype(float)

            # 计算ego_pose的逆矩阵
            ego_to_world_inv = np.linalg.inv(ego_to_world_start)
            ego_to_world = ego_to_world_inv @ ego_to_world_current
            _cam_to_ego = ego_to_world @ cam_to_ego

            R = _cam_to_ego[:3, :3]
            # 计算四元数
            quaternion = rotation_matrix_to_quaternion(R)

            # print("四元数 (w, x, y, z):")
            quaternion = [float(q) for q in quaternion]

            # 提取平移向量 (最后一列的前三行)
            T = _cam_to_ego[:3, 3]
            T = [float(t) for t in T]

            imgname = os.path.splitext(os.path.basename(ego_pose_current_name))[0] + '_' + numbers_suf + '.jpg'

            line = f"{idx} {' '.join(map(str, quaternion))} {' '.join(map(str, T))} {idx} {imgname}\n"
            lines.append(line)

            idx += 1
    # 将所有数据写入 images.txt
    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"所有数据已写入 {output_file}")
