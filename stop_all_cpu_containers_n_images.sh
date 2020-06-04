#!/bin/bash

# Prefix for container names
PFX=${1:-""}


for i in {1..5}
do
   docker container stop ${PFX}maddpg-rllib_$i
done
