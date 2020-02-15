# Comparison experiments for MADDPG, DQN, PPO


## Running in docker (Tensorflow images)

Build image for CPU based Tensorflow:
```
docker build -t maddpg-rllib:latest -f cpu.Dockerfile .
```
Or GPU
```
docker build -t maddpg-rllib:latest -f gpu.Dockerfile .
```

Optionally cleanup if a container was created before
```
docker stop maddpg-rllib
docker rm maddpg-rllib
```
Start the container.
Environment parameters:
* `repeats` - number of experiment repetitions
* `dboxtoken` - (optional) your Dropbox token
* `dboxdir` - directory in the Dropbox where the results will be uploaded. Must be empty or non existent. **Should only be defined when `dboxtoken` us supplied**

If you don't want to use Dropbox auto upload, just omit `-e dboxtoken=...` and `-e dboxdir=...` flags. Results will be stored in `maddpg-rllib-vres` Docker volume.

```
docker run \
 -e dboxtoken=YOUR_TOKEN \
 -e dboxdir=/epxeriment_1 \
 -e repeats=5 \
 --name maddpg-rllib \
 -v maddpg-rllib-vtmp:/ray_temp \
 -v maddpg-rllib-vres:/ray_results \
 --shm-size=4gb \
 maddpg-rllib:latest
```

After the container experiments finish, the container quits. If you didn't supply a valid Dropbox token, you'll need to get the results from the mounted volume. You can access a volume with a *dummy* container attacched to that volume. Example using [Docker `cp`](https://docs.docker.com/engine/reference/commandline/cp/):
```
docker container create --name maddpg-rllib-dummy \
    -v maddpg-rllib-vtmp:/ray_temp \ 
    -v maddpg-rllib-vres:/ray_results \ 
    hello-world

mkdir -p ./ray_results  

docker cp maddpg-rllib-dummy:/ray_results ./ray_results

docker rm maddpg-rllib-dummy
```

If you want the results to be uploaded to Dropbox, you'll need to setup an app in your account [App console](https://www.dropbox.com/developers/apps) in order to get a token.

---

## Running in docker (CUDA)

[Local installation instructions](./INSTALL_CUDA.md)

```
docker build -t maddpg-rllib-cuda:latest -f cuda.Dockerfile .
```

As in the case with Tensorflow images, omit `-e dboxtoken=...` and `-e dboxdir=...` flags if you don't want to upload results to your Dropbox and want them to be store locally

```
docker run \
 --gpus all \
 -e dboxtoken=YOUR_TOKEN \
 -e dboxdir=/epxeriment_1 \
 --name maddpg-rllib-cuda \
 --shm-size=4gb \
 -v maddpg-rllib-vtmp:/ray_temp \
 -v maddpg-rllib-vres:/ray_results \
 maddpg-rllib-cuda:latest
```


***
Fork of [wsjeon/maddpg-rllib](https://github.com/wsjeon/maddpg-rllib)
***

# Multi-Agent DDPG in Ray/RLlib

## Notes
- The codes in [OpenAI/MADDPG](https://github.com/openai/maddpg) were refactored in RLlib, and test results are given in `./plots`.
    - It was tested on 7 scenarios of [OpenAI/Multi-Agent Particle Environment (MPE)](https://github.com/openai/multiagent-particle-envs).
        - `simple`, `simple_adversary`, `simple_crypto`, `simple_push`, `simple_speaker_listener`, `simple_spread`, `simple_tag`
            - RLlib MADDPG shows the similar performance as OpenAI MADDPG on 7 scenarios except `simple_crypto`. 
    - Hyperparameters were set to follow the original hyperparameter setting in [OpenAI/MADDPG](https://github.com/openai/maddpg).
    
- Empirically, *removing lz4* makes running much faster. I guess this is due to the small-size observation in MPE. 
    

## References
- [OpenAI/MADDPG](https://github.com/openai/maddpg)
- [OpenAI/Multi-Agent Particle Environment](https://github.com/openai/multiagent-particle-envs)
    - [wsjeon/Multi-Agent Particle Environment](https://github.com/wsjeon/multiagent-particle-envs)
        - It includes the minor change for MPE to work with recent OpenAI Gym.

 ***
