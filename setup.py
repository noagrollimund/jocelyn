import os, glob
import jocelyn.config as cfg
import jocelyn.generate_jobs as gen

def symlinks(path_archive, date):
    archives = glob.glob(path_archive + date + '*.C*')
    for archive in archives:
        link_archive = archive + ' ' + date
        os.system('ln -s ' + link_archive)
    flags_file = glob.glob(path_archive + date + '*.flag')
    link_flags = flags_file[0] + ' ' + date
    os.system('ln -s ' + link_flags)

def main():
    path = os.getcwd()
    path_archive = path + '/archive/'
    path_code = path + '/jocelyn/'
    path_stack = path + '/stack/' if cfg.STACK_OBS else None
    paths_obs = []
    if not os.path.exists(path_archive):
        raise FileNotFoundError('No archive directory found.')
    for date in cfg.DATES:
        path_obs = f'{path}/{date}/'
        if not os.path.exists(path_obs):
            os.makedirs(path_obs)
        symlinks(path_archive, date)
        gen.slurm_jocelyn(path_obs, path_code)
        paths_obs.append(path_obs)
    if cfg.STACK_OBS:
        if not os.path.exists(path_stack):
            os.makedirs(path_stack)
        gen.slurm_stack(path_stack, path_code)
    gen.slurm_main(path, paths_obs, path_stack)

if __name__ == "__main__":
    main()