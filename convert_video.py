import argparse
from email.mime import image
import os
from pathlib import Path, PurePosixPath

import numpy as np
import json
import sys
import math
import cv2
import os
import shutil

from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Convert image into a different format. By default, converts to our binary fp16 '.bin' format, which helps quickly load large images.")
    parser.add_argument("--input", default="", help="Path to the image to convert.")
    parser.add_argument("--output", default="", help="Path to the output. Defaults to <input>.bin")
    parser.add_argument("--scale", default=4, help="scale")
    parser.add_argument("--show_image", default=0, help="scale")
    parser.add_argument("--t", default=1, help="Take a picture every t second")
    args = parser.parse_args()
    return args

def process_video(input,output,scale):
    
    cap = cv2.VideoCapture(input)
    cap.open(input)
    fps = cap.get(cv2.CAP_PROP_FPS)		# 视频的帧率FPS
    
    T = int(t * fps)
    total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)	# 视频的总帧数
    print('采样间隔时间:', t)
    cnt = 0
    image_num = 0
    for i in range(int(total_frame)):
        ret = cap.grab() #捕获一帧
        if not ret:
            print("Error grabbing frame from movie!")
            break
        if i % T == 0: #每T秒选取一帧
            ret, frame = cap.retrieve() #进行解码
            if ret:
                cnt += 1
                width,height = frame.shape[1],frame.shape[0]
                img_rescaled = cv2.resize(frame,(int(width/scale),int(height/scale))) #下采样
                output_dir = output + "/image_c" + str(cnt) + ".jpg"
                image_num  += 1
                cv2.imwrite(output_dir,img_rescaled)
                if show_image == 1:
                    cv2.imshow("image",img_rescaled)
                    cv2.waitKey(10)
                # key = cv2.waitKey(1)
                
            else:
                print("Error retrieving frame from movie!")
                break
    print('采样得到的图片总数:', image_num)
        
if __name__ == "__main__":
    args = parse_args()
    scale       = int(args.scale)
    show_image  = int(args.show_image)
    t = float(args.t)
    # make dir
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    process_video(args.input,args.output,scale)
