import os
import torch
import torchvision
from tqdm import tqdm
import numpy as np
from argparse import ArgumentParser
from scene import Scene
from gaussian_renderer import render, GaussianModel
from arguments import ModelParams, PipelineParams, get_combined_args
from utils.render_utils import save_img_u8

# TODO: Not sure the cameras are being converted correctly!

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Prepare TexRecon script parameters")
    model = ModelParams(parser, sentinel=True)
    pipeline = PipelineParams(parser)
    parser.add_argument("--iteration", default=-1, type=int)
    #parser.add_argument("--resolution", default=1, type=float, help="Resolution scale for camera")
    parser.add_argument("--output_dir", default="texrecon", type=str, help="Output directory")
    parser.add_argument("--skip_mask", action="store_true", help="Skip saving masks")
    args = get_combined_args(parser)
    
    # Create output directories
    output_dir = os.path.join(args.model_path, args.output_dir)
    render_path = os.path.join(output_dir, "render")
    mask_path = os.path.join(output_dir, "mask")
    os.makedirs(render_path, exist_ok=True)
    if not args.skip_mask:
        os.makedirs(mask_path, exist_ok=True)
    
    # Load model
    print("Loading model from " + args.model_path)
    dataset, iteration, pipe = model.extract(args), args.iteration, pipeline.extract(args)
    gaussians = GaussianModel(dataset.sh_degree)
    scene = Scene(dataset, gaussians, load_iteration=iteration, shuffle=False)
    bg_color = [1,1,1] if dataset.white_background else [0, 0, 0]
    background = torch.tensor(bg_color, dtype=torch.float32, device="cuda")
    
    # Process cameras and save renders
    cameras = scene.getTrainCameras()
    print(f"Processing {len(cameras)} cameras...")
    
    for camera in tqdm(cameras):
        camera = camera.to("cuda")
        
        with torch.no_grad():
            render_pkg = render(camera, gaussians, pipe, background)
        
        # Get render outputs
        rendering = render_pkg["render"]
        
        # Get alpha/opacity information
        rendered_opacity = render_pkg["rend_alpha"]
        
        # Get depth information
        rendered_depth = render_pkg["surf_depth"]
        
        # Create invalid mask where opacity is low
        invalid_mask = rendered_opacity < 0.5
        
        # Zero out invalid regions
        rendering_masked = rendering.clone()
        rendering_masked[:, invalid_mask[0]] = 0.
        
        # Save render image
        image_path = os.path.join(render_path, f"{camera.image_name}.png")
        save_img_u8(rendering_masked.permute(1, 2, 0).cpu().numpy(), image_path)
        
        # Save mask
        if not args.skip_mask:
            mask_path_file = os.path.join(mask_path, f"{camera.image_name}.png")
            mask_image = (~invalid_mask[0]).float().cpu().numpy()
            save_img_u8(mask_image, mask_path_file)
        
        # Save camera information
        cam_path = os.path.join(render_path, f"{camera.image_name}.cam")
        
        # Extract camera parameters
        P = camera.world_view_transform.cpu()
        
        # Get intrinsics (focal length, etc.)
        K = torch.zeros((3, 3), dtype=torch.float32)
        K[0, 0] = camera.FoVx
        K[1, 1] = camera.FoVy
        K[0, 2] = camera.image_width / 2 # cx
        K[1, 2] = camera.image_height / 2 # cy
        K[2, 2] = 1.0
        
        # Calculate parameters for texrecon format
        fx = K[0, 0]
        fy = K[1, 1]
        paspect = fy / fx
        width, height = camera.image_width, camera.image_height
        dim_aspect = width / height
        img_aspect = dim_aspect * paspect
        
        if img_aspect < 1.0:
            flen = fy / height
        else:
            flen = fx / width
            
        ppx = K[0, 2] / width
        ppy = K[1, 2] / height
        
        # Write camera file in the required format
        with open(cam_path, 'w') as f:
            s1, s2 = '', ''
            for i in range(3):
                for j in range(3):
                    s1 += str(P[i, j].item()) + ' '
                s2 += str(P[i, 3].item()) + ' '
            f.write(s2 + s1[:-1] + '\n')
            f.write(f"{flen} 0 0 {paspect} {ppx} {ppy}\n")
    
    print(f"Processing complete. Results saved to {output_dir}")