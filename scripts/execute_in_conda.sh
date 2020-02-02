#!/bin/bash

source ~/miniconda/etc/profile.d/conda.sh
conda activate maddpg-rllib
python experiment.py  --temp-dir /ray_temp --local-dir /ray_results --r 3 --dbox-token "$1" --dbox-dir "$2"
