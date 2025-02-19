# dataConvert
drivestudio中的数据转换为原始的3DGS数据格式

**drivestudio中Nuscenes数据格式**：

```shell
nuscenesData/
    └── processed_10Hz
        └── mini
            ├── 000
                ├── dynamic_masks
                ├── extrinsics
                ├── fine_dynamic_masks
                ├── humanpose
                ├── images
                ├── instances
                ├── intrinsics
                ├── lidar
                ├── lidar_pose
                └── sky_masks
            ├── 002
                ├── ……
                ├── ……
                ├── ……
            ├── 003
            ├── 004
            └── ……
```

**drivestudio中Waymo数据格式**：

```shell
waymo/
└── processed
    └── training
        ├── 023
            ├── dynamic_masks
            ├── ego_pose
            ├── extrinsics
            ├── fine_dynamic_masks
            ├── frame_info.json
            ├── humanpose
            ├── images
            ├── instances
            ├── intrinsics
            ├── lidar
            └── sky_masks
        ├── 114
        ├── 172
        ├── 327
        ├── 552
        ├── 621
        ├── 703
        └── 788
```





**项目结构**：

```shell
dataConvert/
├── exp         			 # 实验
│   ├── data				 # 生成数据
│   │   ├── cameras.txt		  # 相机内参
│   │   ├── images.txt		  # 相机外参
│   │   └── points3D.ply	  # 点云
│   ├── getExtrinsics.py	  # 实验：生成相机外参，extrinsics目录转换为images.txt文件
│   ├── getIntrinsics.py	  # 实验：生成相机内参，intrinsics目录转换为cameras.txt文件
│   ├── mergePointClouds.py	   # 实验：合并点云 
│   └── test.py				  # 实验：4*4的变换矩阵得到images.txt文件
├── README.md
├── test					 # 测试
│   ├── data
│   │   ├── cameras.txt		  # 测试结果，生成的相机内参
│   │   ├── images.txt		  # 测试结果，生成的相机外参
│   │   └── points3D.ply	  # 测试结果，生成的点云
│   └── test_utils.py		  # 单元测试
└── utils					 # 一些工具程序
    ├── convert_tools.py	   # 数据转换工具
    ├── file_utils.py		   # 系统文件操作工具
    ├── __init__.py
    └── transform.py		   # 格式转换工具
```



