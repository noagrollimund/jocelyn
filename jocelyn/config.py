import os

#----- Observation ---------------------------------------#
TARGET = ''
CAL_PRIMARY = ''
CAL_SECONDARY = ''
SCANS = ''
TELESCOPE = ''
BAND = 'C'


#----- Paths ---------------------------------------------#
PATH_OBS = os.getcwd() + '/'
PATH_JOCELYN = PATH_OBS + 'jocelyn/'
PATH_SCRIPTS = PATH_OBS + 'SCRIPTS/'
PATH_LOGS = PATH_OBS + 'LOGS/'
PATH_BAND = PATH_OBS + f'{BAND}-band/'
PATH_JSON = PATH_BAND + 'info.json'
PATH_TABLES = PATH_BAND + 'TABLES/'
PATH_IMAGES = PATH_BAND + 'IMAGES/'


#----- Flagging ------------------------------------------#
BASIC_FLAG = True
AUTO_FLAG = True
MANUAL_FLAG = True


#----- Imaging parameters --------------------------------#
# Data selection
TCLEAN_UVRANGE = ''
# Image dimensions
CELL = ''
IMSIZE = ''
# Gridding
GRIDDER = 'standard'
WPROJPLANES = -1
PBLIMIT = 0.1
# Weighting
WEIGHTING = 'briggs'
ROBUST = 0
# Deconvolution
DECONVOLVER = 'hogbom'
SCALES = []
NTERMS = 2
NITER = 50000
NSIGMA = 3
INTERACTIVE = False
# Masking
USEMASK = 'auto-multithresh'
PBMASK = 0.0
SIDELOBETHRESHOLD = 1.25
NOISETHRESHOLD = 5.0
LOWNOISETHRESHOLD = 3.0
MINBEAMFRAC = 0.1
# Parallel tclean
PARALLEL = False


#----- Self-calibration ----------------------------------#
N_ROUNDS_SELFCAL = 4
DO_AP_SELFCAL = True


#----- Cluster settings ----------------------------------#
CASA_CONTAINER_PATH = '/idia/software/containers/casa-6.5.0-modular.sif'