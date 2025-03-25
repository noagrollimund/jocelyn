import os

#----- Observation ---------------------------------------#
TARGET = ''
CAL_PRIMARY = ''
CAL_SECONDARY = ''
SCANS = ''
TELESCOPE = ''
BAND = 'C'


#----- Paths ---------------------------------------------#
PATH_OBS = os.getcwd()
PATH_CODE = PATH_OBS + '/jocelyn/'
PATH_BAND = PATH_OBS + f'/{BAND}-band/'
PATH_JSON = PATH_BAND + 'info.json'
PATH_TABLES = PATH_BAND + 'TABLES/'
PATH_IMAGES = PATH_BAND + 'IMAGES/'


#----- Flagging ------------------------------------------#
BASIC_FLAG = True
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
SIDELOBETHRESHOLD = 1.8
NOISETHRESHOLD = 6.0
LOWNOISETHRESHOLD = 6.0
MINBEAMFRAC = 0.15

# Parallel tclean
PARALLEL = False


#----- Self-calibration ----------------------------------#
N_ROUNDS_SELFCAL = 4
DO_AP_SELFCAL = True


#----- Cluster settings ----------------------------------#
CASA_CONTAINER_PATH = '/idia/software/containers/casa-6.simg'