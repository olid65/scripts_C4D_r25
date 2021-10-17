import c4d, os
import sys
import subprocess
#import platform
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True
#


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

def gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate'):
    if sys.platform == 'win32':
        exe+='.exe'
    path = os.path.join(path_to_QGIS_bin,exe)
    if os.path.isfile(path):
        return path
    else:
        return False


def createVRTfromDir(path_tifs, path_to_gdalbuildvrt = None):
    if not path_to_gdalbuildvrt:
        path_to_QGIS_bin = getPathToQGISbin()
        if path_to_QGIS_bin:
            path_to_gdalbuildvrt = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdalbuildvrt')

    if not path_to_gdalbuildvrt:
        c4d.gui.MessageDialog("La génération du raster virtuel (.vrt) est impossible")
        return False
    fn_vrt = path_tifs+'.vrt'
    req = f'{path_to_gdalbuildvrt} {fn_vrt} {path_tifs}/*.tif'
    output = subprocess.check_output(req,shell=True)
    if os.path.isfile(fn_vrt):
        return fn_vrt
    return False

def extractFromBbox(raster_srce, raster_dst,xmin,ymin,xmax,ymax,path_to_gdal_translate = None):
    """normalement l'extension du fichier de destination permet le choix du format (à vérifier)
       si on a du .png ou du .jpg un fichier wld est généré"""

    name,ext = os.path.splitext(raster_dst)
    if ext in ['.jpg','.png']:
        wld = '-co worldfile=yes'
    else:
        wld = ''
    if not path_to_gdal_translate:
        path_to_QGIS_bin = getPathToQGISbin()
        if path_to_QGIS_bin:
            path_to_gdal_translate = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate')

    if not path_to_gdal_translate:
        c4d.gui.MessageDialog("L'extraction est impossible, gdal_translate non trouvé")
        return False
    req = f'{path_to_gdal_translate} {wld} -projwin {xmin} {ymax} {xmax} {ymin} {raster_srce} {raster_dst}'
    output = subprocess.check_output(req,shell=True)
    if os.path.isfile(raster_dst):
        return raster_dst

    return False



# Main function
def main():
    path_tifs = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY)
    if not path_tifs:
        retiurn
    
    fn_vrt = (createVRTfromDir(path_tifs, path_to_gdalbuildvrt = None))
    return




# Execute main()
if __name__=='__main__':
    main()