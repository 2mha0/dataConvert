import os

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

def get_files_by_camera_index(directory, camera_index):
    """获取指定相机索引的所有txt文件。
    
    :param directory: 存放txt文件的目录路径。
    :param camera_index: 相机索引（整数）。
    :return: 包含所有匹配文件名的列表。
    """
    matched_files = []
    # 遍历目录中的所有文件和子目录
    for filename in os.listdir(directory):
        # 检查是否为txt文件且符合命名规则
        if filename.endswith(".txt"):
            parts = filename.split('_')
            if len(parts) == 2:
                img_idx, cam_idx = parts
                cam_idx = cam_idx.replace('.txt', '')  # 移除.txt后缀
                # 检查相机索引是否匹配
                if int(cam_idx) == camera_index:
                    matched_files.append((int(img_idx), filename))  # 将图片索引作为整数保存以便排序
    
    # 根据图片索引从小到大排序
    matched_files.sort(key=lambda x: x[0])  # 默认升序排列
    
    # 返回排序后的文件路径列表
    return [os.path.join(directory, item[1]) for item in matched_files]
