import c4d
import os.path
import sys
import subprocess
import shapefile


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN =1026473

def fichierPRJ(fn):
    fn = os.path.splitext(fn)[0]+'.prj'
    f = open(fn,'w')
    f.write("""PROJCS["CH1903+_LV95",GEOGCS["GCS_CH1903+",DATUM["D_CH1903+",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",46.95240555555556],PARAMETER["longitude_of_center",7.439583333333333],PARAMETER["azimuth",90],PARAMETER["scale_factor",1],PARAMETER["false_easting",2600000],PARAMETER["false_northing",1200000],UNIT["Meter",1]]""")
    f.close()

def createOutline(sp,distance,doc):
    bc = c4d.BaseContainer()
    bc[c4d.MDATA_SPLINE_OUTLINE] = distance
    bc[c4d.MDATA_SPLINE_OUTLINESEPARATE] = True
    res = c4d.utils.SendModelingCommand(command = c4d.MCOMMAND_SPLINE_CREATEOUTLINE,
                                list = [sp],
                                mode = c4d.MODELINGCOMMANDMODE_ALL,
                                bc = bc,
                                doc = doc)
    if res :
        return res[0]
    else :
        return None

def shapefileFromSpline(sp,doc,fn,buffer = 0):
    origine = doc[CONTAINER_ORIGIN]
    if not origine: return None

    if buffer :
        sp = createOutline(sp,buffer,doc)
        if not sp :
            print("problème outline")
            return
    nb_seg = sp.GetSegmentCount()
    mg = sp.GetMg()
    pts = [p*mg+origine for p in sp.GetAllPoints()]

    #UN SEUL SEGMENT
    if not nb_seg :
        poly = [[[p.x,p.z] for p in pts]]

    #MULTISEGMENT (attention avec segments interne à un autre il faut les points antihoraire)
    else:
        poly = []
        id_pt = 0
        for i in range(nb_seg):
            cnt = sp.GetSegment(i)['cnt']
            poly.append([[p.x,p.z] for p in pts[id_pt:id_pt+cnt]])
            id_pt +=cnt

    with shapefile.Writer(fn,shapefile.POLYGON) as w:
        w.field('id','I')
        w.record(1)
        w.poly(poly)

        fichierPRJ(fn)
    
    if os.path.isfile(fn):
        return fn
    
    return None

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
    
    cellsize = 0.5
    
    sp = op.GetRealSpline()
    
    #création du shapefile pour la découpe
    fn_shp = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Meyrin4/swisstopo/decoupe_buffer50cm.shp'
    fn_shp = shapefileFromSpline(sp,doc,fn_shp,buffer = cellsize*2)
    if not fn_shp :
        print("problème lors de la création du shapefile")
        return
    
    fn_vrt = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Meyrin4/swisstopo/swissalti3d_50cm.vrt'
    fn_asc = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Meyrin4/swisstopo/swissalti3d_50cm_test_decoupe3.asc'
    
    
    path_to_gdalwarp = '/Applications/QGIS.app/Contents/MacOS/bin/gdalwarp'
    cellsize = 0.5
    
    extractFromSpline(fn_shp,fn_vrt, fn_asc,cellsize, form = 'AAIGrid')
    

# Execute main()
if __name__=='__main__':
    main()