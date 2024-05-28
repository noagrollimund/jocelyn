import sys, os

def main(path_obs):
    os.chdir(path_obs)

    import look
    look.main()

    import calibratimage
    calibratimage.main()

if __name__ == "__main__":
    main(sys.argv[1])