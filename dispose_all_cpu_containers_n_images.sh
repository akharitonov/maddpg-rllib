#!/bin/bash

# Prefix for container names
PFX=${1:-""}


for i in {1..5}
do
   docker container rm -v ${PFX}maddpg-rllib_$i
done

docker image rm ${PFX}maddpg-rllib:latest
