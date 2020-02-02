# Comparison experiments for MADDPG, DQN, PPO


## Running in docker (Tensorflow images)

Build image for CPU based Tensorflow:
```
sudo docker build -t maddpg-rllib:latest -f cpu.Dockerfile .
```
Or GPU
```
sudo docker build -t maddpg-rllib:latest -f gpu.Dockerfile .
```

Optionally cleanup if a container was created before
```
sudo docker stop maddpgrllib-test
sudo docker rm maddpgrllib-test
```
Start the container (Replace `YOUR_TOKEN` with your Dropbox token):
```
sudo docker run -e dboxtoken=YOUR_TOKEN -e dboxdir=/epxeriment_1 --name maddpgrllib-test --shm-size=4gb maddpg-rllib:latest
```

`-e dboxdir=/epxeriment_1` points to the destination directory inside of the Dropbox account, you might want to adjust it.

If you want the results to be uploaded to Dropbox, you'll need to setup an app in your account [App console](https://www.dropbox.com/developers/apps) in order to get a token.

---

## Running in docker (CUDA)

[Local installation instructions](./INSTALL_CUDA.md)

```
sudo docker build -t maddpg-rllib-cuda:latest -f cuda.Dockerfile .
```

```
sudo docker run  --gpus all -e dboxtoken=YOUR_TOKEN -e dboxdir=/epxeriment_1 --name maddpgrllib-test-cuda --shm-size=4gb maddpg-rllib-cuda:latest
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
