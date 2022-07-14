# 3D Reconstruction

使用Colmap+CasMVSVet实现输入图片输出3D模型的端到端三维重建。  
Colmap完成特征提取、特征匹配、稀疏重建以及图像矫正，输出相机内外参和稀疏点云。  
CasMVSNet将Colmap输出作为神经网络输入来估计深度图，利用深度图进行稠密点云估计和网格重建。

## 硬件环境
- OS: Ubuntu 20.04
- GPU: Nvidia GPU CUDA >= 11.6 （在RTX 2080 Ti 12G上进行测试）
## 软件
python==3.8  
python相关依赖见requirements,可使用下列命令安装`pip install -r requirements.txt`  
安装implace-ABN: `pip install inplace-abn`
## Colmap
根据项目步骤下载编译安装，在终端输入命令 \
    `colmap gui`
若弹出colmap可视化界面则说明安装成功。\
[项目链接](https://github.com/colmap/colmap)
[文档](http://colmap.github.io/)

## CasMVSNet
[项目链接](https://github.com/kwea123/CasMVSNet_pl)


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
#### Colmap
首先运行脚本 ColmapPipeline.py 进行Colmap重建（需要指定输入工程文件夹路径） \
例如 \
`python ColmapPipeline.py --project_path /home/yuda/book_store \

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
#### 准备CasMVSNet数据
dense 文件夹中的images中的图片和sparse中的3个txt文件经过colmap2mvsnet.py转换作为CasMVSNet的输入：  
`python colmap2mvsnet.py --dense_folder data/book_store/dense --max_d 192 --interval_scale 1.06`
- --dense_folder: 需要以我们的dense_folder作为地址，里面必须包含sparse文件夹
- --max_d: 最大估计的离散深度采样区间数，因为MVSNet是按照平面扫描原理进行深度估计的，所以深度是离散采样的，一般设定为192个深度采样区间。
- --interval_scale:表示每个深度区间的大小，默认为1.06(mm)。
- 深度估计范围：已知深度最小值depth_min,则深度最大值满足：depth_max=depth_min+(interval_scale*depth_interval)*(max_d-1)  
**注意**：我们需要估计自采数据的深度范围，以保证在深度采样区间内能对目标场景进行有效的深度估计。举个例子，如果自采数据的深度范围为45cm – 80cm，那么我们用于深度估计的区间范围应该是从45 – 80cm。此时如果我们设定的深度区间为0 – 35cm，那么估计出来的深度图肯定是错误的。所以对于自采数据，需要尝试不同的深度区间，以找到合适的取值范围。  
对于测试数据，需要把数据集整理为tanks的结构（见data文件夹的结构，其中*all_list.txt*文件保存场景名称）然后到*datasets->tanks.py*中手动增加场景（见代码中book_store的示例，估计深度时depth_interval这个参数非常重要，一般可以先设置为0.02左右看看效果，如果没有太大问题再进行微调。  
data数据结构：
```
data
|   all_list.txt
|   
|______book_store
       |   pair.txt
       |   
       |______cams
       |      |   00000000_cam.txt
       |      |   ......
       |
       |——————images
              |    00000000.jpg
              |    ......
```
#### CasMVSNet重建
```
python eval.py \
    --dataset_name tanks \
    --root_dir data/ \
    --split all \
    --ckpt_path ckpts/blended/epoch.15.ckpt \
    --num_groups 8 --depth_interval 192.0
```
此处神经网络模型是使用[Blended](https://github.com/YoYo000/BlendedMVS)数据集训练得到的，若要训练自己的模型需要RGB和对应深度图。  
输出在results中查看点云和深度图
#### 调参
最终点云效果好不好主要还是看拍摄的图片质量(图片重叠度高，数量多，表面都能覆盖到的话效果就好)以及深度图过滤融合(confidence，min_geo_consistent这两个参数可以多试试，输入图片少的情况下conf设置比较高的话生成的点云就会比较少，重建表面会有空洞，可以尝试设置低一点。min_geo_consistent设置高一点也会生成更多的点，但相对的会有更多噪点)
#### 点云重建为网格
使用的是泊松技术进行重建，超参数为depth。`python generate_mesh.py --root_dir /home/bs/CasMVSNet/results/tanks/points --depth`   
### 模型查看与后处理
使用[Meshlab](https://www.meshlab.net/)来进行模型的查看与后处理\
主要是裁减不需要的网格以及进行减面操作\
减面：filters->Remeshing,simplification and Reconstruction->simplification:Quadric Edge Collapse Decimation(with texture)\
减面不建议超过50%否则大大影响模型精度。