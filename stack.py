import glob, sys, os
from casatasks import concat, gaincal, applycal
from calibratimage import jocelyn_clean
import config as cfg

def selfcal(myms, imagename):
    jocelyn_clean(ms = myms,
                  datacolumn = 'data',
                  imagename = imagename + '_init')
    n_rounds = 3
    gaintables = []
    for round in range(n_rounds):
        SC = 'cal.SC' + str(round + 1)
        img_name = imagename + '_selfcal' + str(round + 1)
        gaincal(vis = myms,
                caltable = SC,
                solint = '80s',
                refant = 'CA04',
                calmode = 'p',
                gaintype = 'T',
                gaintable = gaintables)
        gaintables.append(SC)
        applycal(vis = myms,
                 gaintable = gaintables)
        jocelyn_clean(ms = myms,
                      imagename = img_name)
    jocelyn_clean(ms = myms,
                  imagename = imagename + '_final',
                  usemask = 'user',
                  savemodel = 'none')

def main(path_stack):
    os.chdir(path_stack)
    list_of_target_ms = glob.glob('../*/{}band/*_target.ms'.format(cfg.BAND))
    myms = '_'.join([cfg.SOURCE, cfg.TELESCOPE, cfg.BAND + 'band.ms'])
    concat(vis = list_of_target_ms,
           concatvis = myms)
    imagename = myms.replace('.ms', '')
    if cfg.STACK_SELFCAL:
        selfcal(myms, imagename)
    else:
        jocelyn_clean(ms = myms,
                      datacolumn = 'data',
                      imagename = imagename,
                      usemask = 'user',
                      savemodel = 'none')

if __name__ == "__main__":
    main(sys.argv[1])