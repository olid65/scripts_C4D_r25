import c4d
import os.path
import sys
import subprocess


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate'):
    if sys.platform == 'win32':
        exe+='.exe'
    path = os.path.join(path_to_QGIS_bin,exe)
    if os.path.isfile(path):
        return path
    else:
        return False

def getPathToQGISbin(path_to_QGIS = None):
    #Si le path_to_QGIS n'est pas renseigné on prend le chemin par défaut selon la plateforme
    win = sys.platform == 'win32'
    if not path_to_QGIS:
        if sys.platform == 'win32':
            path_to_QGIS = 'C:\\Program Files'
        else:
            path_to_QGIS = '/Applications'
    for folder_name in os.listdir(path_to_QGIS):
        if 'QGIS'  in folder_name:
            if win :
                path = os.path.join(path_to_QGIS,folder_name,'bin')
            else:

                path = os.path.join(path_to_QGIS,folder_name,'Contents/MacOS/bin')

            if os.path.isdir(path):
                return path
    return None

#{path_to_gdalwarp} -overwrite -of {form} -cutline {fn_shp} -tr {cellsize} {cellsize} -cl {layer_name} -crop_to_cutline {fn_vrt} {fn_asc}

def extractFromSpline(fn_shp,raster_srce, raster_dst,cellsize, form = 'AAIGrid', path_to_gdalwarp = None):
    if not path_to_gdalwarp:
        path_to_QGIS_bin = getPathToQGISbin()
        if path_to_QGIS_bin:
            path_to_gdalwarp = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdalwarp')

    if not path_to_gdalwarp:
        c4d.gui.MessageDialog("L'extraction est impossible, gdal_translate non trouvé")
        return False
    
    layer_name = os.path.basename(fn_shp)[:-4]
    req = f"{path_to_gdalwarp} -overwrite -of {form} -cutline {fn_shp} -tr {cellsize} {cellsize} -cl {layer_name} -crop_to_cutline {raster_srce} {raster_dst}"
    output = subprocess.check_output(req,shell=True)
    
    if os.path.isfile(raster_dst):
        return raster_dst
    
    return False

# Main function
def main():
    fn_vrt = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/meyrin3/swisstopo/swissalti3d_50cm.vrt'
    fn_asc = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/meyrin3/swisstopo/swissalti3d_50cm_test_decoupe2.asc'
    fn_shp = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/meyrin3/swisstopo/decoupe_buffer1m.shp'
    
    path_to_gdalwarp = '/Applications/QGIS.app/Contents/MacOS/bin/gdalwarp'
    cellsize = 0.5
    
    extractFromSpline(fn_shp,fn_vrt, fn_asc,cellsize, form = 'AAIGrid')
    

# Execute main()
if __name__=='__main__':
    main()