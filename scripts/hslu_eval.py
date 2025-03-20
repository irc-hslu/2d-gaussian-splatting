import os
from argparse import ArgumentParser

scenes = ['alanturing0.5x', 'alanturing1.0x',
            'audimax0.5x', 'audimax1.0x', 'interactionspace0.5x', 'interactionspace1.0x', 'officespace0.5x', 'officespace1.0x', 'peterskapelle0.5x',
              'peterskapelle1.0x', 's1meetingroom0.5x', 's1meetingroom1.0x', 's1outside0.5x']

parser = ArgumentParser(description="Full evaluation script parameters")
parser.add_argument("--skip_training", action="store_true")
parser.add_argument("--skip_rendering", action="store_true")
parser.add_argument("--skip_texrecon", action="store_true")
parser.add_argument("--output_path", default="/data/hslu/eval")
parser.add_argument('--dtu', "-dtu", required=True, type=str)
args, _ = parser.parse_known_args()

all_scenes = []
all_scenes.extend(scenes)


args = parser.parse_args()


for scene in scenes:
    train_args = " --quiet --depth_ratio 1.0  --test_iterations -1"
    # Used values from tnt large scenes. Cannot use mesh_res 1024 as it is too large for the CPU memory (could be optimized).
    rendering_args = " --quiet --depth_ratio 1.0  --skip_train --skip_test --depth_trunc 4.5 --mesh_res 256" #--voxel_size 0.004 --sdf_trunc 0.016 
    source = args.dtu + "/" + scene

    if not args.skip_training:
        print("python train.py -s " + source + " -m " + args.output_path + "/" + scene + train_args)
        os.system("python train.py -s " + source + " -m " + args.output_path + "/" + scene + train_args)
    
    if not args.skip_rendering:
        print("python render.py --iteration 30000 -s " + source + " -m" + args.output_path + "/" + scene + rendering_args)
        os.system("python render.py --iteration 30000 -s " + source + " -m" + args.output_path + "/" + scene + rendering_args)

    if not args.skip_texrecon:
        print("python prepare_texrecon.py -s " + source + " -m " + args.output_path + "/" + scene)
        os.system("python prepare_texrecon.py -s " + source + " -m " + args.output_path + "/" + scene)
    
