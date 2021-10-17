import c4d, os
import urllib.request
import json
from pprint import pprint
import zipfile
import io
from glob import glob

#Liste de liste des couches avec nom,url
LYRS =  [["CN10","Carte nationale 1:10'000","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.landeskarte-farbe-10"],
        ["CN25","Carte nationale 1:25'000","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.pixelkarte-farbe-pk25.noscale"],
        ["CN50","Carte nationale 1:50'000","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.pixelkarte-farbe-pk50.noscale"],
        ["Ortho","Orthophoto","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissimage-dop10"],
        ["MNT","MNT 50cm ou 2m","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d"],
        ["MNS","MNS 50cm ou 2m","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swisssurface3d-raster"],
        ["Bati3D","Swissbuildings3D","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissbuildings3d_2"]]


#["Carte nationale 1:10'000","https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swisssurface3d -> LIDAR


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473


def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini.x,mini.z,maxi.x,maxi.z


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

    return mini.x,mini.z,maxi.x,maxi.z

def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])
    

def get_list_from_STAC_swisstopo(list_layers,xmin,ymin,xmax,ymax):
    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"
    
    #parcours des couches pour listes des fichiers à télécharger
    for abrev,nom_lyr,url in list_layers:
        url += sufixe_url
        f = urllib.request.urlopen(url)
        txt = f.read().decode('utf-8')
        json_res = json.loads(txt)

        for item in json_res['features']:
            for k,dic in item['assets'].items():
                print(dic['href'])



def downloadSwissBuildingDXF(url,directory_dest):
    f = urllib.request.urlopen(url)
    z = zipfile.ZipFile(io.BytesIO(f.read()))
    z.extractall(directory_dest)
    
# Main function
def main():

    origine = doc [CONTAINER_ORIGIN]
    if not origine:
        c4d.gui.MessageDialog("Document non géréférencé, import impossible !")
        return

    xmin,ymin,xmax,ymax = 0,0,0,0
    #on regarde si un objet est sélectionné et s'il a une géométrie
    if op :
        xmin,ymin,xmax,ymax = empriseObject(op, origine)

    #s'il n'y a pas d'objet sélectionné ou si la bbox n'a pas de surface on prend la vue de haut
    if  (xmax-xmin)*(ymax-ymin) <= 0:
        bd = doc.GetActiveBaseDraw()
        camera = bd.GetSceneCamera(doc)

        if not camera[c4d.CAMERA_PROJECTION]== c4d.Ptop:
            c4d.gui.MessageDialog("Il faut soit sélectionner un objet avec une géométrie soit activer une vue de haut")
            return
        xmin,ymin,xmax,ymax = empriseVueHaut(bd, origine)
        
    get_list_from_STAC_swisstopo(LYRS,xmin,ymin,xmax,ymax)
    return






    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"


    #parcours des couches pour listes des fichiers à télécharger
    for abrev,nom_lyr,url in LYRS:
        url += sufixe_url
        f = urllib.request.urlopen(url)
        txt = f.read().decode('utf-8')
        json_res = json.loads(txt)

        for item in json_res['features']:
            for k,dic in item['assets'].items():
                print(dic['href'])





    return


    #Choix du dossier pour le dépôt des fichiers
    #pth_dst = '/Users/donzeo/Documents/TEMP/SWISSTOPO_buildings3D_dxf'

    pth_dst = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY,title="Séléctionnez le dossier pour enregistrer les fichiers dxf")

    if not pth_dst : return

    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    url = f'https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissbuildings3d_2/items?bbox={est},{sud},{ouest},{nord}'

    f = urllib.request.urlopen(url)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    #Téléchargement des dxf
    for item in json_res['features']:
        for k,dic in item['assets'].items():
            name = k
            typ = dic['type'] # si 'application/x.dxf+zip' -> dxf 'application/x.filegdb+zip' -> gdb
            #on prend que les dxf
            if typ ==  'application/x.dxf+zip':
                downloadSwissBuildingDXF(dic['href'],pth_dst)

    #Importation des DXF

    #mise en cm des option d'importation DXF
    plug = c4d.plugins.FindPlugin(1001035, c4d.PLUGINTYPE_SCENELOADER)

    dic = {}

    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, dic):

        import_data = dic.get("imexporter",None)

        if not import_data:
            print ("pas de data pour l'import 3Ds")
            return

        scale = import_data[c4d.DXFIMPORTFILTER_SCALE]
        scale.SetUnitScale(1,c4d.DOCUMENT_UNIT_M)

        import_data[c4d.DXFIMPORTFILTER_SCALE] = scale

        import_data[c4d.DXFIMPORTFILTER_LAYER] = c4d.DXFIMPORTFILTER_LAYER_NONE

    i = 0
    first_obj = doc.GetFirstObject()
    for fn in glob(os.path.join(pth_dst,'*.dxf')):
        c4d.documents.MergeDocument(doc, fn, c4d.SCENEFILTER_OBJECTS,None)
        obj = doc.GetFirstObject()
        if not obj : continue
        mg = obj.GetMg()
        mg.off-=origine
        obj.SetMg(mg)

    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()