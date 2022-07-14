import numpy as np
import open3d as o3d
from argparse import ArgumentParser
import os

from torch import poisson

def get_opts():
    parser = ArgumentParser()
    parser.add_argument('--root_dir', type=str,
                        default='/home/bs/CasMVSNet/results/tanks/points',
                        help='root directory of point cloud (.ply) and storing mesh ')
    parser.add_argument('--depth', type=int,
                        default=10,
                        help='A higher depth value means a mesh with more details(对于大场景不建议大于10)')
    
    return parser.parse_args()
if __name__ == "__main__":
    args = get_opts()
    ply = o3d.io.read_point_cloud(args.root_dir)
    print('Read point cloud file done!')
    ply.estimate_normals() # 计算法线
    '''
    泊松重建
    '''
    poisson_mesh = \
        o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            ply, depth=args.depth, width=0, scale=1.1, linear_fit=False
        )[0]
    print("poisson reconstruct done!")
    bbox = ply.get_axis_aligned_bounding_box()
    p_mesh_crop = poisson_mesh.crop(bbox) # 清理边界多余的mesh

    o3d.io.write_triangle_mesh(args.root_dir+"poisson_mesh.ply", p_mesh_crop)
    print("save mesh!")
    
