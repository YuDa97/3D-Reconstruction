import os
import subprocess
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Colmap+OpenMVS完成重建,输入图片,Colmap完成特征提取,特征匹配,稀疏重建,图像矫正,将结果输出到OpenMVS.\
                                                    OpenMVS进行稠密点云重建,粗略网格重建,精细网格重建,材质重建,输出.obj模型文件")
    
    parser.add_argument("--project_path", default="/home/bs/colmap/data/seven_hotel_copy", help="工程文件夹路径.")
    parser.add_argument("--Open_MVS_bin", default="/home/bs/openMVS_build/bin", help="Open_MVS编译后生成的可执行程序目录.")
    parser.add_argument("--Output_path", default="/home/bs/colmap/data/seven_hotel_copy/dense", help="模型输出路径")
    args = parser.parse_args()
    return args

def run_shell(cmd):
    subprocess.run(cmd, shell = True)


if __name__ == "__main__":
    args = parse_args()
    
    if not os.path.exists(args.project_path+"/images"):
        print("工程目录%S下没有images文件!" % (args.project_path))
    else:
        # 特征提取
        run_shell("colmap feature_extractor \
                    --database_path %s \
                    --image_path %s" %  
                    (args.project_path+"/database.db",args.project_path+"/images"))
        # 特征匹配 
        run_shell("colmap exhaustive_matcher\
            --database_path %s" %  
            (args.project_path+"/database.db"))
        # 稀疏重建
        os.mkdir(args.project_path+"/sparse")
        run_shell("colmap mapper \
                    --database_path %s \
                    --image_path %s \
                    --output_path %s" %  
                    (args.project_path+"/database.db", \
                    args.project_path+"/images", \
                    args.project_path+"/sparse"))
        # 去除图片畸变
        os.mkdir(args.project_path+"/dense")
        run_shell("colmap image_undistorter \
                    --image_path %s \
                    --input_path %s \
                    --output_path %s \
                    --output_type COLMAP " %  
                    (args.project_path+"/images", \
                    args.project_path+"/sparse/0", \
                    args.project_path+"/dense"))
        # dense工程文件.bin转.txt
        run_shell("colmap model_converter \
                    --input_path %s \
                    --output_path %s \
                    --output_type TXT" %  
                    (args.project_path+"/dense/sparse", \
                    args.project_path+"/dense/sparse"))
        print("=====================================================")
        print("COLMAP部分完成!")
        print("=====================================================")
        

    # OpenMVS
    if not os.path.exists(args.project_path+"/dense"):
        print("缺少dense文件!")
    else:
        os.chdir(args.Open_MVS_bin)
        # 将colmap工程文件转为OpenMVS的.mvs文件

        run_shell("./InterfaceCOLMAP -i %s \
            -o %s \
            --image-folder %s" %  
            (args.project_path+"/dense", \
                args.project_path+"/dense/scene.mvs", \
                args.project_path+"/dense/images"))
        # 稠密点云重建
        run_shell("./DensifyPointCloud \
            -i %s \
            -o %s \
            -w %s" %  
            (args.project_path+"/dense/scene.mvs", \
            args.project_path+"/dense/dense_scene.mvs", \
            args.project_path+"/dense"))
        # 粗略mesh重建
        run_shell("./ReconstructMesh \
            -i %s \
            -o %s \
            -w %s" %  
            (args.project_path+"/dense/dense_scene.mvs", \
            args.project_path+"/dense/rough_scene.mvs", \
            args.project_path+"/dense"))
        # 精细mesh重建
        run_shell("./RefineMesh \
            -i %s \
            -o %s \
            -w %s" %  
            (args.project_path+"/dense/rough_scene.mvs", \
            args.project_path+"/dense/refine_scene.mvs", \
            args.project_path+"/dense"))
        
        # 材质重建
        run_shell("./TextureMesh \
            -w %s \
            --export-type obj \
            --input-file %s \
            --output-file %s" %  
            (args.project_path+"/dense", \
            args.project_path+"/dense/refine_scene.mvs", \
            args.Output_path))
        print("=====================================================")
        print("重建完成!")
        print("=====================================================")
        

