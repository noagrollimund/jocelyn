import os
import jocelyn.config as cfg

def write_slurm(slurm_file, instruct):
    with open(slurm_file, "w") as f:
        f.write(instruct)
    os.system('chmod +x ' + slurm_file)

def slurm_jocelyn(path_obs, path_code):
    instruct = "#!/bin/bash\n"
    instruct += "#SBATCH --job-name=jocelyn\n"
    instruct += "#SBATCH --time=4:00:00\n"
    instruct += "#SBATCH --partition=Main\n"
    instruct += "#SBATCH --nodes=1\n"
    instruct += "#SBATCH --ntasks-per-node=8\n"
    instruct += "#SBATCH --cpus-per-task=1\n"
    instruct += "#SBATCH --mem=64GB\n"
    instruct += f"#SBATCH --output={path_obs}jocelyn.log\n"
    instruct += "module load openmpi/4.0.3\n"
    instruct += f"mpirun singularity exec {cfg.CASA_CONTAINER_PATH} python {path_code}jocelyn.py {path_obs}\n"
    instruct += 'echo "****ELAPSED "$SECONDS""\n'
    slurm_file = f'{path_obs}jocelyn.sh'
    write_slurm(slurm_file, instruct)

def slurm_stack(path_stack, path_code):
    instruct = "#!/bin/bash\n"
    instruct += "#SBATCH --job-name=stack\n"
    instruct += "#SBATCH --time=15:00:00\n"
    instruct += "#SBATCH --partition=Main\n"
    instruct += "#SBATCH --nodes=1\n"
    instruct += "#SBATCH --ntasks-per-node=8\n"
    instruct += "#SBATCH --cpus-per-task=1\n"
    instruct += "#SBATCH --mem=64GB\n"
    instruct += f"#SBATCH --output={path_stack}stack.log\n"
    instruct += "module load openmpi/4.0.3\n"
    instruct += f"mpirun singularity exec {cfg.CASA_CONTAINER_PATH} python {path_code}stack.py {path_stack}\n"
    instruct += 'echo "****ELAPSED "$SECONDS""\n'
    slurm_file = f'{path_stack}stack.sh'
    write_slurm(slurm_file, instruct)

def slurm_main(path, paths_obs, path_stack):
    instruct = "#!/bin/bash\n"
    for i, path_obs in enumerate(paths_obs):
        instruct += f"jcl{i}=`sbatch {path_obs}jocelyn.sh" + " | awk '{print $4}'`\n"
    list_of_jobs = [f"jcl{i}" for i in range(len(paths_obs))]
    if path_stack != None:
        afterok = ''.join([':$' + name for name in list_of_jobs])
        instruct += f"stack=`sbatch --dependency=afterok{afterok} {path_stack}stack.sh" + " | awk '{print $4}'`\n"
        list_of_jobs.append('stack')
    scancel_jobs = ' '.join(['$' + name for name in list_of_jobs])
    slurm_file = path + '/submit_jobs.sh'
    kill_file = path + "/kill_jobs.sh"
    instruct += f"echo 'scancel '{scancel_jobs} > {kill_file}"
    write_slurm(slurm_file, instruct)