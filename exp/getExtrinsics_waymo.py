# /extrinsics/0.txt
# 9.998362731902032952e-01 -6.126490657911932460e-03 1.702624225551873857e-02 1.538666713905354921e+00
# 6.212629204228849004e-03 9.999681466335748059e-01 -5.010883812664571751e-03 -2.493885762968131928e-02
# -1.699500077951916072e-02 5.115841126518573707e-03 9.998424866538090372e-01 2.115339904827197692e+00
# 0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00 1.000000000000000000e+00

# /ego_pose/000.txt
# 1.702781963104923468e-01 -9.853720322939264475e-01 -6.877051270909139216e-03 -3.329700242540837644e+04
# 9.852628239263193644e-01 1.701362829465725146e-01 1.762988978577055901e-02 3.920061360832751961e+04
# -1.620196438645718495e-02 -9.777688789335804709e-03 9.998209305430442173e-01 -6.259700000000000131e+01
# 0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00 1.000000000000000000e+00
import numpy as np
import os
from decimal import Decimal

import sys
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import get_file_paths_in_directory
from utils import rotation_matrix_to_quaternion
from scipy.spatial.transform import Rotation as R
# OpenCV to Dataset coordinate transformation
# opencv coordinate system: x right, y down, z front
# waymo coordinate system: x front, y left, z up
OPENCV2DATASET = np.array(
    [[0, 0, 1, 0], [-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, 1]]
)

# extrinsics/0.txt
cam_to_ego = np.array([
    [ 9.998362731902032952e-01, -6.126490657911932460e-03, 1.702624225551873857e-02, 1.538666713905354921e+00],
    [ 6.212629204228849004e-03, 9.999681466335748059e-01, -5.010883812664571751e-03, -2.493885762968131928e-02],
    [ -1.699500077951916072e-02, 5.115841126518573707e-03, 9.998424866538090372e-01, 2.115339904827197692e+00],
    [ 0.000000000000000000e+00,  0.000000000000000000e+00,  0.000000000000000000e+00, 1.000000000000000000e+00]
])
cam_to_ego = cam_to_ego @ OPENCV2DATASET

# TODO
output_file = "/home/zmh/Codes/dataConvert/test/data/images.txt"
ego_pose_dir = '/home/zmh/data/waymo/processed/training/023/ego_pose'
ego_pose_name = get_file_paths_in_directory(ego_pose_dir)
index = '0'
lines = [] # 记录数据
ego_to_world_start = np.loadtxt('/home/zmh/data/waymo/processed/training/023/ego_pose/000.txt', dtype=str)
ego_to_world_start = np.array([[Decimal(value) for value in row] for row in ego_to_world_start], dtype=object).astype(float)
for idx, ego_pose_file in enumerate(ego_pose_name, start=1):
    # print("------  读取外参文件：" + str(ego_pose_file) + "  ---------")
    ego_to_world_current = np.loadtxt(ego_pose_file, dtype=str)
    # 将字符串转换为 Decimal 数值类型
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
    # print(quaternion)

    # 提取平移向量 (最后一列的前三行)
    T = _cam_to_ego[:3, 3]
    T = [float(t) for t in T]
    # print("平移向量:")
    # print(T)

    filename = os.path.basename(ego_pose_file)
    filename_wo_ext = os.path.splitext(filename)[0]
    imgname = filename_wo_ext + '_' + index + '.jpg'

    line = f"{idx} {' '.join(map(str, quaternion))} {' '.join(map(str, T))} {idx} {imgname}\n"
    lines.append(line)

# 将所有数据写入 images.txt
with open(output_file, "w") as f:
    f.write("\n".join(lines))

print(f"所有数据已写入 {output_file}")