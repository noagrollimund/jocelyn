import glob, sys, os
from casatasks import concat, gaincal, applycal
from calibratimage import jocelyn_clean
import config as cfg

def selfcal(myms, imagename):
    jocelyn_clean(ms = myms,
                  datacolumn = 'data',
                  imagename = imagename)
    SC = 'cal.SC'
    gaincal(vis = myms,
            caltable = SC,
            solint = '80s',
            refant = 'CA04',
            calmode = 'p',
            gaintype = 'T')
    applycal(vis = myms,
             gaintable = SC)
    jocelyn_clean(ms = myms,
                  imagename = imagename,
                  usemask = 'user',
                  savemodel = 'none')

def main(path_stack):
    os.chdir(path_stack)
    list_of_target_ms = glob.glob('../*/{}band/*_target.ms'.format(cfg.BAND))
    myms = '_'.join([cfg.SOURCE, cfg.TELESCOPE, cfg.BAND + 'band.ms'])
    concat(vis = list_of_target_ms,
           concatvis = myms)
    imagename = myms.replace('.ms', '')
    
    # jocelyn_clean(ms = myms,
    #               datacolumn = 'data',
    #               imagename = imagename,
    #               usemask = 'user',
    #               savemodel = 'none')
    selfcal(myms, imagename)

if __name__ == "__main__":
    main(sys.argv[1])