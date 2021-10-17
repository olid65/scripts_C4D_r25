import c4d,os,sys
import subprocess
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


TXT = """Pour le découpage il faut soit activer un objet avec une géométrie, soit se mettre dans la vue de haut et zoomer sur la zone à extraire"""
CONTAINER_ORIGIN =1026473


def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi


def empriseObject(obj, origine):
    mg = obj.GetMg()

    rad = obj.GetRad()
    centre = obj.GetMp()

    # 4 points de la bbox selon orientation de l'objet
    pts = [c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z + rad.z) * mg]

    mini = c4d.Vector(min([p.x for p in pts]), min([p.y for p in pts]), min([p.z for p in pts])) + origine
    maxi = c4d.Vector(max([p.x for p in pts]), max([p.y for p in pts]), max([p.z for p in pts])) + origine

    return mini, maxi

#GDAL
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
    
    doc = c4d.documents.GetActiveDocument()
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        c4d.gui.MessageDialog("Le document n'est pas géréférencé")
        return
    
    op = doc.GetActiveObject()
    mini,maxi = None,None
    #Si on a un objet sélectionnée on prend la bbox de l'objet'
    if op:
        mini,maxi = empriseObject(op,doc[CONTAINER_ORIGIN])    
        
    if not mini or not maxi or mini==maxi:
        bd = doc.GetActiveBaseDraw()
        camera = bd.GetSceneCamera(doc)
        if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
                c4d.gui.MessageDialog(TXT)
                return
        mini,maxi = empriseVueHaut(bd, doc[CONTAINER_ORIGIN])

    raster_srce = c4d.storage.LoadDialog(title="Fichier raster source (.vrt ou image géoréférencée)",type = c4d.FILESELECTTYPE_ANYTHING)
    if not raster_srce:
        return
    #si swissalti3d dans le nom du fichier src -> mnt donc on génère un asc
    if 'swissalti3d'in raster_srce:
        raster_dst = raster_srce[:-4]+'.asc'
    #sinon plutôt un png    
    else:
        raster_dst = raster_srce[:-4]+'.png'
    raster_dst = c4d.storage.SaveDialog(title="Fichier de destination (l'extension détermine le type)", def_file=raster_dst)    
    if not raster_dst : return
    
    xmin = mini.x
    xmax = maxi.x
    ymin = mini.z
    ymax = maxi.z
    extractFromBbox(raster_srce, raster_dst,xmin,ymin,xmax,ymax,path_to_gdal_translate = None)


# Execute main()
if __name__=='__main__':
    main()