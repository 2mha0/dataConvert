# 生成相机内参：intrinsics目录转换为cameras.txt文件
import numpy as np
import os
from decimal import Decimal
from PIL import Image
import re

def get_file_paths_in_directory(directory):
    # 获取指定路径下的所有文件的完整路径（不包括子目录）
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    file_paths = sorted(file_paths)
    return file_paths

# TODO
output_file = "/home/zmh/Codes/dataConvert/exp/data/cameras.txt"
extrinsics_dir = '/home/zmh/Codes/nuscenesData/000/extrinsics'
intrinsics_dir = '/home/zmh/Codes/nuscenesData/000/intrinsics'
img_dir = '/home/zmh/Codes/nuscenesData/000/images'
extrinsics_name = get_file_paths_in_directory(extrinsics_dir)
# 先读取内参
intrinsics_names = get_file_paths_in_directory(intrinsics_dir)
intrinsics = []
lines = [] # 记录数据
for name in intrinsics_names:
    # 只读取前四行
    _intrinsics = np.loadtxt(name, max_rows=4)
    intrinsics.append(_intrinsics)
print(intrinsics)

# 使用外参的文件名来遍历循环：
for idx, extrinsics_file in enumerate(extrinsics_name, start=1):
    filename = os.path.basename(extrinsics_file)
    filename_wo_ext = os.path.splitext(filename)[0]
    # print(filename_wo_ext) # "190_0", "190_1", "190_2"等

    # 使用正则表达式来匹配 "_" 后面的数字
    pattern = r'_(\d+)'
    numbers = re.search(pattern, filename_wo_ext).group(1)
    # 通过后面的数字来确实是哪个摄像头，从而知道这一行使用哪一个内参文件
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

print(f"所有数据已写入 {output_file}")