#!/bin/sh

source ~/miniconda3/etc/profile.d/conda.sh
conda activate maddpg-rllib
python experiments.sh  --temp-dir /ray_temp --local-dir /ray_results --r 10 --dbox-token "$1" --dbox-dir "$2"
