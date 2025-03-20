import os
from argparse import ArgumentParser

scenes = ['audimax0.5x', 'audimax1.0x', 'interactionspace0.5x', 'interactionspace1.0x', 'officespace0.5x', 'officespace1.0x', 'peterskapelle0.5x',
              'peterskapelle1.0x', 's1meetingroom0.5x', 's1meetingroom1.0x', 's1outside0.5x']

parser = ArgumentParser(description="Full evaluation script parameters")
parser.add_argument("--skip_training", action="store_true")
parser.add_argument("--skip_rendering", action="store_true")
parser.add_argument("--output_path", default="/data/hslu/eval")
parser.add_argument('--dtu', "-dtu", required=True, type=str)
args, _ = parser.parse_known_args()

all_scenes = []
all_scenes.extend(scenes)


args = parser.parse_args()


if not args.skip_training:
    common_args = " --quiet --depth_ratio 1.0  --test_iterations -1 -r 2 --lambda_dist 1000"
    for scene in scenes:
        source = args.dtu + "/" + scene
        print("python train.py -s " + source + " -m " + args.output_path + "/" + scene + common_args)
        os.system("python train.py -s " + source + " -m " + args.output_path + "/" + scene + common_args)


if not args.skip_rendering:
    all_sources = []
    common_args = " --quiet --depth_ratio 1.0  --skip_train --num_cluster 1 --voxel_size 0.004 --sdf_trunc 0.016 --depth_trunc 3.0"
    for scene in scenes:
        source = args.dtu + "/" + scene
        print("python render.py --iteration 30000 -s " + source + " -m" + args.output_path + "/" + scene + common_args)
        os.system("python render.py --iteration 30000 -s " + source + " -m" + args.output_path + "/" + scene + common_args)


