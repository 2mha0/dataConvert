import sys
import argparse
from pathlib import Path
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import getExtrinsics_all, getIntrinsics_all, mergePointClouds, getExtrinsics_by_index, getIntrinsics_by_index
from utils import get_sorted_directories

# 创建colmap的目录格式：'sparse/0'
def create_colmap_directories(path):
    # 定义基础路径
    base_path = Path(path)
    # 创建sparse目录
    sparse_path = base_path / "sparse"
    sparse_path.mkdir(parents=True, exist_ok=True)  # 使用parents=True确保所需的父目录存在；exist_ok=True避免目录已存在时抛出异常

    # 在sparse目录中创建名为0的目录
    zero_path = sparse_path / "0"
    zero_path.mkdir(parents=True, exist_ok=True)
    return {
        "sparse_path": str(sparse_path),
        "zero_path": str(zero_path)
    }

def main():
    # 创建解析器对象
    parser = argparse.ArgumentParser(description="处理输出路径和索引值")
    
    parser.add_argument('input_path', type=str, help='指定输入数据目录，该目录下应该会有很多场景')
    parser.add_argument('output_path', type=str, help='指定输出文件或目录的路径')
    parser.add_argument('index', type=str, help='指定摄像头索引，多个摄像头合用中文顿号分割')
    
    # 解析命令行参数
    args = parser.parse_args()
    # 访问命令行参数
    input_path = args.input_path
    output_path = args.output_path
    cam_index = args.index
    
    print(f"input_path: {input_path}")
    print(f"output_path: {output_path}")
    print(f"index: {cam_index}") 

    # 依次去遍历每个场景
    scene_index = get_sorted_directories(input_path)
    for index in scene_index:
        data_path = input_path + '/' + index


        path_dict = create_colmap_directories(output_path + '/' + index)
        imagesPath = path_dict['zero_path'] + '/images.txt'
        camerasPath = path_dict['zero_path'] + '/cameras.txt'
        pointsPath = path_dict['zero_path'] + '/points3D.ply'

        # print("*****************************")
        # print(f"===========data_path=========={data_path}")
        # print(f"===========imagesPath=========={imagesPath}")
        # print(f"===========camerasPath=========={camerasPath}")
        # print(f"===========pointsPath=========={pointsPath}")

        getExtrinsics_by_index(data_path, imagesPath, cam_index)
        getIntrinsics_by_index(data_path, camerasPath, cam_index)
        mergePointClouds(data_path, pointsPath)
            


if __name__ == "__main__":
    # python convert.py /home/zmh/Codes/nuscenesData/mini  /home/zmh/Codes/dataConvert/tools/nuscenes_colmap  0
    main()
    # inputPath = '/home/zmh/Codes/nuscenesData/000'
    # basePath = ''
    # imagesPath = '/images.txt'
    # camerasPath = '/cameras.txt'
    # pointsPath = '/points3D.ply'
    # 测试整体：所有相机索引
    # getExtrinsics_all(dataPath, imagesPath)
    # getIntrinsics_all(dataPath, camerasPath)
    # mergePointClouds(dataPath, pointsPath)
    # 测试指定相机索引：索引传'0、1、2'或单个'0'都可
    # index = '0'
    # getExtrinsics_by_index(inputPath, imagesPath, index)
    # getIntrinsics_by_index(inputPath, camerasPath, index)
    # mergePointClouds(inputPath, pointsPath)
