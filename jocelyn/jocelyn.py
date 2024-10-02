import sys, os

def main(path_obs):
    if path_obs == '':
        path_obs = os.getcwd()
    os.chdir(path_obs)

    import look
    look.main()

    import calibratimage
    calibratimage.main()

if __name__ == "__main__":
    options = sys.argv[1] if len(sys.argv) > 1 else ''
    main(options)