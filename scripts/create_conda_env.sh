#!/bin/bash

source ~/miniconda/etc/profile.d/conda.sh
conda create -y --name maddpg-rllib python=3.6
conda activate maddpg-rllib

#pip install --progress-bar off numpy==1.18.1
#pip install --progress-bar off tensorflow==1.13.2
pip install --progress-bar off tensorflow-gpu==1.13.2
pip install --progress-bar off psutil
pip install --progress-bar off tabulate==0.8.6
pip install --progress-bar off -U https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-0.8.0.dev3-cp36-cp36m-manylinux1_x86_64.whl
pip install --progress-bar off requests

git clone https://github.com/akharitonov/multiagent-particle-envs.git /code/MPE

cd /code/MPE
pip install --progress-bar off -e .

cd /code
pip install --progress-bar off opencv-python==4.1.0.25
pip install --progress-bar off pandas==0.25.1
pip install --progress-bar off setproctitle==1.1.10
pip install --progress-bar off box2d-py
pip install --progress-bar off dropbox

conda deactivate