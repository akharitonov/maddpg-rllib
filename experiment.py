import argparse
import os, sys
import time
import traceback
from datetime import datetime

import dropbox
from dropbox.exceptions import ApiError
from dropbox import files as dropf

"""
Script running a series of MPE RL experiments, optionally uploading results to Dropbox
"""

parser = argparse.ArgumentParser(description='Experiments runner.')
parser.add_argument("--temp-dir",
                    type=str,
                    default="/ray_temp",
                    help="storage for temporary ray files")
parser.add_argument("--local-dir",
                    type=str,
                    default="./ray_results",
                    help="path to save checkpoints")
parser.add_argument("-r", "--repeat",
                    type=int,
                    default=7,
                    help="number of repetitions per experiment")
parser.add_argument("--dbox-token",
                    type=str,
                    default=None,
                    required=False,  # https://www.dropbox.com/developers/documentation/python
                    help="App token for Dropbox where results should be uploaded")
parser.add_argument("--dbox-dir",
                    type=str,
                    default='/experiment',
                    required=False,
                    help="Dropbox folder where results should be uploaded")
parser.add_argument("--num-gpus",
                    type=int, default=0)
parser.add_argument("--checkpoint-freq",
                    type=int, default=75000,
                    help="save model once every time this many iterations are completed")

parser.add_argument("--scenario",
                    type=int, default=-1,
                    help="Selected scenario to run. -1 will run all, [0, 5] correspond to the index in scenarios list.")

args = parser.parse_args()

gamma_exp = True
lr_exp = True
buffer_exp = True
step_exp = True
tau_exp = True
policy_exp = True

# Scenarios to run
scenarios = ["simple_speaker_listener",
             "simple_push",
             "simple_tag",
             "simple_crypto",
             "simple_spread",
             "simple_adversary"]

if args.scenario >= 0:  # select only a particular scenario
    scenarios = [scenarios[args.scenario]]

log_file = os.path.join(args.local_dir, "_log.txt")


def write_to_log(msg):
    with open(log_file, 'a') as fd:
        fd.write(msg)
    upload_log_to_dropbox()


def write_to_log_start(msg):
    write_to_log(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} START: {msg}\n')


def write_to_log_end(msg):
    write_to_log(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} END: {msg}\n')


def write_to_log_ts(msg, is_error: bool):
    if is_error:
        write_to_log(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} ERROR: {msg}\n')
    else:
        write_to_log(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} INFO: {msg}\n')


def execute_command(cmd) -> bool:
    try:
        write_to_log_start(cmd)
        os.system(cmd)
        return True
    except Exception:
        write_to_log_ts(traceback.format_exc(), True)
        return False
    finally:
        write_to_log_end(cmd)
        cleanup(args.temp_dir)


def cleanup(folder):
    """
    Cleanup after an experiment
    """
    os.system('rm -rf %s/*' % folder)


dbx = None

if args.dbox_token is not None:
    try:
        dbx = dropbox.Dropbox(args.dbox_token)
    except Exception:
        write_to_log_ts(traceback.format_exc(), True)


def upload(file_to_upload, folder, subfolder, name, overwrite=False):
    # https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')

    mode = (dropf.WriteMode.overwrite
            if overwrite
            else dropf.WriteMode.add)
    mtime = os.path.getmtime(file_to_upload)
    with open(file_to_upload, 'rb') as f:
        data = f.read()
    try:
        res = dbx.files_upload(
            data, path, mode,
            client_modified=datetime(*time.gmtime(mtime)[:6]),
            mute=True)
        print('uploaded as', res.name.encode('utf8'))
        return True
    except ApiError as err:
        write_to_log_ts('Dropbox error: ' + err.error, True)
    except Exception:
        write_to_log_ts('Dropbox general error: ' + traceback.format_exc(), True)
    return False


def upload_with_retries(file_to_upload, folder, subfolder, name, overwrite=False, retries=3):
    for r in range(0, retries):
        res = upload(file_to_upload=file_to_upload, folder=folder, subfolder=subfolder, name=name, overwrite=overwrite)
        if res:
            break
        else:
            write_to_log_ts('Failed to upload file "{}", attempt: {}.'.format(file_to_upload, r), True)


def upload_log_to_dropbox():
    if dbx is None:
        return
    # Upload log file
    upload(log_file, args.dbox_dir, '', "log.txt", True)


def upload_to_dropbox(run_result_folder, experiment_name):
    cleanup_only = False
    if dbx is None:
        cleanup_only = True
    
    # Upload relevant experiment files
    f_params = 'params.json'
    f_progress = 'progress.csv'
    f_result = 'result.json'
    relevant_files = [f_params, f_progress, f_result]

    for root, dirs, files in os.walk(run_result_folder):
        uploaded_marker_file = os.path.join(root, '__processed_results_flag.txt')
        if os.path.isfile(uploaded_marker_file):
            continue  # this directory was already uploaded

        if os.path.isfile(os.path.join(root, f_progress)):  # If folder contains the progress file, that's what we need
            full_f_params = os.path.join(root, f_params)
            full_f_progress = os.path.join(root, f_progress)
            full_f_result = os.path.join(root, f_result)
            if not cleanup_only:
                # If Dropbox upload is active for this run upload relevant files
                if os.path.isfile(full_f_params):
                    upload_with_retries(full_f_params, args.dbox_dir, experiment_name, f_params)
                else:
                    write_to_log_ts('File not found: ' + full_f_params, False)

                if os.path.isfile(full_f_progress):
                    upload_with_retries(full_f_progress, args.dbox_dir, experiment_name, f_progress)
                else:
                    write_to_log_ts('File not found: ' + full_f_progress, False)

                if os.path.isfile(full_f_result):
                    upload_with_retries(full_f_result, args.dbox_dir, experiment_name, f_result)
                else:
                    write_to_log_ts('File not found: ' + full_f_result, False)
            try:
                # mark dir as uploaded
                with open(uploaded_marker_file, 'w') as f:
                    f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                # Cleanup the results folder, leave only files that are actually relevant
                # remove irrelevant files
                for name in files:
                    if name not in relevant_files:
                        os.remove(os.path.join(root, name))
                # remove folders
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            except Exception as err:
                print(err)
                write_to_log_ts(traceback.format_exc(), True)


# MADDPG
maddpg_results_folder = os.path.join(args.local_dir, "maddpg/")
try:
    if gamma_exp:
        # Standard experiments with varying gamma
        var_gamma_variations = [0.95, 0.75, 0.50, 0.35, 0.15]
        for scenario in scenarios:
            for gamma_var in var_gamma_variations:
                c_run_title = "maddpg_{0}_gamma_{1:1.2e}".format(scenario, gamma_var)
                c_folder = os.path.join(maddpg_results_folder, c_run_title)
                for pfx in range(args.repeat):
                    ivk_cmd = "python run_maddpg.py --scenario={} --gamma={} --local-dir={} --add-postfix={} --temp-dir={} " \
                              "--num-gpus={} --checkpoint-freq={}" \
                        .format(scenario, gamma_var, c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
                    if execute_command(ivk_cmd):
                        upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title, pfx))

    if lr_exp:
        # Standard experiments with varying learning rate
        var_lr_variations = [1e-3, 1e-2, 1e-1, 1, 1e+1, 1e+2]
        for scenario in scenarios:
            for lr_var in var_lr_variations:
                c_run_title = "maddpg_{0}_lr_{1:1.2e}".format(scenario, lr_var)
                c_folder = os.path.join(maddpg_results_folder, c_run_title)
                for pfx in range(args.repeat):
                    ivk_cmd = "python run_maddpg.py --scenario={} --lr={} --local-dir={} --add-postfix={} --temp-dir={} " \
                              "--num-gpus={} --checkpoint-freq={}" \
                        .format(scenario, lr_var, c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
                    if execute_command(ivk_cmd):
                        upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title, pfx))
    if buffer_exp:
        # Varying replay buffer
        var_replay_buffer_variations = [1000000, 100000, 10000]  # first one is the default value
        for scenario in scenarios:
            for rb_var in var_replay_buffer_variations:
                c_run_title = "maddpg_{}_rb_{}".format(scenario, rb_var)
                c_folder = os.path.join(maddpg_results_folder, c_run_title)
                for pfx in range(args.repeat):
                    ivk_cmd = "python run_maddpg.py --scenario={} --replay-buffer={} --local-dir={} --add-postfix={} " \
                              "--temp-dir={} --num-gpus={} --checkpoint-freq={}" \
                        .format(scenario, rb_var, c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
                    if execute_command(ivk_cmd):
                        upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title, pfx))

    if step_exp:
        # Standard experiments with varying numbers of steps
        var_steps_variations = [1, 5, 10, 15]
        for scenario in scenarios:
            for n_steps in var_steps_variations:
                c_run_title = "maddpg_{0}_n_steps_{1}".format(scenario, n_steps)
                c_folder = os.path.join(maddpg_results_folder, c_run_title)
                for pfx in range(args.repeat):
                    ivk_cmd = "python run_maddpg.py --scenario={} --n-step={} --local-dir={} --add-postfix={} --temp-dir={} " \
                              "--num-gpus={} --checkpoint-freq={}" \
                        .format(scenario, n_steps, c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
                    if execute_command(ivk_cmd):
                        upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title, pfx))

    if tau_exp:
        # Standard experiments with varying tau
        var_tau_variations = [1, 0.1, 0.01, 0.001]
        for scenario in scenarios:
            for tau_var in var_tau_variations:
                c_run_title = "maddpg_{0}_tau_{1:1.2e}".format(scenario, tau_var)
                c_folder = os.path.join(maddpg_results_folder, c_run_title)
                for pfx in range(args.repeat):
                    ivk_cmd = "python run_maddpg.py --scenario={} --tau={} --local-dir={} --add-postfix={} --temp-dir={} " \
                              "--num-gpus={} --checkpoint-freq={}" \
                        .format(scenario, tau_var, c_folder, str(pfx), args.temp_dir, args.num_gpus,
                                args.checkpoint_freq)
                    if execute_command(ivk_cmd):
                        upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title, pfx))

    if policy_exp:
        # Varying policy
        for scenario in scenarios:
            for pfx in range(args.repeat):
                # Good: DDPG
                c_run_title_g = "maddpg_{}_policy_good_ddpg".format(scenario)
                c_folder = os.path.join(maddpg_results_folder, c_run_title_g)
                ivk_cmd = "python run_maddpg.py --scenario={} --good-policy={} --local-dir={} --add-postfix={} --temp-dir={} " \
                          "--num-gpus={} --checkpoint-freq={}" \
                    .format(scenario, "ddpg", c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
                if execute_command(ivk_cmd):
                    upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title_g, pfx))

                # Adv: DDPG
                c_run_title_a = "maddpg_{}_policy_adv_ddpg".format(scenario)
                c_folder = os.path.join(maddpg_results_folder, c_run_title_a)
                ivk_cmd = "python run_maddpg.py --scenario={} --adv-policy={} --local-dir={} --add-postfix={} --temp-dir={} " \
                          "--num-gpus={} --checkpoint-freq={}" \
                    .format(scenario, "ddpg", c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
                if execute_command(ivk_cmd):
                    upload_to_dropbox(c_folder, 'maddpg/{}_{}'.format(c_run_title_a, pfx))

    # DQN
    """
    dqn_results_folder = os.path.join(args.local_dir, "dqn/")
    for scenario in scenarios:  # Run with default parameters
        c_run_title = "dqn_{}_default".format(scenario)
        c_folder = os.path.join(dqn_results_folder, c_run_title)
        for pfx in range(args.repeat):
            ivk_cmd = "python run_dqn.py --scenario={} --local-dir={} --add-postfix={} --temp-dir={} --num-gpus={} " \
                      "--checkpoint-freq={}" \
                .format(scenario, c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
            if execute_command(ivk_cmd):
                upload_to_dropbox(c_folder, 'dqn/{}_{}'.format(c_run_title, pfx))
    """


    # PPO
    """
    ppo_results_folder = os.path.join(args.local_dir, "ppo/")
    for scenario in scenarios:  # Run with default parameters
        c_folder = os.path.join(ppo_results_folder, "ppo_{}_default".format(scenario))
        for pfx in range(args.repeat):
            ivk_cmd = "python run_ppo.py --scenario={} --local-dir={} --add-postfix={} --temp-dir={} --num-gpus={} --checkpoint-freq={}" \
                .format(scenario, c_folder, str(pfx), args.temp_dir, args.num_gpus, args.checkpoint_freq)
            if execute_command(ivk_cmd):
                upload_to_dropbox(c_folder, 'ppo/{}_{}'.format(scenario, pfx))
    """
except Exception as exp_err:
    print(exp_err)
    write_to_log_ts(traceback.format_exc(), True)
