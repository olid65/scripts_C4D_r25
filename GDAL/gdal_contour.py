import c4d
import os.path


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

#-p pour générer de polygones
#-i -> intervalle
#-3D pour poly 3D

DIC_FORMATS = {
                'GeoJSON':'.geojson',
                'ESRI Shapefile':'.shp',
                'DXF':'.dxf',
                }

#Attention le GeoJson ne s'affiche pas dans Qgis !?

def gdal_comntour(fn_mnt,fn_curves = None, equidist=1, geom3D =True, form = 'GeoJSON'):

    #si le fichier de det n'est pas renseigné on fait un nom automatique
    if not fn_curves:
        name,ext = os.path.splitext(fn_mnt)
        fn_curves = name + f'_courbes{equidist}m' + DIC_FORMATS[form]

    pth_gdal_contour = '/Applications/QGIS.app/Contents/MacOS/bin/gdal_contour'
    if geom3D:
        g3D = '-3d'
    else:
        g3D = ''

    req = f"""{pth_gdal_contour} -p -amax ELEV_MAX -amin ELEV_MIN -b 1 -i {equidist} {g3D} -f "{form}" {fn_mnt} {fn_curves}"""
    print(req)

# Main function
def main():
    fn_mnt = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Trient2/swisstopo/swissalti3d_2m.asc'

    gdal_comntour(fn_mnt,fn_curves = None, equidist=10, geom3D =True)

# Execute main()
if __name__=='__main__':
    main()