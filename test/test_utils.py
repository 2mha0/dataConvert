import sys
# 将当前路径添加到 sys.path
sys.path.append("/home/zmh/Codes/dataConvert")
from utils import getExtrinsics_all, getIntrinsics_all, mergePointClouds, getExtrinsics_by_index, getIntrinsics_by_index

if __name__ == "__main__":
    dataPath = '/home/zmh/Codes/nuscenesData/000'
    imagesPath = '/home/zmh/Codes/dataConvert/test/data/images.txt'
    camerasPath = '/home/zmh/Codes/dataConvert/test/data/cameras.txt'
    pointsPath = '/home/zmh/Codes/dataConvert/test/data/points3D.ply'
    # getExtrinsics_all(dataPath, imagesPath)
    # getIntrinsics_all(dataPath, camerasPath)
    # mergePointClouds(dataPath, pointsPath)
    index = '0、1、2、3'
    getExtrinsics_by_index(dataPath, imagesPath, index)
    getIntrinsics_by_index(dataPath, camerasPath, index)

