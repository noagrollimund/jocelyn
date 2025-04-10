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

5. The first step of the pipeline is to run a script that imports the archive (i), gathers some information about the observation (g) and applies basic and auto flagging (f):

    ```
    python jocelyn/0_INFO.py
    ```

6. The second step is to run a script that will perform manual flagging (f), calibration (c) and imaging (i) of your data:

    ```
    python jocelyn/1GC.py
    ```

7. The third step self-calibrates the data (several rounds of phase-only selfcal, then phase and amplitude selfcal):

    ```
    python jocelyn/2GC.py
    ```

Notes: 

* If you want to run only some of the steps, you can specify them as arguments:

    ```
    python jocelyn/0_INFO.py i,g,f
    ...
    python jocelyn/1GC.py f,c,i
    ...
    python jocelyn/2GC.py
    ```