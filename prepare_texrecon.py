import os
import torch
import torchvision
from tqdm import tqdm
import numpy as np
from argparse import ArgumentParser

from utils.render_utils import save_img_u8

# Use colmap model-converter to convert model to .cam files and create copy of images

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Prepare TexRecon script parameters")

    parser.add_argument("--input_dir", required=True, type=str, help="Input directory")
    parser.add_argument("--output_dir", default="texrecon", type=str, help="Output directory")
    args = parser.parse_args()
  
    
    # Create output directories
    output_dir = os.path.join(args.output_dir, "texrecon", "camera_poses")
    model_dir = os.path.join(args.input_dir, "sparse", "0")

    os.makedirs(output_dir, exist_ok=True)

    print("Converting model to .cam files...")
    os.system(f"colmap model_converter --input_path {model_dir} --output_path {output_dir} --output_type cam")

    print("Copying images...")
    images_dir = os.path.join(args.input_dir, "images")
    output_images_dir = os.path.join(args.output_dir, "texrecon", "camera_poses")
    os.makedirs(output_images_dir, exist_ok=True)
    os.system(f"cp {images_dir}/* {output_images_dir}")


    print(f"Processing complete. Results saved to {output_dir}")