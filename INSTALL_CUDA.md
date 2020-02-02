##Ubuntu 18.04 LTS

### Setting up CUDA capable Docker

[Official guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)

Preliminaries

*Assuming Docker is already installed, as well as CUDA capable NVidia GPU.*

```
sudo apt-get install g++ freeglut3-dev build-essential libx11-dev libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev
```

Driver [Compute repos](https://developer.download.nvidia.com/compute/cuda/repos/). 
Combination of the installed GPU driver and CUDA driver must be compatible.
```
wget http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo dpkg -i cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
sudo apt-get update
sudo apt-get install cuda
```

Docker
[GitHub](https://github.com/NVIDIA/nvidia-docker)

```
# Add the package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```


***
### Deinstallation
Remove driver:
```
sudo dpkg -r cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01
```
