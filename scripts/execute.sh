#!/bin/bash

if [ "$#" -eq 2 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r "$1" --num-gpus "$2"
elif [ "$#" -eq 4 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r "$1" --num-gpus "$2" --dbox-token "$3" --dbox-dir "$4"
else
    echo Incorrect number of arguments >&2
fi
