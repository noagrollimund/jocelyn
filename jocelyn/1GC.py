import os, sys, glob
from casatasks import flagdata, gencal, plotweather, setjy, gaincal, bandpass, fluxscale, applycal, split, delmod, clearcal, polcal
import tools
import config as cfg

def manual_flagging(info: dict):
    """
    Flag data from commands given in an input .flag file.
    """
    # Check if a flagging file is available
    flags_filename = glob.glob(cfg.PATH_OBS + '/*.flag')
    if flags_filename == []:
        tools.jocelyn_log('No flagging file found')
    else:
        # Apply the external flags
        flagdata(vis = info['ms'], mode = 'list', inpfile = flags_filename[0])
        tools.jocelyn_log('Manual flagging completed')

def calibrate_VLA(info):
    target = info['fields']['target']
    fcal = info['fields']['fcal']
    pcal = info['fields']['pcal']
    # date = info['datetime']['date']
    # time = info['datetime']['time']
    myms = info['ms']
    clearcal(myms)
    delmod(myms)
    if not os.path.exists(cfg.PATH_TABLES):
        os.makedirs(cfg.PATH_TABLES)
    refant = tools.find_best_refant(info)

    # Antenna position corrections
    # working_ants = tools.antenna_dist2cofa(myms)
    # antennas, antpos_corr = tools.VLA_corrected_baselines(date, time, working_ants)
    # gencal(vis = myms,
    #        caltable = cfg.PATH_TABLES + 'antpos.cal',
    #        caltype = 'antposvla',
    #        antenna = antennas,
    #        parameter = antpos_corr)


    high_frequencies = cfg.BAND in ['Ku', 'K', 'Q']
    if high_frequencies:
        # Opacity corrections
        tau = plotweather(vis = myms, doPlot = False)
        gencal(vis = myms,
               caltable = cfg.PATH_TABLES + 'opacity.cal',
               caltype = 'opac',
               parameter = tau,
               spw = '0, 1')

    # Gaincurves and antenna efficiencies
    gencal(vis = myms,
           caltable = cfg.PATH_TABLES + 'gaincurve.cal',
           caltype = 'gceff')

    # Set up the model for the flux calibrator
    setjy(vis = myms,
          field = fcal)

    if high_frequencies:
        # Gain calibration
        # tables = [cfg.PATH_TABLES + table for table in ['antpos.cal', 'opacity.cal', 'gaincurve.cal']]
        tables = [cfg.PATH_TABLES + table for table in ['opacity.cal', 'gaincurve.cal']]
        gaincal(vis = myms,
                caltable = cfg.PATH_TABLES + 'intphase.gcal',
                field = ','.join([fcal, pcal]),
                solint = 'int',
                refant = refant,
                gaintype = 'G',
                minsnr = 2.0,
                calmode = 'p',
                gaintable = tables)
        gaincal(vis = myms,
                caltable = cfg.PATH_TABLES + 'scanphase.gcal',
                field = ','.join([fcal, pcal]),
                solint = 'inf',
                refant = refant,
                gaintype = 'G',
                minsnr = 2.0,
                calmode = 'p',
                gaintable = tables)
        gaincal(vis = myms,
                caltable = cfg.PATH_TABLES + 'amp.gcal',
                field = ','.join([fcal, pcal]),
                solint = 'inf',
                refant = refant,
                minsnr = 2.0,
                calmode = 'ap',
                gaintable = tables + [cfg.PATH_TABLES + 'intphase.gcal'])
        
        # Derive the flux scale for the phase cal
        fluxscale(vis = myms,
                  caltable = cfg.PATH_TABLES + 'amp.gcal',
                  fluxtable = cfg.PATH_TABLES + 'flux.cal',
                  reference = fcal,
                  incremental = True)
        
        # Apply calibration
        tables.extend([cfg.PATH_TABLES + 'flux.cal', cfg.PATH_TABLES + 'amp.gcal'])
        applycal(vis = myms,
                field = target, 
                gaintable = tables + [cfg.PATH_TABLES + 'scanphase.gcal'],
                gainfield = len(tables) * [''] + [pcal, pcal, pcal],
                calwt = False)
        applycal(vis = myms,
                field = pcal,
                gaintable = tables + [cfg.PATH_TABLES + 'intphase.gcal'],
                gainfield = len(tables) * [''] + [pcal, pcal, pcal],
                calwt = False)
        applycal(vis = myms,
                field = fcal, 
                gaintable = tables + [cfg.PATH_TABLES + 'intphase.gcal'],
                gainfield = len(tables) * [''] + [fcal, fcal, fcal],
                calwt = False)

    else:
        # Gain calibration
        # tables = [cfg.PATH_TABLES + table for table in ['antpos.cal', 'gaincurve.cal']]
        tables = [cfg.PATH_TABLES + table for table in ['gaincurve.cal']]
        gaincal(vis = myms,
            caltable = cfg.PATH_TABLES + 'gaintable.g1',
            field = fcal,
            solint = '30s',
            refant = refant,
            minsnr = 2.0,
            gaintype = 'G',
            gaintable = tables)

        gaincal(vis = myms,
            caltable = cfg.PATH_TABLES + 'gaintable.g1',
            field = pcal,
            solint = '30s',
            refant = refant,
            minsnr = 2.0,
            gaintype = 'G',
            gaintable = tables,
            append = True)

        # Derive the flux scale for the phase cal
        fluxscale(vis = myms,
                  caltable = cfg.PATH_TABLES + 'gaintable.g1',
                  fluxtable = cfg.PATH_TABLES + 'flux.cal',
                  reference = fcal,
                  transfer = pcal)
        
        # Apply calibration
        tables.append(cfg.PATH_TABLES + 'flux.cal')
        applycal(vis = myms,
                field = target, 
                gaintable = tables,
                gainfield = len(tables) * [''] + [pcal],
                calwt = False)
        applycal(vis = myms,
                field = pcal, 
                gaintable = tables,
                gainfield = len(tables) * [''] + [pcal],
                calwt = False)
        applycal(vis = myms,
                field = fcal, 
                gaintable = tables,
                gainfield = len(tables) * [''] + [fcal],
                calwt = False)
    tools.jocelyn_log('Data calibrated')

def image_VLA(info):
    myms = info['ms']
    target = info['fields']['target']
    myms_target = myms.replace('.ms', '_target.ms')
    imagename = cfg.PATH_IMAGES + myms.split('/')[-1].replace('.ms', '')
    split(vis = myms,
          outputvis = myms_target,
          field = target,
          datacolumn = 'corrected')
    tools.jclean(ms = myms_target,
                 datacolumn = 'data',
                 imagename = imagename)
    tools.jocelyn_log('Image deconvolved')

def calibrate_ATCA(info):
    target = info['fields']['target']
    fcal = info['fields']['fcal']
    pcal = info['fields']['pcal']
    myms = info['ms']
    refant = tools.find_best_refant(info, nb_ctr_ant = 3)
    clearcal(myms)
    delmod(myms)
    if not os.path.exists(cfg.PATH_TABLES):
        os.makedirs(cfg.PATH_TABLES)
    G0 = cfg.PATH_TABLES + 'cal.G0'
    K0 = cfg.PATH_TABLES + 'cal.K0'
    B0 = cfg.PATH_TABLES + 'cal.B0'
    G1 = cfg.PATH_TABLES + 'cal.G1'
    F0 = cfg.PATH_TABLES + 'cal.F0'
    D0 = cfg.PATH_TABLES + 'cal.D0'

    # Initial Flux Density Scaling
    setjy(vis = myms,
          field = fcal,
          standard = 'Perley-Butler 2010')
    
    # Initial Phase Calibration
    gaincal(vis = myms,
            caltable = G0,
            field = fcal,
            refant = refant,
            gaintype = 'G',
            calmode = 'p',
            solint = '60s',
            parang = True)
    
    # Delay Calibration
    gaincal(vis = myms,
            caltable = K0,
            field = fcal,
            refant = refant,
            gaintype = 'K',
            solint = 'inf',
            gaintable = [G0],
            parang = True)
    
    # Bandpass Calibration
    bandpass(vis = myms,
             caltable = B0,
             field = fcal,
             refant = refant,
             solnorm = True,
             solint = 'inf',
             bandtype = 'B',
             gaintable = [G0, K0],
             parang = True)
    
    # Gain Calibration
    gaincal(vis = myms,
            caltable = G1,
            field = ','.join([fcal, pcal]),
            solint = '60s',
            refant = refant,
            gaintype = 'G',
            calmode = 'ap',
            gaintable = [K0, B0],
            parang = True)
    
    # Polarization Calibration: Leakage Terms
    polcal(vis = myms,
           caltable = D0,
           field = fcal,
           solint = 'inf',
           refant = refant,
           gaintable = [K0, B0, G1],
           gainfield = ['', '', '', fcal],
           poltype = 'Df')
    
    # Scaling the Amplitude Gains
    fluxscale(vis = myms,
              caltable = G1,
              fluxtable = F0,
              reference = fcal,
              transfer = [pcal])
    
    # Applying the Calibration
    applycal(vis = myms,
             field = fcal,
             gaintable = [K0, B0, D0, F0],
             gainfield = ['', '', '', fcal],
             interp = ['', '', '', 'nearest'],
             parang = True)
    applycal(vis = myms,
             field = pcal,
             gaintable = [K0, B0, D0, F0],
             gainfield = ['', '', '', pcal],
             interp = ['', '', '', 'nearest'],
             parang = True)
    applycal(vis = myms,
             field = target,
             gaintable = [K0, B0, D0, F0],
             gainfield = ['', '', '', pcal],
             interp = ['', '', '', 'linear'],
             parang = True)
    myms_target = myms.replace('.ms', '_target.ms')
    export_ms(myms, myms_target, target)
    tools.jocelyn_log('Data calibrated')

def image_ATCA(info):
    myms = info['ms']
    myms_target = myms.replace('.ms', '_target.ms')
    imagename = cfg.PATH_IMAGES + myms.split('/')[-1].replace('.ms', '')
    tools.jclean(ms = myms_target,
                 datacolumn = 'data',
                 imagename = imagename,
                 nsigma = 10.0)
    tools.jocelyn_log('Imaging completed')

def export_ms(myms, myms_target, target = ''):
    split(vis = myms,
          outputvis = myms_target,
          field = target,
          datacolumn = 'corrected')

def main(options):
    os.chdir(cfg.PATH_BAND)
    info = tools.info_json()
    tools.jocelyn_log('Information loaded')
    if options == '':
        if cfg.MANUAL_FLAG:
            manual_flagging(info)
        if cfg.TELESCOPE == 'VLA':
            calibrate_VLA(info)
            image_VLA(info)
        elif cfg.TELESCOPE == 'ATCA':
            calibrate_ATCA(info)
            image_ATCA(info)
    else:
        steps = options.replace(' ', '').split(',')
        if 'f' in steps and cfg.MANUAL_FLAG:
            manual_flagging(info)
        if 'c' in steps:
            if cfg.TELESCOPE == 'VLA':
                calibrate_VLA(info)
            elif cfg.TELESCOPE == 'ATCA':
                calibrate_ATCA(info)
        if 'i' in steps:
            if cfg.TELESCOPE == 'VLA':
                image_VLA(info)
            elif cfg.TELESCOPE == 'ATCA':
                image_ATCA(info)

if __name__ == "__main__":
    options = sys.argv[1] if len(sys.argv) > 1 else ''
    main(options)