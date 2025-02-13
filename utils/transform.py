import numpy as np
from decimal import Decimal

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