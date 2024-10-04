# Jocelyn

## What is this?

A set of `Python` scripts to automatize basic data reduction of radio-interferometric observations. For now, the available arrays are the VLA and the ATCA. Jocelyn performs flagging, calibration and imaging (including self-calibration) within CASA.

## Prerequisites

You will need a modular version of CASA 6: https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Modular-Packages

## Quick start

1. Navigate to a working space.

2. Clone jocelyn into it:

   ```
   git clone https://github.com/noagrollimund/jocelyn.git .
   ```

3. Make a symlink to your MS or archive file (or place it in the working directory):

    ```
    ln -s /path/to/archive/VLA.exp .
    ```

4. (Optional) Add your CASA-friendly flag file of the format `*.flag` in the working directory.

4. Edit [`config.py`](config.py) to set your favorite parameters.

5. The first step of the pipeline is to run a script that imports the archive (i), gathers some information about the observation (g) and applies basic and manual flagging (f):

    ```
    python jocelyn/look.py
    ```

6. The second step is to run a script that will perform calibration (c) and imaging (i) of your data.

    ```
    python jocelyn/calibratimage.py
    ```

Notes: 

* If you want to run only some of the steps, you can specify them as arguments:

    ```
    python jocelyn/look.py i,g,f
    ...
    python jocelyn/calibratimage.py c,i
    ```

* If you want to run the whole pipeline without stopping between [`look.py`](look.py) and [`calibratimage.py`](calibratimage.py):

    ```
    python jocelyn/jocelyn.py
    ```