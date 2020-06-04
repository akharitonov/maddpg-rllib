#!/bin/bash

if [ "$#" -eq 3 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r "$1" --scenario "$2" --num-gpus "$3"
elif [ "$#" -eq 5 ];then
    python experiment.py --temp-dir /ray_temp --local-dir /ray_results --r "$1" --scenario "$2" --num-gpus "$3" --dbox-token "$4" --dbox-dir "$5"
else
    echo Incorrect number of arguments >&2
fi
