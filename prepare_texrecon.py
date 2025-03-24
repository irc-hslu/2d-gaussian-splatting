import os
from tqdm import tqdm
from argparse import ArgumentParser
from PIL import Image


# Use colmap model-converter to convert model to .cam files and create copy of images

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Prepare TexRecon script parameters")

    parser.add_argument("--input_dir", required=True, type=str, help="Input directory")
    parser.add_argument("--output_dir", default="texrecon", type=str, help="Output directory")
    parser.add_argument("--resolution", "-r", default=-1, type=int, help="Resolution of the images to be saved. If -1, the original resolution is used.")
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
    if args.resolution == -1:
        os.system(f"cp {images_dir}/* {output_images_dir}")
    else:
        for img_name in tqdm(os.listdir(images_dir)):
            img_path = os.path.join(images_dir, img_name)
            img = Image.open(img_path)
            if img.width > img.height:
                img = img.resize((args.resolution, int(args.resolution * img.height / img.width)))
            else:
                img = img.resize((int(args.resolution * img.width / img.height), args.resolution))
            img.save(os.path.join(output_images_dir, img_name))


    print(f"Processing complete. Results saved to {output_dir}")