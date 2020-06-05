#!/bin/sh

# Prefix for container names
PFX=${1:-""}

# Dropbox token
DBOX_TOKEN=${2:-""}

# Dropbox folder
DBOX_FOLDER=${3:-"/maddpg_exp"}

REPEATS=${4:-3}

# build the image
docker build -t ${PFX}maddpg-rllib:latest -f cpu.Dockerfile . --no-cache

# run each scenario in a separate container
max=5
for IDX in $(seq 0 $max)
do
    docker run -d -e dboxtoken=${DBOX_TOKEN} -e dboxdir=${DBOX_FOLDER}/scen_${IDX} -e repeats=${REPEATS} -e scenario=${IDX} --name ${PFX}maddpg-rllib_${IDX} \
    -v ${PFX}maddpg-rllib-vtmp_${IDX}:/ray_temp -v ${PFX}maddpg-rllib-vres_${IDX}:/ray_results --shm-size=8gb ${PFX}maddpg-rllib:latest
done
