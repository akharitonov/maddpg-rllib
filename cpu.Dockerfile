FROM tensorflow/tensorflow:1.13.2-py3

RUN apt-get update
RUN apt-get install -y git libsm6 libxext6 libxrender-dev ssh rsync

# Ray rllib
RUN apt-get install -y libxrender1
RUN pip install --progress-bar off psutil
RUN pip install --progress-bar off tabulate==0.8.6
RUN pip install --progress-bar off -U https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-0.8.0.dev3-cp36-cp36m-manylinux1_x86_64.whl
RUN pip install --progress-bar off requests

RUN mkdir p /code
WORKDIR /code
ADD . .
# Multi-agent particle environments (fork of the original, minimal compatibility fixes)
RUN git clone https://github.com/akharitonov/multiagent-particle-envs.git ./MPE
WORKDIR ./MPE
RUN pip install --progress-bar off -e .
WORKDIR /code

# Dependencies
RUN pip install --progress-bar off opencv-python==4.1.0.25
RUN pip install --progress-bar off pandas==0.25.1
RUN pip install --progress-bar off setproctitle==1.1.10
# optional MPE dependency
RUN pip install --progress-bar off box2d-py

# Uploader dependencies
RUN pip install --progress-bar off dropbox

# Temporary direcotory for RAY
RUN mkdir -p /ray_temp
# Results directory
RUN mkdir -p /ray_results

VOLUME ["/ray_temp", "/ray_results"]

RUN chmod 777 ./scripts/execute.sh

# Run experiments
ENTRYPOINT /code/scripts/execute.sh ${repeats} ${scenario} 0 ${dboxtoken} ${dboxdir}
