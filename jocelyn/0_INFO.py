import glob, os, sys
import numpy as np
import pandas as pd
from casatasks import importvla, importatca, listobs, split, flagdata
import config as cfg
import tools

def import_archive(master_ms: str):
    """
    Find an input archive file and convert it to a Measurement Set (MS).
    """
    if not os.path.exists(master_ms):
        if cfg.TELESCOPE == 'VLA':
            archive_filename = glob.glob(cfg.PATH_OBS + '/*.exp')
            importvla(archivefiles = archive_filename, vis = master_ms)
        elif cfg.TELESCOPE == 'ATCA':
            archive_filename = glob.glob(cfg.PATH_OBS + '/*.C*')
            importatca(vis = master_ms, files = archive_filename, options = 'birdie, noac')
        tools.jocelyn_log(f'{cfg.TELESCOPE} archive imported')
    else:
        tools.jocelyn_log('Master MS found')
    listobs(master_ms, listfile = master_ms + '.listobs')

def get_info(master_ms: str) -> dict:
    """
    Collect information about the main MS.
    """
    spw, freq = tools.get_spw(master_ms, cfg.BAND)
    list_obs = listobs(master_ms, spw = spw)
    target, fcal = tools.get_target_fcal(master_ms)
    pcal = tools.get_pcal(list_obs, master_ms)
    scans = tools.check_scans(list_obs, master_ms) if cfg.SCANS == 'auto' else cfg.SCANS
    MJD, date, time = tools.get_date_time(list_obs, master_ms, target)
    myms = '_'.join([cfg.TARGET, cfg.TELESCOPE, date, cfg.BAND + 'band.ms'])

    # Save the gathered information into a JSON file.
    info = {
        "ms":myms,
        "spw":spw,
        "mean_freq":freq,
        "fields":{
            "target":target,
            "pcal":pcal,
            "fcal":fcal
        },
        "scans":scans,
        "datetime":{
            "MJD":MJD,
            "date":date,
            "time":time
        }
    }
    if not os.path.exists(cfg.PATH_BAND):
        os.makedirs(cfg.PATH_BAND)
    tools.info_json(mode = 'w', info = info)
    tools.jocelyn_log('Information collected')
    return info

def split_ms(master_ms: str, info: dict):
    """
    Create a new MS with the fields and spectral windows of interest.
    """
    myms = cfg.PATH_BAND + info['ms']
    spw = info['spw']
    target = info['fields']['target']
    pcal = info['fields']['pcal']
    fcal = info['fields']['fcal']
    scans = info['scans']
    split(vis = master_ms,
          outputvis = myms,
          spw = spw,
          field = ','.join([target, pcal, fcal]),
          scan = ','.join(scans),
          datacolumn = 'data')
    listobs(myms, listfile = cfg.PATH_BAND + 'list.obs')
    tools.jocelyn_log('MS splitted')

def flag_cal_uvrange(myms: str, fcal: str, pcal: str):
    """
    Perform flagging of the calibrators based on the recommended UV range at a given frequency.
    """
    for cal_field in [pcal, fcal]:
        cal_name = cal_field.split('_')[0]
        # Load the recommanded UV range
        UVrange = pd.read_csv(cfg.PATH_JOCELYN + f'data/calibrators_UVrange/{cal_name}.csv', sep = '\t')
        UVmin = UVrange[UVrange['BAND'] == cfg.BAND]['UVMIN'].iloc[0]
        UVmax = UVrange[UVrange['BAND'] == cfg.BAND]['UVMAX'].iloc[0]
        # Flag calibrators outside the UV range
        if not np.isnan(UVmin):
            try:
                flagdata(vis = myms,
                         mode = 'manual',
                         field = cal_name,
                         uvrange = f'<{int(UVmin)}klambda')
            except:
                pass
        if not np.isnan(UVmax):
            try:
                flagdata(vis = myms,
                         mode = 'manual',
                         field = cal_name,
                         uvrange = f'>{int(UVmax)}klambda')
            except:
                pass

def basic_flagging(info: dict):
    """
    Deterministic flagging (quack, clip, shadowing, UV range).
    """
    myms = cfg.PATH_BAND + info['ms']
    fcal = info['fields']['fcal']
    pcal = info['fields']['pcal']
    flagdata(vis = myms,
             mode = 'quack',
             quackinterval = 10.0,
             quackmode = 'beg')
    flagdata(vis = myms,
             mode = 'clip',
             clipzeros = True)
    flagdata(vis = myms,
             mode = 'clip',
             clipminmax = [0.0, 50.0])
    flagdata(vis = myms,
             mode = 'shadow',
             tolerance = 0.0)
    if cfg.TELESCOPE == 'VLA':
        flag_cal_uvrange(myms, fcal, pcal)
    tools.jocelyn_log('Basic flagging completed')

def main(options: str):
    """
    Run the first steps of the pipeline: import the archive data (i), gather some information
    about the observation (g) and apply basic flagging (f).
    """
    master_ms = cfg.PATH_OBS + '/master.ms'
    if options == '': # All the steps
        import_archive(master_ms)
        info = get_info(master_ms)
        split_ms(master_ms, info)
        if cfg.BASIC_FLAG:
            basic_flagging(info)
    else:
        steps = options.replace(' ', '').split(',') # Selection of step(s)
        if 'i' in steps:
            import_archive(master_ms)
        if 'g' in steps:
            info = get_info(master_ms)
            split_ms(master_ms, info)
        if 'f' in  steps:
            info = tools.info_json()
            if cfg.BASIC_FLAG:
                basic_flagging(info)

if __name__ == "__main__":
    options = sys.argv[1] if len(sys.argv) > 1 else ''
    main(options)