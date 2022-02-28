import c4d
import sys, os.path

sys.path.append(os.path.dirname(__file__))

from SIG import splines2geojson, grid2asc
from GDAL import gdal_contour


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    #fn = '/Users/olivierdonze/Documents/TEMP/mnt_temp.asc'
    grid2asc.main()


# Execute main()
if __name__=='__main__':
    main()