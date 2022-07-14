import argparse
from email.mime import image
import os
from pathlib import Path, PurePosixPath
# from tkinter import image_names

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
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    print(args.input)
    input_dir   = args.input

    image_names = os.listdir(input_dir)
    scale       = int(args.scale)
    
    show_image  = int(args.show_image)

    for item in tqdm(image_names):

        full_path    = input_dir + item
        print(full_path)
        img          = cv2.imread(full_path)
        width,height = img.shape[1],img.shape[0]
        img_rescaled = cv2.resize(img,(int(width/scale),int(height/scale)))
        
        if show_image == 1:
            cv2.imshow("image",img_rescaled)
            cv2.waitKey()

        output_dir = item
        cv2.imwrite(output_dir, img_rescaled)
