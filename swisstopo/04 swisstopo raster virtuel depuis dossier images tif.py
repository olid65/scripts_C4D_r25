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

def dirImgToTextFile(path_dir, ext = '.tif'):
    """crée un fichier texte avec le chemin de l'image pour chaque ligne"""
    fn_txt = path_dir+'.txt'
    len_ext = len(ext)
    lst_img = [os.path.join(path_dir,fn) for fn in os.listdir(path_dir) if fn[-len_ext:] == ext]
    
    if lst_img :
        with open(fn_txt,'w') as f:
            for fn in lst_img:
                f.write(fn+'\n')
        return fn_txt
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
    #fichier texte avec listes images tif
    lst_img_txt = dirImgToTextFile(path_tifs, ext = '.tif')
    if lst_img_txt:
        req = f'"{path_to_gdalbuildvrt}" -input_file_list "{lst_img_txt}" "{fn_vrt}"'
        output = subprocess.check_output(req,shell=True)
        #on supprime le fichier txt
        os.remove(lst_img_txt)
        if os.path.isfile(fn_vrt):
            
            return fn_vrt
        
    return False

# Main function
def main():
    path_tifs = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY)
    if not path_tifs:
        return

    fn_vrt = (createVRTfromDir(path_tifs, path_to_gdalbuildvrt = None))
    return




# Execute main()
if __name__=='__main__':
    main()