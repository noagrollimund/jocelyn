import sys, os
import tools
import config as cfg

def compact_blind_imaging(myms, imagename):
    tools.jclean(ms = myms,
                 uvrange = cfg.TCLEAN_UVRANGE,
                 imagename = imagename,
                 scales = [],
                 savemodel = 'none')
    tools.jocelyn_log('Blind deconvolution completed')

def compact_masked_imaging(myms, imagename, mask):
    tools.jclean(ms = myms,
                 uvrange = cfg.TCLEAN_UVRANGE,
                 imagename = imagename,
                 scales = [],
                 usemask = 'user',
                 mask = mask,
                 savemodel = 'none')
    tools.jocelyn_log('Masked deconvolution completed')

def main(options):
    os.chdir(cfg.PATH_BAND)
    info = tools.info_json()
    myms = info['ms']
    myms_target = myms.replace('.ms', '_target.ms')
    imagename_blind = 'compact_blind'
    im_suffix = 'image.tt0' if cfg.DECONVOLVER == 'mtmfs' else 'image'
    maskname = imagename_blind + '_threshmask'
    imagename_masked = cfg.PATH_IMAGES + myms.split('/')[-1].replace('.ms', '_compact_masked')
    if options == '':
        compact_blind_imaging(myms_target, cfg.PATH_IMAGES + imagename_blind)
        os.system(f'casa -c {cfg.PATH_JOCELYN}make_thresh_mask.py {cfg.PATH_IMAGES} {imagename_blind}.{im_suffix} {maskname} {cfg.MASK_THRESHOLD}')
        tools.jocelyn_log('Thresholded mask generated')
        compact_masked_imaging(myms_target, imagename_masked, cfg.PATH_IMAGES + maskname)
    else:
        steps = options.replace(' ', '').split(',')
        if 'b' in steps:
            compact_blind_imaging(myms_target, cfg.PATH_IMAGES + imagename_blind)
        if 'm' in steps:
            os.system(f'casa -c {cfg.PATH_JOCELYN}make_thresh_mask.py {cfg.PATH_IMAGES} {imagename_blind}.{im_suffix} {maskname} {cfg.MASK_THRESHOLD}')
            tools.jocelyn_log('Thresholded mask generated')
        if 'i' in steps:
            compact_masked_imaging(myms_target, imagename_masked, cfg.PATH_IMAGES + maskname)

if __name__ == "__main__":
    options = sys.argv[1] if len(sys.argv) > 1 else ''
    main(options)