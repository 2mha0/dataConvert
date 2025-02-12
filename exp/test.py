import numpy as np
from decimal import Decimal, getcontext
# 将旋转矩阵转换为四元数
# 设置decimal的精度
getcontext().prec = 20

# 定义旋转矩阵
R = np.array([
    [0.04134264043958485, -0.9991446882133515, -0.0008234661664743179],
    [0.0049496488403644985, 0.0010289672835715096, -0.999987221019692],
    [0.9991327674828006, 0.04133803625444092, 0.004987955571800371]
], dtype=Decimal)

# 计算四元数
def rotation_matrix_to_quaternion(R):
    m00, m01, m02 = R[0]
    m10, m11, m12 = R[1]
    m20, m21, m22 = R[2]

    tr = m00 + m11 + m22 + 1  # 迹，加上1保证在0到1之间

    # 如果tr为0就说明w为0，并且除数为0，需要特殊处理
    if tr != 0:
        S = np.sqrt(tr) * 2  # S=4*qw
        qw = 0.25 * S
        qx = (m21 - m12) / S
        qy = (m02 - m20) / S
        qz = (m10 - m01) / S
    else:
        # 选择最大的特征值，这里我们选择m00
        if m00 >= m11 and m00 >= m22:
            S = np.sqrt(1 + m00 - m11 - m22) * 2
            qx = 0.25 * S
            qw = (m21 - m12) / S
            qy = (m01 + m10) / S
            qz = (m02 + m20) / S
        elif m11 > m22:
            S = np.sqrt(1 + m11 - m00 - m22) * 2
            qy = 0.25 * S
            qw = (m02 - m20) / S
            qx = (m01 + m10) / S
            qz = (m12 + m21) / S
        else:
            S = np.sqrt(1 + m22 - m00 - m11) * 2
            qz = 0.25 * S
            qw = (m10 - m01) / S
            qx = (m02 + m20) / S
            qy = (m12 + m21) / S

    return np.array([qw, qx, qy, qz], dtype=Decimal)

# 计算四元数
quaternion = rotation_matrix_to_quaternion(R)

print("四元数 (w, x, y, z):")
print(quaternion)