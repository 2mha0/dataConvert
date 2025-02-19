import sys
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import getExtrinsics_all, getIntrinsics_all, mergePointClouds, getExtrinsics_by_index, getIntrinsics_by_index

if __name__ == "__main__":
    dataPath = '/home/zmh/Codes/nuscenesData/000'
    imagesPath = '/home/zmh/Codes/dataConvert/test/data/images.txt'
    camerasPath = '/home/zmh/Codes/dataConvert/test/data/cameras.txt'
    pointsPath = '/home/zmh/Codes/dataConvert/test/data/points3D.ply'
    # 测试整体：所有相机索引
    # getExtrinsics_all(dataPath, imagesPath)
    # getIntrinsics_all(dataPath, camerasPath)
    # mergePointClouds(dataPath, pointsPath)
    # 测试指定相机索引：索引传'0、1、2'或单个'0'都可
    index = '0'
    getExtrinsics_by_index(dataPath, imagesPath, index)
    getIntrinsics_by_index(dataPath, camerasPath, index)
    mergePointClouds(dataPath, pointsPath)
