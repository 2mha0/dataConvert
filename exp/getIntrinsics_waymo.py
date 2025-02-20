# 生成相机内参：intrinsics目录转换为cameras.txt文件
import numpy as np
import os
from PIL import Image
import re

import sys
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import get_file_paths_in_directory

# TODO
index = '0'
output_file = "/home/zmh/Codes/dataConvert/test/data/cameras.txt"
extrinsics_dir = '/home/zmh/data/waymo/processed/training/023/extrinsics'
intrinsics_dir = '/home/zmh/data/waymo/processed/training/023/intrinsics'
img_dir = '/home/zmh/data/waymo/processed/training/023/images'
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
# 使用图片文件名来循环遍历：
for idx, img_file in enumerate(img_name, start=1):
    filename = os.path.basename(img_file)
    filename_wo_ext = os.path.splitext(filename)[0]
    # print(filename_wo_ext) # "190_0", "190_1", "190_2"等

    # 使用正则表达式来匹配 "_" 后面的数字
    pattern = r'_(\d+)'
    numbers = re.search(pattern, filename_wo_ext).group(1)
    if numbers == index:
        # 通过后面的数字来确定是哪个摄像头，从而知道这一行使用哪一个内参文件
        _intrinsics = intrinsics[int(numbers)] # 文件命名是从0开始

        img_path = img_dir + '/' + filename_wo_ext + '.jpg'
        img = Image.open(img_path)
        # 获取图片分辨率 (宽度, 高度)
        width, height = img.size
        # print(f"width:{width}    height{height}")

        line = f"{_idx} {'PINHOLE'} {width} {height} {' '.join(map(str, _intrinsics))}"
        _idx += 1
        lines.append(line)

# 将所有数据写入 images.txt
with open(output_file, "w") as f:
    f.write("\n".join(lines))

print(f"所有数据已写入 {output_file}")