import os
import config as cfg
import generate_jobs as gen

def main():
    path = os.getcwd()
    path_data = path + '/data/'
    path_code = path + '/jocelyn/'
    path_stack = path + '/stack/' if cfg.STACK_OBS else None
    paths_obs = []
    if not os.path.exists(path_data):
        raise FileNotFoundError('No data directory found.')
    for date in cfg.DATES:
        path_obs = path + '/' + date[0] + '/'
        if not os.path.exists(path_obs):
            os.makedirs(path_obs)
        gen.symlinks(path_data, date)
        gen.slurm_jocelyn(path_obs, path_code)
        paths_obs.append(path_obs)
    if cfg.STACK_OBS:
        if not os.path.exists(path_stack):
            os.makedirs(path_stack)
        gen.slurm_stack(path_stack, path_code)
    gen.slurm_main(path, paths_obs, path_stack)

if __name__ == "__main__":
    main()