import ray
from ray.tune import run_experiments
from ray.tune.registry import register_env
from env import MultiAgentParticleEnv

from ray.rllib.agents.dqn import DQNTrainer

import argparse
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # {'0': 'DEBUG', '1': 'INFO', '2': 'WARNING', '3': 'ERROR'}


def parse_args():
    parser = argparse.ArgumentParser("Ray DQN with OpenAI MPE")

    # Environment
    parser.add_argument("--scenario", type=str, default="simple",
                        choices=['simple', 'simple_speaker_listener',
                                 'simple_crypto', 'simple_push',
                                 'simple_tag', 'simple_spread', 'simple_adversary',
                                 'simple_adversary_m', 'simple_speaker_listener_m'],
                        help="name of the scenario script")
    parser.add_argument("--max-episode-len", type=int, default=25,
                        help="maximum episode length")
    parser.add_argument("--num-episodes", type=int, default=60000,
                        help="number of episodes")
    parser.add_argument("--num-adversaries", type=int, default=0,
                        help="number of adversaries")
    parser.add_argument("--trainer", type=str, default="dqn",
                        choices=["dqn"],
                        help="Trainer")

    # Core training parameters
    parser.add_argument("--lr", type=float, default=1e-2,
                        help="learning rate for Adam optimizer")
    parser.add_argument("--gamma", type=float, default=0.95,
                        help="discount factor")
    # NOTE: 1 iteration = sample_batch_size * num_workers timesteps
    parser.add_argument("--sample-batch-size", type=int, default=25,
                        help="number of data points sampled /update /worker")
    parser.add_argument("--train-batch-size", type=int, default=1024,
                        help="number of data points /update")
    parser.add_argument("--n-step", type=int, default=1,
                        help="length of multistep value backup")
    parser.add_argument("--num-units", type=int, default=64,
                        help="number of units in the mlp")
    parser.add_argument("--replay-buffer", type=int, default=1000000,
                        help="length of the replay buffer > 0")

    # Checkpoint
    parser.add_argument("--checkpoint-freq", type=int, default=7500,
                        help="save model once every time this many iterations are completed")
    parser.add_argument("--local-dir", type=str, default="./ray_results",
                        help="path to save checkpoints")
    parser.add_argument("--restore", type=str, default=None,
                        help="directory in which training state and model are loaded")

    # Parallelism
    parser.add_argument("--num-workers", type=int, default=1)
    parser.add_argument("--num-envs-per-worker", type=int, default=4)
    parser.add_argument("--num-gpus", type=int, default=0)

    # Misc
    parser.add_argument("--temp-dir", type=str, default="/ray_temp")
    parser.add_argument("--add-postfix", type=str, default="",
                        help="postfix that's added to the directory name of the resulted experiments")

    return parser.parse_args()


def main(args):
    ray.init(redis_max_memory=int(ray.utils.get_system_memory() * 0.4),
             memory=int(ray.utils.get_system_memory() * 0.2),
             object_store_memory=int(ray.utils.get_system_memory() * 0.2),
             num_gpus=1,
             num_cpus=6,
             temp_dir=args.temp_dir)

    discrete_action_input = False

    if args.trainer == 'dqn':
        trainer = DQNTrainer
        discrete_action_input = True
    else:
        raise Exception('Unknown trainer: "{}"'.format(args.trainer))

    def env_creater(mpe_args):
        return MultiAgentParticleEnv(**mpe_args)

    register_env("mpe", env_creater)

    env = env_creater({
        "scenario_name": args.scenario,
        "discrete_action_input": discrete_action_input
    })

    def gen_policy(i):
        return (
            None,
            env.observation_space_dict[i],
            env.action_space_dict[i],
            {
                "agent_id": i,
                "use_local_critic": False,
                "obs_space_dict": env.observation_space_dict,
                "act_space_dict": env.action_space_dict,
            }
        )

    policies = {"policy_%d" %i: gen_policy(i) for i in range(len(env.observation_space_dict))}
    policy_ids = list(policies.keys())

    def policy_mapping_fn(agent_id):
        return policy_ids[agent_id]

    exp_name = "{}{}".format(args.scenario.replace("_", "").replace("-", ""),
                             "_{}".format(args.add_postfix) if args.add_postfix != "" else "")

    run_experiments({
        exp_name: {
            "run": trainer,
            "env": "mpe",
            "stop": {
                "episodes_total": args.num_episodes,
            },
            "checkpoint_freq": args.checkpoint_freq,
            "local_dir": args.local_dir,
            "restore": args.restore,
            "config": {
                # === Log ===
                "log_level": "ERROR",

                # === Environment ===
                "env_config": {
                    "scenario_name": args.scenario,
                    "discrete_action_input" : discrete_action_input
                },
                "num_envs_per_worker": args.num_envs_per_worker,
                "horizon": args.max_episode_len,

                # === Policy Config ===
                # --- Model ---
                #"good_policy": args.good_policy,
                #"adv_policy": args.adv_policy,
                #"actor_hiddens": [args.num_units] * 2,
                #"actor_hidden_activation": "relu",
                #"critic_hiddens": [args.num_units] * 2,
                #"critic_hidden_activation": "relu",
                "n_step": args.n_step,
                "gamma": args.gamma,

                # --- Exploration ---
                #"tau": 0.01,

                # --- Replay buffer ---
                "buffer_size": args.replay_buffer,  # int(10000), # int(1e6)

                # --- Optimization ---
                #"actor_lr": args.lr,
                #"critic_lr": args.lr,
                "learning_starts": args.train_batch_size * args.max_episode_len,
                "sample_batch_size": args.sample_batch_size,
                "train_batch_size": args.train_batch_size,
                "batch_mode": "truncate_episodes",

                # --- Parallelism ---
                "num_workers": args.num_workers,
                "num_gpus": args.num_gpus,
                "num_gpus_per_worker": 0,

                # === Multi-agent setting ===
                "multiagent": {
                    "policies": policies,
                    "policy_mapping_fn": ray.tune.function(policy_mapping_fn)
                },
            },
        },
    }, verbose=1, reuse_actors=False)  # reuse_actors=True - messes up the results


if __name__ == '__main__':
    args = parse_args()
    main(args)
