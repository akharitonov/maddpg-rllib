#!/bin/bash

if [ "$#" -eq 1 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r 10 --num-gpus "$1"
elif [ "$#" -eq 3 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r 10 --num-gpus "$1" --dbox-token "$2" --dbox-dir "$3"
else
    echo Incorrect number of arguments >&2
fi
