# 3D Reconstruction

使用Colmap+OpenMVS实现输入图片输出3D模型的端到端三维重建。\
Colmap完成特征提取、特征匹配、稀疏重建以及图像矫正，输出相机内外参和稀疏点云。\
OpenMVS利用Colmap的输出完成稠密重建、网格重建、精细网格重建和材质重建，输出模型和材质文件。

## 硬件环境
OS：Ubuntu 20.04\
GPU：Nvidia GPU (在RTX 2080Ti上进行测试)\
RAM：越大越好(分别在在48G，128G上进行测试)
## 软件
python 3.9.12\
opencv-python 4.5.5.64\
numpy 1.22.4\
meshlab 

## Colmap
根据项目步骤下载编译安装，在终端输入命令 \
    `colmap gui`
若弹出colmap可视化界面则说明安装成功。\
[项目链接](https://github.com/colmap/colmap)
[文档](http://colmap.github.io/)

## OpenMVS 
根据项目步骤下载编译安装，若编译生成的OpenMVS_build/bin中存在7个可执行程序则说明安装成功。\
[项目链接](https://github.com/cdcseacave/openMVS)
[文档](https://github.com/cdcseacave/openMVS/wiki)

## 使用
### 数据准备
若输入为视频： \
    使用 convert_video.py 从视频中截取图片 \
    例如：\
        `python ./convert_video.py --input book_store/videos/DJI_0012.mp4  
                                  --output book_store/images 
                                  --show_image 1 
                                  --scale 1 
                                  --t 1`

若输入直接为图片，要注意图片分辨率是否过大，以370张2K图片(2720*1529)为例，需要至少63G以上RAM才能完成重建。\
若输入图片过多过大，考虑删除图片或者降低图片分辨率，可以使用rescale_images.py对图片进行下采样。\
例：
`python rescale_images.py --input book_store/original_images/ 
			--output book_store/images 
			--scale 2`
            
### 数据存放目录结构
首先创建工程文件夹（以book_store为例)，里面包括存放图片的子文件夹images\
```
book_store
|
|
|______images
       |   image_1.jpg
       |   image_2.jpg
       |   ......
```
### 实施重建
运行脚本 ColmapMvsPipeline.py 进行重建（指定输入工程文件夹路径，模型输出路径，OpenMVS_build中bin文件路径） \
例如 \
`python ColmapMvsPipeline.py --project_path /home/yuda/book_store \
			     --Open_MVS_bin /home/yuda/openMVS_build/bin \
			     --Output_path /home/yuda/book_store`

第一阶段Colmap重建完成后工程目录结构变为:
```
book_store
|   database.db
|
|______images
|       |   image_1.jpg
|       |   image_2.jpg
|       |   ......
|
|_______dense
         |____images
         |    |   image_1.jpg
         |    |   image_2.jpg
         |    |   ......
         |
         |____sparse
         |    |   cameras.txt
         |    |   images.txt
         |    |   points3D.txt
         |    |      ......
         |   
         |____stereo
              |......
```

dense 文件夹中的images中的图片和sparse中的3个txt文件作为OpenMVS的输入\
图片和txt数据统一转换为.mvs格式文件输入到OpenMVS中

第二阶段OpenMVS重建完成后工程目录变为：
```
book_store
|   database.db
|   refine_model.obj
|   refine_model_material_0_map_Kd.jpg
|   refine_model.mtl
|______images
|       |   image_1.jpg
|       |   image_2.jpg
|       |   ......
|
|_______dense
         |  scene.mvs
         |  dense_scene.mvs
         |  rough_mesh.mvs
         |  refine_mesh.mvs
         |  refine_model.mvs
         |  
         |  ......
```
其中refine_model.obj为模型文件，refine_model_material_0_map_Kd.jpg为材质文件，refine_model.mtl为模型与材质的软连接。

### 模型查看与后处理
使用[Meshlab](https://www.meshlab.net/)来进行模型的查看与后处理\
主要是裁减不需要的网格以及进行减面操作\
减面：filters->Remeshing,simplification and Reconstruction->simplification:Quadric Edge Collapse Decimation(with texture)\
减面不建议超过50%否则大大影响模型精度。




