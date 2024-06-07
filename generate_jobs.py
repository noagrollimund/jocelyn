import os, glob

def symlinks(path_data, date):
    obs_dir = date[0]
    for prefix in date:
        archives = glob.glob(path_data + prefix + '*.C*')
        for archive in archives:
            link_archive = archive + ' ' + obs_dir
            os.system('ln -s ' + link_archive)
    flags_file = glob.glob(path_data + obs_dir + '*flags*.py')
    link_flags = flags_file[0] + ' ' + obs_dir
    os.system('ln -s ' + link_flags)

def slurm_jocelyn(path_obs, path_code):
    instruct = "#!/bin/bash\n"
    instruct += "#SBATCH --job-name=jocelyn\n"
    instruct += "#SBATCH --time=4:00:00\n"
    instruct += "#SBATCH --partition=Main\n"
    instruct += "#SBATCH --nodes=1\n"
    instruct += "#SBATCH --ntasks-per-node=8\n"
    instruct += "#SBATCH --cpus-per-task=1\n"
    instruct += "#SBATCH --mem=64GB\n"
    instruct += "#SBATCH --output=" + path_obs + "jocelyn.log\n"
    instruct += "module load openmpi/4.0.3\n"
    instruct += "mpirun singularity exec /idia/software/containers/casa-6.simg python " + path_code + "jocelyn.py " + path_obs + "\n"
    instruct += 'echo "****ELAPSED "$SECONDS""\n'
    slurm_file = path_obs + 'jocelyn.sh'
    with open(slurm_file, "w") as f:
        f.write(instruct)
    os.system('chmod +x ' + slurm_file)

def slurm_stack(path_stack, path_code):
    instruct = "#!/bin/bash\n"
    instruct += "#SBATCH --job-name=stack\n"
    instruct += "#SBATCH --time=15:00:00\n"
    instruct += "#SBATCH --partition=Main\n"
    instruct += "#SBATCH --nodes=1\n"
    instruct += "#SBATCH --ntasks-per-node=8\n"
    instruct += "#SBATCH --cpus-per-task=1\n"
    instruct += "#SBATCH --mem=64GB\n"
    instruct += "#SBATCH --output=" + path_stack + "stack.log\n"
    instruct += "module load openmpi/4.0.3\n"
    instruct += "mpirun singularity exec /idia/software/containers/casa-6.simg python " + path_code + "stack.py " + path_stack + "\n"
    instruct += 'echo "****ELAPSED "$SECONDS""\n'
    slurm_file = path_stack + 'stack.sh'
    with open(slurm_file, "w") as f:
        f.write(instruct)
    os.system('chmod +x ' + slurm_file)

def slurm_main(path, paths_obs, path_stack):
    slurm_file = path + '/submit_jobs.sh'
    kill_file = path + "/kill_jobs.sh"
    instruct = "#!/bin/bash\n"
    for i, path_obs in enumerate(paths_obs):
        instruct += "jcl{}".format(i) + "=`sbatch " + path_obs + "jocelyn.sh | awk '{print $4}'`\n"
    list_of_jobs = ["jcl{}".format(i) for i in range(len(paths_obs))]
    if path_stack != None:
        afterok = ''.join([':$' + name for name in list_of_jobs])
        instruct += "stack=`sbatch --dependency=afterok" + afterok + " " + path_stack + "stack.sh | awk '{print $4}'`\n"
        list_of_jobs.append('stack')
    scancel_jobs = ' '.join(['$' + name for name in list_of_jobs])
    instruct += "echo 'scancel '" + scancel_jobs + " > " + kill_file
    with open(slurm_file, "w") as f:
        f.write(instruct)
    os.system('chmod +x ' + slurm_file)