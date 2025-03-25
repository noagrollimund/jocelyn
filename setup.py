import jocelyn.config as cfg
import jocelyn.generate_jobs as gen

def main():
    slurm_jocelyn = gen.slurm_jocelyn()
    submit_file = cfg.PATH_OBS + '/submit_jobs.sh'
    kill_file = cfg.PATH_SCRIPTS + '/kill_jobs.sh'
    instruct = '#!/bin/bash\n'
    instruct += f"JOCELYN=`sbatch {slurm_jocelyn}" + " | awk '{print $4}'`\n"
    instruct += f"echo 'scancel $JOCELYN' > {kill_file}"
    gen.write_slurm(submit_file, instruct)

if __name__ == "__main__":
    main()