FROM tensorflow/tensorflow:1.13.2-gpu-py3

RUN apt-get install -y git

# Ray rllib
RUN apt-get install -y libxrender1
RUN pip install --progress-bar off psutil
#RUN pip install --progress-bar off tabulate==0.8.6
# Running with Ray 0.8.0.dev3, update the version if needed. Compatibility of the scripts might be needed adjutment.
RUN pip install --progress-bar off -U https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-0.8.0.dev3-cp37-cp37m-manylinux1_x86_64.whl
RUN pip install --progress-bar off requests

RUN mkdir p ~/code
RUN cd ~/code
ADD . .
# Multi-agent particle environments (fork of the original, minimal compatibility fixes)
RUN git clone https://github.com/jcridev/multiagent-particle-envs.git ./MPE
RUN cd ./MPE
RUN pip install --progress-bar off -e .
RUN cd ..

# Dependencies
RUN pip install --progress-bar off opencv-python==4.1.0.25
RUN pip install --progress-bar off pandas==0.25.1
RUN pip install --progress-bar off setproctitle==1.1.10
RUN pip install --progress-bar off box2d-py

# Uploader dependencies
RUN pip install --progress-bar off dropbox

# Temporary direcotory for RAY
RUN mkdir p ~/ray_temp
# Results directory
RUN mkdir p ~/ray_results

# Run experiments
CMD python experiments.py --temp-dir ~/ray_temp --local-dir ~/ray_results --r 10 --dbox-token $dboxtoken