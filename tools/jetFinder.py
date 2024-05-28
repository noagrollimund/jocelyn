import glob, os, sys
from casatasks import concat, tclean
import tools.tools as tools
import config as cfg

def concatenate_vis(path_data):
    os.chdir(path_data)
    vis = glob.glob('*.ms')
    if len(vis) == 1:
        return vis[0]
    vis.sort()
    vis = [ms for ms in vis if '--' not in ms]
    dates = [ms_name.split('_')[1] for ms_name in vis]
    first_date, last_date = dates[0], dates[-1]
    if first_date.split('-')[1] == last_date.split('-')[1]:
        combined_date = first_date + '--' + '-'.join([last_date.split('-')[-1]])
    else:
        combined_date = first_date + '--' + '-'.join(last_date.split('-')[-2:])
    prefix = vis[0].split('_')[0]
    suffix = '_'.join(vis[0].split('_')[2:])
    concatvis = '_'.join([prefix, combined_date, suffix])
    if not os.path.exists(concatvis):
        concat(vis = vis, concatvis = concatvis)
    return concatvis

def deconvolve(path_data, ms, weighting):
    imagename = weighting + '/' + ms.replace('_target.ms', '')
    cell = tools.compute_cell(cfg.BAND, cfg.VLA_CONFIG)
    imsize = tools.compute_imsize(cfg.BAND, cell)
    os.chdir(path_data)
    if weighting == 'briggs':
        tclean(vis = ms,
            datacolumn = 'data',
            cell = cell,
            imsize = imsize,
            imagename = imagename,
            weighting = weighting,
            robust = 0,
            niter = 200)
    else:
        tclean(vis = ms,
            datacolumn = 'data',
            cell = cell,
            imsize = imsize,
            imagename = imagename,
            weighting = weighting,
            niter = 200)

def main(weighting):
    path_code = os.getcwd()
    path_data = os.path.dirname(path_code)
    ms = concatenate_vis(path_data)
    os.chdir(path_code)
    deconvolve(path_data, ms, weighting)

if __name__ == "__main__":
    main(sys.argv[1])