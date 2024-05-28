import glob, sys, os
import config as cfg

def main(path_stack):
    os.chdir(path_stack)

    list_of_target_ms = glob.glob('../*/Cband/*_target.ms')
    myms = '4U1755_ATCA_Cband.ms'

    from casatasks import concat, tclean

    concat(vis = list_of_target_ms,
           concatvis = myms)

    imagename = myms.replace('.ms', '')
    # tclean(vis = myms,
    #        datacolumn = 'data',
    #        imagename = imagename,
    #        imsize = cfg.IMSIZE,
    #        cell = cfg.CELL,
    #        gridder = cfg.GRIDDER,
    #        wprojplanes = cfg.WPROJPLANES,
    #        pblimit = cfg.PBLIMIT,
    #        deconvolver = cfg.DECONVOLVER,
    #        scales = cfg.SCALES,
    #        weighting = cfg.WEIGHTING,
    #        robust = cfg.ROBUST,
    #        niter = 10000,
    #        nsigma = 3.0,
    #        usemask = cfg.USEMASK,
    #        pbmask = cfg.PBMASK,
    #        sidelobethreshold = 4.0,
    #        noisethreshold = cfg.NOISETHRESHOLD,
    #        lownoisethreshold = cfg.LOWNOISETHRESHOLD,
    #        minbeamfrac = cfg.MINBEAMFRAC,
    #        fastnoise = False,
    #        parallel = cfg.PARALLEL)
    tclean(vis = myms,
           datacolumn = 'data',
           imagename = imagename,
           imsize = cfg.IMSIZE,
           cell = cfg.CELL,
           gridder = cfg.GRIDDER,
           wprojplanes = cfg.WPROJPLANES,
           pblimit = cfg.PBLIMIT,
           deconvolver = cfg.DECONVOLVER,
           scales = cfg.SCALES,
           weighting = cfg.WEIGHTING,
           robust = cfg.ROBUST,
           niter = 10000,
           nsigma = 3,
           parallel = cfg.PARALLEL)

if __name__ == "__main__":
    main(sys.argv[1])