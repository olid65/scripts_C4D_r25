import c4d,os
import subprocess,sys


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

['gdal_translate.exe','gdalbuildvrt.exe']

def getPathToQGISbin(path_to_QGIS = None, win = True):
    
    #Si le path_to_QGIS n'est pas renseigné on prend le chemin par défaut selon la plateforme
    if not path_to_QGIS:
        if win :
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

def gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate',win = True):
    if win:
        exe+='.exe'
    path = os.path.join(path_to_QGIS_bin,exe)
    if os.path.isfile(path):
        return path
    else:
        return False

# Main function
def main():
    win = False
    if sys.platform == 'win32':
        win=True
    path_to_QGIS_bin = getPathToQGISbin(win=win)
    print(path_to_QGIS_bin)

    if path_to_QGIS_bin:
        gdaltranslate = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate',win = win)
        if gdaltranslate : print(gdaltranslate)

        gdalbuildvrt = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdalbuildvrt',win = win)
        if gdalbuildvrt : print(gdalbuildvrt)
    
    return
    src = 'E:\\OD\\TEMP\\ch.swisstopo.swissalti3d-VlGA00Tg_tif\\*.tif'
    vrt =  'E:\\OD\\TEMP\\ch.swisstopo.swissalti3d-VlGA00Tg_tif.vrt'

    asc = vrt.replace('.vrt','.asc')
    print(asc)
    subprocess.run(f'{gdalbuildvrt} {vrt} {src}')

    subprocess.run(f'{gdaltranslate} -of AAIGrid {vrt} {asc}')



# Execute main()
if __name__=='__main__':
    main()