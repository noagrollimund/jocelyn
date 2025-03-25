import jocelyn.config as cfg
import jocelyn.generate_jobs as gen

def main():
    gen.slurm_jocelyn(cfg.PATH_OBS, cfg.PATH_CODE)
    gen.slurm_main(cfg.PATH_OBS)

if __name__ == "__main__":
    main()