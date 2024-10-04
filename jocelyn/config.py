import os

#----- Source and calibrators ----------------------------#
SOURCE = '4U1755'
TARGET = '4U1755-33'
PCAL = '1729-37'
FCAL = '1934-638'


#----- Observation ---------------------------------------#
DATES = ['2024-02-18',
         '2024-03-01',
         '2024-03-09',
         '2024-03-18',
         '2024-03-21',
         '2024-03-27',
         '2024-03-28',
         '2024-03-31']
TELESCOPE = 'ATCA'
BAND = 'C'

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


#----- Paths ---------------------------------------------#
PATH_OBS = os.getcwd()
PATH_CODE = PATH_OBS + '/jocelyn/'
PATH_BAND = PATH_OBS + f'/{BAND}band/'
PATH_JSON = PATH_BAND + 'info.json'
PATH_tables = PATH_BAND + 'tables/'
PATH_images = PATH_BAND + 'images/'


#----- Flagging ------------------------------------------#
BASIC_FLAG = True
MANUAL_FLAG = True


#----- Imaging parameters --------------------------------#
# Image
CELL = '0.3arcsec'
IMSIZE = 2560

# Gridder
GRIDDER = 'standard'
WPROJPLANES = -1
PBLIMIT = 0.1

# Deconvolution
DECONVOLVER = 'mtmfs'
SCALES = [0, 5, 10, 25, 50]
NTERMS = 2

# Weighting
WEIGHTING = 'briggs'
ROBUST = 2

# Stopping criteria
NITER = 10000
NSIGMA = 3
INTERACTIVE = False

# Mask
USEMASK = 'auto-multithresh'
PBMASK = 0.0
SIDELOBETHRESHOLD = 1.8
NOISETHRESHOLD = 6.0
LOWNOISETHRESHOLD = 6.0
MINBEAMFRAC = 0.15

# Parallel tclean
PARALLEL = True


#----- Stacking ------------------------------------------#
STACK_OBS = True
STACK_WEIGHTS = []
STACK_SELFCAL = True