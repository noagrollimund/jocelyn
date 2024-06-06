import json, os, sys
import tools.tools as tools
import config as cfg
from casatasks import gencal, plotweather, setjy, gaincal, bandpass, fluxscale, applycal, split, tclean, delmod, clearcal, blcal, polcal
sys.path.append(os.path.expanduser('~') + '/analysis_scripts/')
import analysisUtils as au

def calibrate_VLA(info):
    target = info['fields']['target']
    fcal = info['fields']['fcal']
    pcal = info['fields']['pcal']
    date = info['datetime']['date']
    time = info['datetime']['time']
    myms = info['ms']
    clearcal(myms)
    delmod(myms)
    if not os.path.exists(cfg.PATH_tables):
        os.makedirs(cfg.PATH_tables)
    refant = tools.find_best_refant(info)

    # Antenna position corrections
    working_ants = tools.antenna_dist2cofa(myms)
    antennas, antpos_corr = tools.VLA_corrected_baselines(date, time, working_ants)
    gencal(vis = myms,
           caltable = cfg.PATH_tables + 'antpos.cal',
           caltype = 'antposvla',
           antenna = antennas,
           parameter = antpos_corr)

    # Opacity corrections
    high_frequencies = cfg.BAND in ['Ku', 'K', 'Q']
    if high_frequencies:
        tau = plotweather(vis = myms, doPlot = False)
        gencal(vis = myms,
               caltable = cfg.PATH_tables + 'opacity.cal',
               caltype = 'opac',
               parameter = tau,
               spw = '0, 1')

    # Gaincurves and antenna efficiencies
    gencal(vis = myms,
           caltable = cfg.PATH_tables + 'gaincurve.cal',
           caltype = 'gceff')

    # Set up the model for the flux calibrator
    setjy(vis = myms,
          field = fcal)

    if high_frequencies:
        # Gain calibration
        tables = [cfg.PATH_tables + table for table in ['antpos.cal', 'opacity.cal', 'gaincurve.cal']]
        gaincal(vis = myms,
                caltable = cfg.PATH_tables + 'intphase.gcal',
                field = ','.join([fcal, pcal]),
                solint = 'int',
                refant = refant,
                gaintype = 'G',
                minsnr = 2.0,
                calmode = 'p',
                gaintable = tables)
        gaincal(vis = myms,
                caltable = cfg.PATH_tables + 'scanphase.gcal',
                field = ','.join([fcal, pcal]),
                solint = 'inf',
                refant = refant,
                gaintype = 'G',
                minsnr = 2.0,
                calmode = 'p',
                gaintable = tables)
        gaincal(vis = myms,
                caltable = cfg.PATH_tables + 'amp.gcal',
                field = ','.join([fcal, pcal]),
                solint = 'inf',
                refant = refant,
                minsnr = 2.0,
                calmode = 'ap',
                gaintable = tables + [cfg.PATH_tables + 'intphase.gcal'])
        
        # Derive the flux scale for the phase cal
        fluxscale(vis = myms,
                  caltable = cfg.PATH_tables + 'amp.gcal',
                  fluxtable = cfg.PATH_tables + 'flux.cal',
                  reference = fcal,
                  incremental = True)
        
        # Apply calibration
        tables.extend([cfg.PATH_tables + 'flux.cal', cfg.PATH_tables + 'amp.gcal'])
        applycal(vis = myms,
                field = target, 
                gaintable = tables + [cfg.PATH_tables + 'scanphase.gcal'],
                gainfield = ['', '', '', pcal, pcal, pcal],
                calwt = False)
        applycal(vis = myms,
                field = pcal,
                gaintable = tables + [cfg.PATH_tables + 'intphase.gcal'],
                gainfield = ['', '', '', pcal, pcal, pcal],
                calwt = False)
        applycal(vis = myms,
                field = fcal, 
                gaintable = tables + [cfg.PATH_tables + 'intphase.gcal'],
                gainfield = ['', '', '', fcal, fcal, fcal],
                calwt = False)

    else:
        # Gain calibration
        tables = [cfg.PATH_tables + table for table in ['antpos.cal', 'gaincurve.cal']]
        gaincal(vis = myms,
            caltable = cfg.PATH_tables + 'gaintable.g1',
            field = fcal,
            solint = '30s',
            refant = refant,
            minsnr = 2.0,
            gaintype = 'G',
            gaintable = tables)

        gaincal(vis = myms,
            caltable = cfg.PATH_tables + 'gaintable.g1',
            field = pcal,
            solint = '30s',
            refant = refant,
            minsnr = 2.0,
            gaintype = 'G',
            gaintable = tables,
            append = True)

        # Derive the flux scale for the phase cal
        fluxscale(vis = myms,
                  caltable = cfg.PATH_tables + 'gaintable.g1',
                  fluxtable = cfg.PATH_tables + 'flux.cal',
                  reference = fcal,
                  transfer = pcal)
        
        # Apply calibration
        tables.append(cfg.PATH_tables + 'flux.cal')
        applycal(vis = myms,
                field = target, 
                gaintable = tables,
                gainfield = ['', '', pcal],
                calwt = False)
        applycal(vis = myms,
                field = pcal, 
                gaintable = tables,
                gainfield = ['', '', pcal],
                calwt = False)
        applycal(vis = myms,
                field = fcal, 
                gaintable = tables,
                gainfield = ['', '', fcal],
                calwt = False)
    
    print('---------------')
    print('Data calibrated')
    print('---------------')

def deconvolve_VLA(info):
    myms = info['ms']
    target = info['fields']['target']
    myms_target = myms.replace('.ms', '_target.ms')
    imagename = cfg.PATH_images + '/' + myms.replace('.ms', '')
    cell_auto, imsize_auto, _ = au.pickCellSize(vis = myms, npix = 5, imsize = True)
    cell = cell_auto if cfg.CELL == '' else cfg.CELL
    imsize = imsize_auto if cfg.IMSIZE == '' else cfg.IMSIZE
    split(vis = myms,
          outputvis = myms_target,
          field = target,
          datacolumn = 'corrected')
    tclean(vis = myms_target,
           datacolumn = 'data',
           cell = cell,
           imsize = imsize,
           imagename = imagename,
           deconvolver = cfg.DECONVOLVER,
           scales = cfg.SCALES,
           weighting = cfg.WEIGHTING,
           robust = cfg.ROBUST,
           niter = 200)
    print('-----------------')
    print('Image deconvolved')
    print('-----------------')

def calibrate_ATCA(info):
    target = info['fields']['target']
    fcal = info['fields']['fcal']
    pcal = info['fields']['pcal']
    myms = info['ms']
    refant = tools.find_best_refant(info, nb_ctr_ant = 3)
    clearcal(myms)
    delmod(myms)
    if not os.path.exists(cfg.PATH_tables):
        os.makedirs(cfg.PATH_tables)
    G0 = cfg.PATH_tables + 'cal.G0'
    K0 = cfg.PATH_tables + 'cal.K0'
    B0 = cfg.PATH_tables + 'cal.B0'
    G1 = cfg.PATH_tables + 'cal.G1'
    F0 = cfg.PATH_tables + 'cal.F0'
    D0 = cfg.PATH_tables + 'cal.D0'
    BL = cfg.PATH_tables + 'cal.BL'

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
    print('---------------')
    print('Data calibrated')
    print('---------------')

    # Baseline-based Calibration
    # blcal(vis = myms,
    #       field = fcal,
    #       caltable = BL,
    #       solint = 'inf',
    #       gaintable = [K0, B0, D0, F0],
    #       gainfield = ['', '', '', pcal],
    #       interp = ['', '', '', 'nearest'],
    #       freqdep = True)
    # applycal(vis = myms,
    #          field = target,
    #          gaintable = [K0, B0, D0, F0, BL],
    #          gainfield = ['', '', '', pcal, fcal])
    # print('-----------------------------------------')
    # print('Baseline-based error correction completed')
    # print('-----------------------------------------')

def selfcal_ATCA(info):
    myms = info['ms']
    target = info['fields']['target']
    myms_selfcal = myms.replace('.ms', '_selfcal.ms')
    export_ms(myms, myms_selfcal)
    refant = info['refant']

    imagename = cfg.PATH_images + '/' + myms.replace('.ms', '_init')
    nsigmas = [10.0, 7.0, 5.0, 4.0, 3.0]
    jocelyn_clean(ms = myms_selfcal,
                  field = target,
                  datacolumn = 'data',
                  imagename = imagename,
                  nsigma = nsigmas[0])
    # Phase selfcal
    gaintables = []
    for i in range(4):
        SC = cfg.PATH_tables + 'cal.SC' + str(i + 1)
        gaincal(vis = myms_selfcal,
                caltable = SC,
                field = target,
                solint = '80s',
                refant = refant,
                calmode = 'p',
                gaintype = 'T',
                gaintable = gaintables)
        gaintables.append(SC)
        applycal(vis = myms_selfcal,
                 field = target,
                 gaintable = gaintables)
        imagename = cfg.PATH_images + '/' + myms_selfcal.replace('.ms', str(i + 1))
        jocelyn_clean(ms = myms_selfcal,
                      field = target,
                      imagename = imagename,
                      nsigma = nsigmas[i + 1])
    # Amplitude selfcal
    SCa = cfg.PATH_tables + 'cal.SCa'
    gaincal(vis = myms_selfcal,
            caltable = SCa,
            field = target,
            solint = '160s',
            refant = refant,
            calmode = 'ap',
            gaintable = gaintables,
            solnorm = True,
            normtype = 'median')
    gaintables.append(SCa)
    applycal(vis = myms_selfcal,
                field = target,
                gaintable = gaintables)
    imagename = cfg.PATH_images + '/' + myms_selfcal.replace('.ms', '_amp')
    jocelyn_clean(ms = myms_selfcal,
                  field = target,
                  imagename = imagename,
                  nsigma = nsigmas[-1])
    print('--------------------------')
    print('Self-calibration completed')
    print('--------------------------')
    myms_target = myms.replace('.ms', '_target.ms')
    export_ms(myms_selfcal, myms_target, target)

def jocelyn_clean(ms = '',
                  field = '',
                  datacolumn = 'corrected',
                  imagename = '',
                  imsize = cfg.IMSIZE,
                  cell = cfg.CELL,
                  gridder = cfg.GRIDDER,
                  wprojplanes = cfg.WPROJPLANES,
                  pblimit = cfg.PBLIMIT,
                  deconvolver = cfg.DECONVOLVER,
                  scales = cfg.SCALES,
                  nterms = cfg.NTERMS,
                  weighting = cfg.WEIGHTING,
                  robust = cfg.ROBUST,
                  niter = cfg.NITER,
                  nsigma = cfg.NSIGMA,
                  usemask = cfg.USEMASK,
                  pbmask = cfg.PBMASK,
                  sidelobethreshold = cfg.SIDELOBETHRESHOLD,
                  noisethreshold = cfg.NOISETHRESHOLD,
                  lownoisethreshold = cfg.LOWNOISETHRESHOLD,
                  minbeamfrac = cfg.MINBEAMFRAC,
                  fastnoise = False,
                  savemodel = 'modelcolumn',
                  parallel = cfg.PARALLEL):
    cell_auto, imsize_auto, _ = au.pickCellSize(vis = ms, npix = 5, imsize = True)
    _cell_ = cell_auto if cell == '' else cell
    _imsize_ = imsize_auto if imsize == '' else imsize
    tclean(vis = ms,
           field = field,
           datacolumn = datacolumn,
           imagename = imagename,
           imsize = _imsize_,
           cell = _cell_,
           gridder = gridder,
           wprojplanes = wprojplanes,
           pblimit = pblimit,
           deconvolver = deconvolver,
           scales = scales,
           nterms = nterms,
           weighting = weighting,
           robust = robust,
           niter = niter,
           nsigma = nsigma,
           usemask = usemask,
           pbmask = pbmask,
           sidelobethreshold = sidelobethreshold,
           noisethreshold = noisethreshold,
           lownoisethreshold = lownoisethreshold,
           minbeamfrac = minbeamfrac,
           fastnoise = fastnoise,
           savemodel = savemodel,
           parallel = parallel)

def export_ms(myms, myms_target, target = ''):
    split(vis = myms,
          outputvis = myms_target,
          field = target,
          datacolumn = 'corrected')

def main():
    os.chdir(cfg.PATH_BAND)
    with open(cfg.PATH_JSON, 'r') as read_file:
        info = json.load(read_file)
    print('------------------')
    print('Information loaded')
    print('------------------')
    if cfg.TELESCOPE == 'VLA':
        calibrate_VLA(info)
        deconvolve_VLA(info)
    elif cfg.TELESCOPE == 'ATCA':
        calibrate_ATCA(info)
        selfcal_ATCA(info)

if __name__ == "__main__":
    main()