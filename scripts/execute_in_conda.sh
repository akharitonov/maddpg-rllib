#!/bin/bash

source ~/miniconda/etc/profile.d/conda.sh
conda activate maddpg-rllib

if [ "$#" -eq 2 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r "$1" --num-gpus "$2"
elif [ "$#" -eq 4 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r "$1" --num-gpus "$3" --dbox-token "$4" --dbox-dir "$5"
else
    echo Incorrect number of arguments >&2
fi
