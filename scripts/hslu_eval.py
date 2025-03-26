import os
from argparse import ArgumentParser

scenes = {
    "alanturing0.5x": {"depth_trunc": 6.5, "mesh_res": 384},
    "alanturing1.0x": {"depth_trunc": 6.5, "mesh_res": 384},
    "audimax0.5x": {"depth_trunc": 6.5, "mesh_res": 384},
    "audimax1.0x": {"depth_trunc": 6.5, "mesh_res": 384},
    "interactionspace0.5x": {"depth_trunc": 15, "mesh_res": 512},
    "interactionspace1.0x": {"depth_trunc": 15, "mesh_res": 512},
    "officespace0.5x": {"depth_trunc": 30, "mesh_res": 1024},
    "officespace1.0x": {"depth_trunc": 30, "mesh_res": 1024},
    "peterskapelle0.5x": {"depth_trunc": 10, "mesh_res": 512},
    "peterskapelle1.0x": {"depth_trunc": 10, "mesh_res": 512},
    "s1meetingroom0.5x": {"depth_trunc": 6.5, "mesh_res": 384},
    "s1meetingroom1.0x": {"depth_trunc": 6.5, "mesh_res": 384},
    "s1outside0.5x": {"unbounded": True, "mesh_res": 1024},
    "s1outside1.0x": {"unbounded": True, "mesh_res": 1024},
}




parser = ArgumentParser(description="Full evaluation script parameters")
parser.add_argument("--skip_training", action="store_true")
parser.add_argument("--skip_rendering", action="store_true")
parser.add_argument("--skip_texrecon_preparation", action="store_true")
parser.add_argument("--skip_texrecon", action="store_true")
parser.add_argument("--output_path", default="/data/hslu/eval")
parser.add_argument('--dtu', "-dtu", required=True, type=str)
args, _ = parser.parse_known_args()


args = parser.parse_args()


for scene in scenes.keys():
    print("Processing scene " + scene)
    train_args = " --quiet --test_iterations -1"
    # Used values from tnt large scenes. Cannot use mesh_res 1024 as it is too large for the CPU memory (could be optimized).
    #rendering_args = " --quiet --skip_train --skip_test --depth_trunc 12 --voxel_size 0.025 --skip_vertex_colors" #--voxel_size 0.004 --sdf_trunc 0.016 --mesh_res 1024 
    #rendering_args = " --quiet --skip_train --skip_test --depth_trunc 12 --voxel_size 0.025 --skip_vertex_colors" #--voxel_size 0.004 --sdf_trunc 0.016 --mesh_res 1024 
    if "unbounded" in scenes[scene].keys():
        rendering_args = " --quiet --skip_train --skip_test --skip_vertex_colors --unbounded --mesh_res " + str(scenes[scene]["mesh_res"])
    else:
        rendering_args = " --quiet --skip_train --skip_test --depth_trunc " + str(scenes[scene]["depth_trunc"]) + " --skip_vertex_colors --mesh_res " + str(scenes[scene]["mesh_res"]) 
    source = args.dtu + "/" + scene

    if not args.skip_training:
        print("python train.py -s " + source + " -m " + args.output_path + "/" + scene + train_args)
        os.system("python train.py -s " + source + " -m " + args.output_path + "/" + scene + train_args)
    
    if not args.skip_rendering:
        print("python render.py --iteration 30000 -s " + source + " -m" + args.output_path + "/" + scene + rendering_args)
        os.system("python render.py --iteration 30000 -s " + source + " -m" + args.output_path + "/" + scene + rendering_args)

    if not args.skip_texrecon_preparation:
        print("python prepare_texrecon.py --input_dir " + source + " --output_dir " + args.output_path + "/" + scene + " --resolution 1600")
        os.system("python prepare_texrecon.py --input_dir " + source + " --output_dir " + args.output_path + "/" + scene + " --resolution 1600")
        # texrecon ./images ./fused_mesh.ply ./textured_mesh --outlier_removal=gauss_clamping --data_term=area --no_intermediate_results

    if not args.skip_texrecon:
        texture_images_and_cameras = args.output_path + "/" + scene + "/texrecon/camera_poses"
        if "unbounded" in scenes[scene].keys():
            texturing_input_mesh = args.output_path + "/" + scene + "/train/ours_30000/fuse_unbounded_post.ply"
            textured_mesh_output = args.output_path + "/" + scene + "/texrecon/textured_mesh/fuse_unbounded_post_textured"
        else:
            texturing_input_mesh = args.output_path + "/" + scene + "/train/ours_30000/fuse_post.ply"
            textured_mesh_output = args.output_path + "/" + scene + "/texrecon/textured_mesh/fuse_post_textured"
        os.makedirs(args.output_path + "/" + scene + "/texrecon/textured_mesh", exist_ok=True)
        # remove tmp files
        os.system("rm -rf " + args.output_path + "/" + scene + "/texrecon/textured_mesh/tmp")
        print("texrecon " + texture_images_and_cameras + " " + texturing_input_mesh + " " + textured_mesh_output + " --outlier_removal=gauss_clamping --data_term=area --no_intermediate_results")
        os.system("texrecon " + texture_images_and_cameras + " " + texturing_input_mesh + " " + textured_mesh_output + " --outlier_removal=gauss_clamping --data_term=area --no_intermediate_results")

    
    
