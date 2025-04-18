import sys, os

def main(path, imagename, maskname, threshold):
    os.chdir(path)
    selection = 'select'
    ia.open(imagename)
    ia.calcmask(f'{imagename} > {threshold}', name = selection)
    ia.done()
    makemask(mode = 'copy',
             inpimage = imagename,
             inpmask = f'{imagename}:{selection}',
             output = maskname,
             overwrite = True)

if __name__ == "__main__":
    main(*sys.argv[1:])