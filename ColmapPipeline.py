import os
import subprocess
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Colmap+OpenMVS完成重建,输入图片,Colmap完成特征提取,特征匹配,稀疏重建,图像矫正,将结果输出到OpenMVS.\
                                                    OpenMVS进行稠密点云重建,粗略网格重建,精细网格重建,材质重建,输出.obj模型文件")
    
    parser.add_argument("--project_path", default="/home/bs/colmap/data/seven_hotel_copy", help="工程文件夹路径.")
    
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
        


        

