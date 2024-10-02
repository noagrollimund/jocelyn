import sys, os

def main(path_obs):
    os.chdir(path_obs)

    from jocelyn.jocelyn import look
    look.main()

    from jocelyn.jocelyn import calibratimage
    calibratimage.main()

if __name__ == "__main__":
    main(sys.argv[1])