import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json, sys, os
from scipy import stats
from astropy.time import Time
from casatasks import flagdata, gaincal, tclean
from casatools import table, msmetadata
import config as cfg
sys.path.append(os.path.expanduser('~') + '/analysis_scripts/')
import analysisUtils as au

BAND_DEFINITIONS = {
    'L':[1e9, 2e9],
    'S':[2e9, 4e9],
    'C':[4e9, 8e9],
    'X':[8e9, 12e9],
    'Ku':[12e9, 18e9],
    'K':[18.0e9, 26.5e9],
    'Ka':[26.5e9, 40.0e9],
    'Q':[40.0e9, 50.0e9],
    '':[0, 100e9]
    }

def jocelyn_log(message):
    print('--/jocelyn/--: ' + message)

def info_json(mode = 'r', info = {}):
    with open(cfg.PATH_JSON, mode) as file:
        if mode == 'r':
            info = json.load(file)
            return info
        if mode == 'w':
            json.dump(info, file)

def select_keys_with_kwrd(dict, keyword):
    return [key for key in dict.keys() if key[:len(keyword)] == keyword]

def get_spw(myms, band_name):
    freq_min, freq_max = BAND_DEFINITIONS[band_name]
    tb = table(myms + '/SPECTRAL_WINDOW')
    central_freqs = tb.getcol('REF_FREQUENCY')
    tb.close()
    spw, freq = [], []
    for SpwID, CtrFreq in enumerate(central_freqs):
        if CtrFreq > freq_min and CtrFreq < freq_max:
            spw.append(str(SpwID))
            freq.append(CtrFreq)
    return ', '.join(spw), np.mean(freq)

def get_target_fcal(myms):
    if type(cfg.TARGET) == str:
        target_name = cfg.TARGET
    else:
        tb = table(myms + '/FIELD')
        fields = tb.getcol('NAME')
        tb.close()
        for field in fields:
            if field in cfg.TARGET:
                target_name = field
    if type(cfg.CAL_PRIMARY) == str:
        fcal_name = cfg.CAL_PRIMARY
    else:
        tb = table(myms + '/FIELD')
        fields = tb.getcol('NAME')
        tb.close()
        for field in fields:
            if field in cfg.CAL_PRIMARY:
                fcal_name = field
    return target_name, fcal_name

def get_pcal(obs, myms):
    if type(cfg.CAL_SECONDARY) == str:
        pcal_name = cfg.CAL_SECONDARY
    else:
        tb = table(myms + '/FIELD')
        fields = tb.getcol('NAME')
        tb.close()
        for field in fields:
            scans_all = get_scans(obs)
            if field in cfg.CAL_SECONDARY:
                scans = check_scans(obs, myms, field)
                if scans != []:
                    scan_idx = scans_all.index(int(scans[0]))
                    if is_close_to_target(obs, myms, scan_idx):
                        pcal_name = field
    return pcal_name

def scan2field_name(obs, scan_idx):
    scan_ids = get_scans(obs)
    scan_name = 'scan_' + str(scan_ids[scan_idx])
    field_name = str(obs[scan_name]['0']['FieldName'])
    return field_name

def is_close_to_target(obs, myms, scan_idx):
    scan_ids = get_scans(obs)
    scan_idx = int(scan_idx)
    target, _ = get_target_fcal(myms)
    if scan_idx > 0 and scan_idx < len(scan_ids) - 1:
        field_name_before = scan2field_name(obs, scan_idx - 1)
        field_name_after = scan2field_name(obs, scan_idx + 1)
        return field_name_before == target or field_name_after == target
    elif scan_idx == 0:
        field_name_after = scan2field_name(obs, scan_idx + 1)
        return field_name_after == target
    elif scan_idx == len(scan_ids) - 1:
        field_name_before = scan2field_name(obs, scan_idx - 1)
        return field_name_before == target

def get_scans(obs):
    scan_names = select_keys_with_kwrd(obs, 'scan')
    scan_ids = sorted([obs[scan_name]['0']['scanId'] for scan_name in scan_names])
    return scan_ids

def check_scans(obs, myms, field_name_select = None):
    target, fcal = get_target_fcal(myms)
    scan_ids = get_scans(obs)
    scans_to_keep = []
    for i in range(len(scan_ids)):
        scan_name = 'scan_' + str(scan_ids[i])
        field_name = str(obs[scan_name]['0']['FieldName'])
        is_target = field_name == target
        is_fcal = field_name == fcal
        is_pcal_close = field_name in cfg.CAL_SECONDARY and is_close_to_target(obs, myms, i)
        if field_name_select != None:
            good_field = field_name == field_name_select
            if (is_target or is_fcal or is_pcal_close) and good_field:
                scans_to_keep.append(str(scan_ids[i]))
        else:
            if is_target or is_fcal or is_pcal_close:
                scans_to_keep.append(str(scan_ids[i]))
    return scans_to_keep

def get_date_time(obs, myms, target):
    scans = check_scans(obs, myms, target)
    MJD = obs['scan_' + scans[0]]['0']['BeginTime']
    t = Time(MJD, format = 'mjd')
    date = t.iso.split(' ')[0]
    time = t.iso.split(' ')[1]
    return MJD, date, time

def dist_to_center(x, y, z):
    return np.sqrt(x**2 + y**2 + z**2)

def date_time_to_MJD(year, date, time):
    if type(date) != str:
        return -1
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    month = months.index(date[:3]) + 1
    month = '%02d' % month
    day = date[3:]
    t_iso = ' '.join(['-'.join([year, month, day]), time])
    t = Time(t_iso, format = 'iso')
    return t.mjd

def VLA_corrected_baselines(date_obs, time, working_ants):
    year = date_obs.split('-')[0]
    source_filename = cfg.PATH_CODE + f'data/baselines_corrections/VLA_baseline_corr_{year}.txt'
    df = pd.read_fwf(source_filename, skiprows = 2, widths = [7, 10, 8, 8, 5, 4, 8, 8, 8])
    for B in ['Bx', 'By', 'Bz']:
        df[B].apply(float)
    df['MOVED_MJD'] = df.apply(lambda row: date_time_to_MJD(year, row['MOVED'], '00:00:00.0'), axis = 1)
    df['Put_In_MJD'] = df.apply(lambda row: date_time_to_MJD(year, row['Put_In_'], row['MC(IAT)']), axis = 1)

    t_obs = Time(' '.join([date_obs, time]), format = 'iso')
    df1 = df[df['Put_In_MJD'] > t_obs.mjd]
    antenna_names = ['VA%02d' % i for i in range(1, 29)]
    antennas, corrections = [], []
    for antenna_number in range(1, 29):
        df2 = df1[df1['ANT'] == antenna_number]
        following_dates = df2[df2['MOVED_MJD'] > t_obs.mjd].index.values
        if following_dates.size > 0:
            next_move_date = min(following_dates)
            df3 = df2.loc[:next_move_date-1]
        else:
            df3 = df2
        correction = [df3[B].sum() for B in ['Bx', 'By', 'Bz']]
        antenna_name = antenna_names[antenna_number - 1]
        if sum(correction) != 0 and antenna_name in working_ants:
            antennas.append(antenna_name)
            corrections += correction
    if corrections == []:
        antennas = 'VA01'
        corrections = [0., 0., 0.]
    else:
        antennas = ', '.join(antennas)
    return antennas, corrections

def antenna_dist2cofa(ms):
    tb = table(ms + '/ANTENNA')
    msmd = msmetadata()
    msmd.open(ms)
    antennas = tb.getcol('NAME')
    tb.close()
    distances = []
    for antenna in antennas:
        antennna_offset = msmd.antennaoffset(antenna)
        latitude_offset = antennna_offset['latitude offset']['value']
        longitude_offset = antennna_offset['longitude offset']['value']
        elevation_offset = antennna_offset['elevation offset']['value']
        dist = dist_to_center(latitude_offset, longitude_offset, elevation_offset)
        distances.append(dist)
    msmd.done()
    sorted_antennas = [ant_name for _, ant_name in sorted(zip(distances, antennas))]
    return sorted_antennas

def find_best_refant(info, nb_ctr_ant = 6):
    myms = info['ms']
    sorted_antennas = antenna_dist2cofa(myms)
    flagging_antennas = flagdata(myms, mode = 'summary')['antenna']
    central_antennas = sorted_antennas[:nb_ctr_ant]
    flag_percentages = []
    for antenna in central_antennas:
        ant_flags = flagging_antennas[antenna]
        perc = ant_flags['flagged'] / ant_flags['total']
        flag_percentages.append(perc)
    best_antennas = [ant_name for _, ant_name in sorted(zip(flag_percentages, central_antennas))]
    refant = best_antennas[0]
    info['refant'] = refant
    with open(cfg.PATH_JSON, "w") as write_file:
        json.dump(info, write_file)
    jocelyn_log('Best reference antenna found')
    return refant

def find_best_solint(myms, target, refant):
    tb = table()
    _, ax = plt.subplots()
    for solint in ['int', '20s', '40s', '80s', '160s', '320s', '640s']:
        caltable = cfg.PATH_TABLES + 'selfcal_' + solint
        gaincal(vis = myms,
                caltable = caltable,
                field = target,
                solint = solint,
                refant = refant,
                calmode = 'p',
                gaintype = 'T',
                minsnr = 0)
        tb.open(caltable)
        snr = tb.getcol('SNR').ravel()
        tb.close()
        ax.hist(snr, bins = 50, density = True, histtype = 'step', label = solint)
        ax.set_xlabel('SNR')
        ax.legend(loc = 'upper right')
        print(f'P(<=3) = {stats.percentileofscore(snr, 3)} ({solint})')
    plt.savefig('SNR_gaincal_SC_vs_solint.png')

def jclean(ms = '',
           field = '0',
           uvrange = cfg.TCLEAN_UVRANGE,
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
           interactive = cfg.INTERACTIVE,
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
           uvrange = uvrange,
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
           interactive = interactive,
           usemask = usemask,
           pbmask = pbmask,
           sidelobethreshold = sidelobethreshold,
           noisethreshold = noisethreshold,
           lownoisethreshold = lownoisethreshold,
           minbeamfrac = minbeamfrac,
           fastnoise = fastnoise,
           savemodel = savemodel,
           parallel = parallel)