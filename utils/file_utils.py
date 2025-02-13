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