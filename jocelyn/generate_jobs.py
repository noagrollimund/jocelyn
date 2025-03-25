import os
import jocelyn.config as cfg

def write_slurm(slurm_file, instruct):
    with open(slurm_file, "w") as f:
        f.write(instruct)
    os.system('chmod +x ' + slurm_file)

def slurm_jocelyn(path, path_code):
    instruct = "#!/bin/bash\n"
    instruct += "#SBATCH --job-name=JOCELYN\n"
    instruct += "#SBATCH --time=4:00:00\n"
    instruct += "#SBATCH --partition=Main\n"
    instruct += "#SBATCH --nodes=1\n"
    instruct += "#SBATCH --ntasks-per-node=8\n"
    instruct += "#SBATCH --cpus-per-task=1\n"
    instruct += "#SBATCH --mem=64GB\n"
    instruct += f"#SBATCH --output={path}/JOCELYN.log\n"
    instruct += f"cd {path}\n"
    instruct += "module load openmpi/4.0.3\n"
    instruct += f"singularity exec {cfg.CASA_CONTAINER_PATH} python {path_code}0_INFO.py\n"
    instruct += f"mpirun singularity exec {cfg.CASA_CONTAINER_PATH} python {path_code}1GC.py\n"
    instruct += f"mpirun singularity exec {cfg.CASA_CONTAINER_PATH} python {path_code}2GC.py\n"
    instruct += 'echo "****ELAPSED "$SECONDS""\n'
    slurm_file = f'{path}/JOCELYN.sh'
    write_slurm(slurm_file, instruct)

def slurm_main(path):
    slurm_file = path + '/submit_jobs.sh'
    kill_file = path + "/kill_jobs.sh"
    instruct = "#!/bin/bash\n"
    instruct += f"JOCELYN=`sbatch {path}JOCELYN.sh" + " | awk '{print $4}'`\n"
    instruct += f"echo 'scancel JOCELYN' > {kill_file}"
    write_slurm(slurm_file, instruct)