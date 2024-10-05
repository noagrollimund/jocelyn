import glob
from casatasks import concat, gaincal, applycal
import tools
import config as cfg

def selfcal(myms, imagename):
    tools.jclean(ms = myms,
                  datacolumn = 'data',
                  imagename = imagename + '_init')
    n_rounds_p = 3
    gaintables = []
    for round in range(n_rounds_p):
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
        tools.jclean(ms = myms,
                      imagename = img_name)
    n_rounds_ap = 2
    for round in range(n_rounds_ap):
        SC = 'cal.SCap' + str(round + 1)
        img_name = imagename + '_selfcal_ap' + str(round + 1)
        gaincal(vis = myms,
                caltable = SC,
                solint = '160s',
                refant = 'CA04',
                calmode = 'ap',
                gaintable = gaintables,
                solnorm = True,
                normtype = 'median')
        gaintables.append(SC)
        applycal(vis = myms,
                 gaintable = gaintables)
        tools.jclean(ms = myms,
                      imagename = img_name)
    tools.jclean(ms = myms,
                 imagename = imagename + '_final',
                 usemask = 'user',
                 pbmask = 0.2,
                 savemodel = 'none')

def main():
    list_of_target_ms = glob.glob(f'../*/{cfg.BAND}band/*_target.ms')
    list_of_target_ms.sort()
    myms = '_'.join([cfg.SOURCE, cfg.TELESCOPE, cfg.BAND + 'band.ms'])
    concat(vis = list_of_target_ms,
           concatvis = myms,
           visweightscale = cfg.STACK_WEIGHTS)
    imagename = myms.replace('.ms', '')
    if cfg.STACK_SELFCAL:
        selfcal(myms, imagename)
    else:
        tools.jclean(ms = myms,
                     datacolumn = 'data',
                     imagename = imagename,
                     usemask = 'user',
                     savemodel = 'none')

if __name__ == "__main__":
    main()