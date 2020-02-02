FROM nvidia/cuda:9.0-base-ubuntu16.04

SHELL ["/bin/bash", "-c"]

RUN apt-get update

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    git \
    sudo \
    wget \
    software-properties-common \
    libsm6 \
    libxext6 \
    libxrender-dev


RUN update-ca-certificates

ENV HOME /home
WORKDIR ${HOME}/

# Download Miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    chmod +x miniconda.sh && \
    ./miniconda.sh -b -p ${HOME}/miniconda3 && \
    rm miniconda.sh

ENV PATH ${HOME}/miniconda3/bin:$PATH
ENV CONDA_PATH ${HOME}/miniconda3
ENV LD_LIBRARY_PATH ${CONDA_PATH}/lib:${LD_LIBRARY_PATH}

RUN mkdir p /code
# Temporary direcotory for RAY
RUN mkdir -p /ray_temp
# Results directory
RUN mkdir -p /ray_results

WORKDIR /code
ADD . .
RUN bash ./scripts/create_conda_env.sh


RUN chmod 777 ./scripts/execute_in_conda.sh
RUN find ${CONDA_PATH} -type d -exec chmod 777 {} \;

# Run experiments
ENTRYPOINT /code/scripts/execute_in_conda.sh ${dboxtoken} ${dboxdir}

