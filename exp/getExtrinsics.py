# 生成相机外参：extrinsics目录转换为images.txt文件

# 通过四元数获得旋转矩阵
import numpy as np
import os
from decimal import Decimal

import sys
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import get_file_paths_in_directory
from utils import rotation_matrix_to_quaternion

# TODO
output_file = "/home/zmh/Codes/dataConvert/exp/data/images.txt"
extrinsics_dir = '/home/zmh/Codes/nuscenesData/000/extrinsics'
extrinsics_name = get_file_paths_in_directory(extrinsics_dir)
lines = [] # 记录数据
for idx, extrinsics_file in enumerate(extrinsics_name, start=1):
    print("------  读取外参文件：" + str(extrinsics_file) + "  ---------")
    extrinsics_matrix_str = np.loadtxt(extrinsics_file, dtype=str)
    # 将字符串转换为 Decimal 数值类型
    extrinsics_matrix = np.array([[Decimal(value) for value in row] for row in extrinsics_matrix_str], dtype=object).astype(float)

    # 这里需要计算 extrinsics_matrix 的逆矩阵
    extrinsics_matrix_inv = np.linalg.inv(extrinsics_matrix)
    R = extrinsics_matrix_inv[:3, :3]
    # 计算四元数
    quaternion = rotation_matrix_to_quaternion(R)

    print("四元数 (w, x, y, z):")
    # print([float(q) for q in quaternion])  # 转换回 float 进行打印
    quaternion = [float(q) for q in quaternion]
    print(quaternion)

    # 提取平移向量 (最后一列的前三行)
    T = extrinsics_matrix_inv[:3, 3]
    T = [float(t) for t in T]
    print("平移向量:")
    print(T)

    filename = os.path.basename(extrinsics_file)
    filename_wo_ext = os.path.splitext(filename)[0]
    imgname = filename_wo_ext + '.jpg'

    line = f"{idx} {' '.join(map(str, quaternion))} {' '.join(map(str, T))} {idx} {imgname}\n"
    lines.append(line)

# 将所有数据写入 images.txt
with open(output_file, "w") as f:
    f.write("\n".join(lines))

print(f"所有数据已写入 {output_file}")
    