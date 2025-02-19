# 逆矩阵对应的四元数: [ 0.11540123  0.70365481 -0.68920135  0.12866224]
# import numpy as np
# from scipy.spatial.transform import Rotation as R

# # 给定的变换矩阵 T
# T = np.array([
#     [-9.402571710430225327e-01, -1.494311642038989758e-02, -3.401369659031778792e-01, 4.107097710569824471e+02],
#     [ 3.397536310584519659e-01,  2.336811486507700542e-02, -9.402241229569952008e-01, 1.179137526706944072e+03],
#     [ 2.199823821968963089e-02, -9.996152432207603411e-01, -1.689505951248902738e-02, 1.491245328572638806e+00],
#     [ 0.000000000000000000e+00,  0.000000000000000000e+00,  0.000000000000000000e+00, 1.000000000000000000e+00]
# ])

# # 计算 T 的逆矩阵
# T_inv = np.linalg.inv(T)
# print(T_inv)

# # 提取逆矩阵中的旋转部分
# rotation_matrix_inv = T_inv[:3, :3]

# # 创建 Rotation 对象，并从旋转矩阵转换得到四元数
# rot_inv = R.from_matrix(rotation_matrix_inv)

# # 获取四元数表示
# quaternion_inv = rot_inv.as_quat()

# print("逆矩阵对应的四元数:", quaternion_inv)


import numpy as np
from scipy.spatial.transform import Rotation as R
# OpenCV to Dataset coordinate transformation
# opencv coordinate system: x right, y down, z front
OPENCV2DATASET = np.array(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
)

# 给定的变换矩阵 T
T = np.array([
    [-9.402571710430225327e-01, -1.494311642038989758e-02, -3.401369659031778792e-01, 4.107097710569824471e+02],
    [ 3.397536310584519659e-01,  2.336811486507700542e-02, -9.402241229569952008e-01, 1.179137526706944072e+03],
    [ 2.199823821968963089e-02, -9.996152432207603411e-01, -1.689505951248902738e-02, 1.491245328572638806e+00],
    [ 0.000000000000000000e+00,  0.000000000000000000e+00,  0.000000000000000000e+00, 1.000000000000000000e+00]
])

# 计算 T 的逆矩阵
T_inv = np.linalg.inv(T)
print(f"===T_inv==={T_inv}")

cam2world = T_inv @ T
print(f"===cam2world==={cam2world}")

cam2world = cam2world @ OPENCV2DATASET
print(f"===cam2world==={cam2world}")

# # 提取逆矩阵中的旋转部分
# rotation_matrix_inv = T_inv[:3, :3]

# # 创建 Rotation 对象，并从旋转矩阵转换得到四元数
# rot_inv = R.from_matrix(rotation_matrix_inv)

# # 获取四元数表示
# quaternion_inv = rot_inv.as_quat()

# print("逆矩阵对应的四元数:", quaternion_inv)