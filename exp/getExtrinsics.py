# 生成相机外参：extrinsics目录转换为images.txt文件

# 通过四元数获得旋转矩阵
import numpy as np
import os
from decimal import Decimal

def get_filenames_in_directory(directory):
    # 获取指定路径下的所有文件名（不包括子目录）
    filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    filenames = sorted(filenames)
    return filenames

def get_file_paths_in_directory(directory):
    # 获取指定路径下的所有文件的完整路径（不包括子目录）
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    file_paths = sorted(file_paths)
    return file_paths

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
def rotation_matrix_to_quaternion(R):
    m00, m01, m02 = R[0]
    m10, m11, m12 = R[1]
    m20, m21, m22 = R[2]

    tr = m00 + m11 + m22 + Decimal(1)  # 确保 tr 是 Decimal

    if tr > 0:
        S = (Decimal(2) * tr).sqrt()
        qw = Decimal("0.25") * S
        qx = (m21 - m12) / S
        qy = (m02 - m20) / S
        qz = (m10 - m01) / S
    else:
        if m00 > m11 and m00 > m22:
            S = (Decimal(2) * (Decimal(1) + m00 - m11 - m22)).sqrt()
            qx = Decimal("0.25") * S
            qw = (m21 - m12) / S
            qy = (m01 + m10) / S
            qz = (m02 + m20) / S
        elif m11 > m22:
            S = (Decimal(2) * (Decimal(1) + m11 - m00 - m22)).sqrt()
            qy = Decimal("0.25") * S
            qw = (m02 - m20) / S
            qx = (m01 + m10) / S
            qz = (m12 + m21) / S
        else:
            S = (Decimal(2) * (Decimal(1) + m22 - m00 - m11)).sqrt()
            qz = Decimal("0.25") * S
            qw = (m10 - m01) / S
            qx = (m02 + m20) / S
            qy = (m12 + m21) / S

    return np.array([qw, qx, qy, qz], dtype=object)  # 仍然保持 Decimal

# TODO
output_file = "/home/zmh/Codes/dataConvert/exp/data/images.txt"
extrinsics_dir = '/home/zmh/Codes/nuscenesData/000/extrinsics'
extrinsics_name = get_file_paths_in_directory(extrinsics_dir)
lines = [] # 记录数据
for idx, extrinsics_file in enumerate(extrinsics_name, start=1):
    print("------  读取外参文件：" + str(extrinsics_file) + "  ---------")
    # extrinsics_matrix = np.loadtxt(extrinsics_file, dtype=Decimal)  # 高精度读取
    # # 提取 3×3 旋转矩阵
    # R = np.array(extrinsics_matrix[:3, :3], dtype=Decimal)  # 保留高精度
    extrinsics_matrix = np.loadtxt(extrinsics_file, dtype=str) 
    extrinsics_matrix = np.array([[Decimal(value) for value in row] for row in extrinsics_matrix], dtype=object) 
    R = extrinsics_matrix[:3, :3]
    # 计算四元数
    quaternion = rotation_matrix_to_quaternion(R)

    print("四元数 (w, x, y, z):")
    # print([float(q) for q in quaternion])  # 转换回 float 进行打印
    quaternion = [float(q) for q in quaternion]
    print(quaternion)

    # 提取平移向量 (最后一列的前三行)
    T = extrinsics_matrix[:3, 3]
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
    