# dataConvert
drivestudio中的数据转换为原始的3DGS数据格式

* 转换工具在dataConvert/tools目录下，包括两个转换脚本waymoConvert.py和nuscenesConvert.py
* 在dataConvert/tools目录下也包括转好的点云以及内外参文件

waymo数据集转换工具用法：python waymoConvert.py <input> <output> <cam_index>
* <input>：输入路径，指定的目录下应该是场景id
* <output>：输出路径，会自动将所有场景的转换数据写到该目录
* <cam_index>：相机索引列表：索引号之前用中文顿号分割
waymo数据集转换示例：`python waymoConvert.py /home/zmh/data/waymo/processed/training /home/zmh/Codes/dataConvert/tools/waymo_colmap 0、1`

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
├── exp    # 实验
│   ├── data    # 实验生成的数据
│   ├── getExtrinsics_nuscenes.py    # nuscenes和waymo在drivestudio不同，需要分别处理
│   ├── getExtrinsics_waymo.py
│   ├── getIntrinsics_nuscenes.py
│   ├── getIntrinsics_waymo.py
│   ├── merged_downsampled.ply
│   ├── mergePointClouds_nuscenes.py
│   ├── mergePointClouds_waymo.py
│   └── test.py
├── README.md
├── test    # 测试
│   ├── data
│   ├── nuscenes_test.py
│   └── waymo_test.py
├── tools    # 主要的转换工具
│   ├── nuscenesConvert.py    # nuscenes转换工具
│   └── waymoConvert.py       # waymo转换工具
└── utils
    ├── file_utils.py         # 系统文件操作工局
    ├── __init__.py
    ├── nuscenes_convert_tools.py    # nuscenes转换函数
    ├── transform.py                 # 转换脚本
    └── waymo_convert_tools.py       # waymo转换函数
```



