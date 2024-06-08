import glob, json, os
import numpy as np
import pandas as pd
from casatasks import importvla, importatca, listobs, split, flagdata
import config as cfg
import tools

def import_archive(master_ms):
    if not os.path.exists(master_ms):
        if cfg.TELESCOPE == 'VLA':
            archive_filename = glob.glob(cfg.PATH_OBS + '/*.exp')
            importvla(archivefiles = archive_filename, vis = master_ms)
        elif cfg.TELESCOPE == 'ATCA':
            archive_filename = glob.glob(cfg.PATH_OBS + '/*.C*')
            importatca(vis = master_ms, files = archive_filename, options = 'birdie, noac')
        tools.jocelyn_log('Archive imported')
    else:
        tools.jocelyn_log('Master MS found')

def get_info(master_ms):
    spw, freq = tools.get_spw(master_ms, cfg.BAND)

    list_obs = listobs(master_ms, spw = spw)
    target, fcal = tools.get_target_fcal(master_ms)
    pcal = tools.get_pcal(list_obs, master_ms)

    scans = tools.check_scans(list_obs, master_ms)

    MJD, date, time = tools.get_date_time(list_obs, master_ms, target)
    myms = '_'.join([cfg.SOURCE, cfg.TELESCOPE, date, cfg.BAND + 'band.ms'])

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
    with open(cfg.PATH_JSON, "w") as write_file:
        json.dump(info, write_file)
    tools.jocelyn_log('Information collected')
    return info

def split_ms(master_ms, info):
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

def flag_cal_uvrange(myms, fcal, pcal):
    for cal_field in [pcal, fcal]:
        cal_name = cal_field.split('_')[0]
        UVrange = pd.read_csv('data/calibrators_UVrange/' + cal_name + '.csv', sep = '\t')
        UVmin = UVrange[UVrange['BAND'] == cfg.BAND]['UVMIN'].iloc[0]
        UVmax = UVrange[UVrange['BAND'] == cfg.BAND]['UVMAX'].iloc[0]
        if not np.isnan(UVmin):
            try:
                flagdata(vis = myms,
                         mode = 'manual',
                         field = cal_name,
                         uvrange = '<{}klambda'.format(int(UVmin)))
            except:
                pass
        if not np.isnan(UVmax):
            try:
                flagdata(vis = myms,
                         mode = 'manual',
                         field = cal_name,
                         uvrange = '>{}klambda'.format(int(UVmax)))
            except:
                pass

def basic_flagging(info):
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
    if cfg.TELESCOPE == 'VLA':
        flagdata(vis = myms,
                mode = 'shadow',
                tolerance = 0.0)
        flag_cal_uvrange(myms, fcal, pcal)
    tools.jocelyn_log('Basic flagging completed')

def manual_flagging(info):
    myms = cfg.PATH_BAND + info['ms']
    flags_filename = glob.glob(cfg.PATH_OBS + '/*_flags.py')[0]
    if flags_filename == []:
        tools.jocelyn_log('No flagging file found')
    else:
        exec(open(flags_filename).read(), {'myms': myms})
        tools.jocelyn_log('Manual flagging completed')

def main():
    master_ms = cfg.PATH_OBS + '/master.ms'
    import_archive(master_ms)
    info = get_info(master_ms)
    split_ms(master_ms, info)
    if cfg.BASIC_FLAG:
        basic_flagging(info)
    if cfg.MANUAL_FLAG:
        manual_flagging(info)

if __name__ == "__main__":
    main()