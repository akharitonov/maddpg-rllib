#!/bin/bash

# Prefix for container names
PFX=${1:-""}


max=5
for i in $(seq 0 $max)
do
    docker container rm -v ${PFX}maddpg-rllib_$i
    docker volume rm ${PFX}maddpg-rllib-vtmp_$i
    docker volume rm ${PFX}maddpg-rllib-vres_$i
done


docker image rm ${PFX}maddpg-rllib:latest
