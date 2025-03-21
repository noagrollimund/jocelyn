import sys, os
from casatasks import gaincal, applycal
import tools
import config as cfg

def selfcal_ATCA(info):
    myms = info['ms']
    myms_target = myms.replace('.ms', '_target.ms')
    refant = info['refant']
    nsigmas = [7.0, 5.0, 4.0] + (cfg.N_ROUNDS_SELFCAL - 3) * [3.0]

    # Phase selfcal
    gaintables = []
    for i in range(cfg.N_ROUNDS_SELFCAL):
        SC = cfg.PATH_TABLES + 'cal.SC' + str(i + 1)
        gaincal(vis = myms_target,
                caltable = SC,
                solint = '80s',
                refant = refant,
                calmode = 'p',
                gaintype = 'T',
                gaintable = gaintables)
        gaintables.append(SC)
        applycal(vis = myms_target,
                 gaintable = gaintables)
        imagename = cfg.PATH_IMAGES + '/' + myms.replace('.ms', '_selfcal' + str(i + 1))
        tools.jclean(ms = myms_target,
                     imagename = imagename,
                     nsigma = nsigmas[i])
    # Amplitude selfcal
    if cfg.DO_AP_SELFCAL:
        SCa = cfg.PATH_TABLES + 'cal.SCa'
        gaincal(vis = myms_target,
                caltable = SCa,
                solint = '160s',
                refant = refant,
                calmode = 'ap',
                gaintable = gaintables,
                solnorm = True,
                normtype = 'median')
        gaintables.append(SCa)
        applycal(vis = myms_target,
                gaintable = gaintables)
        imagename = cfg.PATH_IMAGES + '/' + myms.replace('.ms', '_selfcal_ap')
        tools.jclean(ms = myms_target,
                        imagename = imagename,
                        nsigma = nsigmas[-1])
    tools.jocelyn_log('Self-calibration completed')

def main(options):
    os.chdir(cfg.PATH_BAND)
    info = tools.info_json()
    tools.jocelyn_log('Information loaded')
    if options == '':
        selfcal_ATCA(info)

if __name__ == "__main__":
    options = sys.argv[1] if len(sys.argv) > 1 else ''
    main(options)