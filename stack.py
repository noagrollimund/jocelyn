import glob, sys, os
from calibratimage import jocelyn_clean

def main(path_stack):
    os.chdir(path_stack)
    list_of_target_ms = glob.glob('../*/Cband/*_target.ms')
    myms = '4U1755_ATCA_Cband.ms'

    from casatasks import concat
    concat(vis = list_of_target_ms,
           concatvis = myms)
    imagename = myms.replace('.ms', '')
    jocelyn_clean(ms = myms,
                  datacolumn = 'data',
                  imagename = imagename,
                  usemask = 'user',
                  savemodel = 'none')

if __name__ == "__main__":
    main(sys.argv[1])