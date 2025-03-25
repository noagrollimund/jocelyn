import os
import jocelyn.config as cfg

def write_slurm(slurm_file, instruct):
    with open(slurm_file, 'w') as f:
        f.write(instruct)
    os.system('chmod +x ' + slurm_file)

def slurm_jocelyn():
    instruct = "#!/bin/bash\n"
    instruct += "#SBATCH --job-name=JOCELYN\n"
    instruct += "#SBATCH --time=4:00:00\n"
    instruct += "#SBATCH --partition=Main\n"
    instruct += "#SBATCH --nodes=1\n"
    instruct += "#SBATCH --ntasks-per-node=8\n"
    instruct += "#SBATCH --cpus-per-task=1\n"
    instruct += "#SBATCH --mem=64GB\n"
    instruct += f"#SBATCH --output={cfg.PATH_LOGS}JOCELYN_{cfg.BAND}-band.log\n"
    instruct += f"cd {cfg.PATH_OBS}\n"
    instruct += "module load openmpi/4.0.3\n"
    instruct += f"singularity exec {cfg.CASA_CONTAINER_PATH} python {cfg.PATH_CODE}0_INFO.py\n"
    instruct += f"mpirun singularity exec {cfg.CASA_CONTAINER_PATH} python {cfg.PATH_CODE}1GC.py\n"
    instruct += f"mpirun singularity exec {cfg.CASA_CONTAINER_PATH} python {cfg.PATH_CODE}2GC.py\n"
    instruct += 'echo "****ELAPSED "$SECONDS""\n'
    slurm_file = f'{cfg.PATH_SCRIPTS}JOCELYN_{cfg.BAND}-band.sh'
    os.makedirs(cfg.PATH_SCRIPTS)
    os.makedirs(cfg.PATH_LOGS)
    write_slurm(slurm_file, instruct)
    return slurm_file