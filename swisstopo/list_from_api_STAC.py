import c4d
import json
import urllib
from pprint import pprint

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

    return mini, maxi, largeur, hauteur

def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])


def get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax):
    #pour les bati3D il y a chaque fois toute la Suisse dans 2 gdb
    #pour les mnt on aussi du xyz
    # attention bien prendre les 8 derniers caractères
    lst_indesirables = ['.xyz.zip','.gdb.zip']
    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"

    url += sufixe_url
    f = urllib.request.urlopen(url)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    res = []
    dico = {}
    for item in json_res['features']:
        nom, an,no = item['id'].split('_')
        dico.setdefault(no,[]).append(an)
        for k,dic in item['assets'].items():
            href = dic['href']

            if href[-8:] not in lst_indesirables:
                res.append(dic['href'])

    pprint(dico)
    return res

LST = [  'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2565-1106/swissimage-dop10_2017_2565-1106_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2565-1106/swissimage-dop10_2017_2565-1106_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2565-1107/swissimage-dop10_2017_2565-1107_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2565-1107/swissimage-dop10_2017_2565-1107_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2566-1106/swissimage-dop10_2017_2566-1106_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2566-1106/swissimage-dop10_2017_2566-1106_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2566-1107/swissimage-dop10_2017_2566-1107_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2566-1107/swissimage-dop10_2017_2566-1107_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2567-1106/swissimage-dop10_2017_2567-1106_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2567-1106/swissimage-dop10_2017_2567-1106_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2567-1107/swissimage-dop10_2017_2567-1107_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2017_2567-1107/swissimage-dop10_2017_2567-1107_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2565-1106/swissimage-dop10_2020_2565-1106_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2565-1106/swissimage-dop10_2020_2565-1106_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2565-1107/swissimage-dop10_2020_2565-1107_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2565-1107/swissimage-dop10_2020_2565-1107_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2566-1106/swissimage-dop10_2020_2566-1106_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2566-1106/swissimage-dop10_2020_2566-1106_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2566-1107/swissimage-dop10_2020_2566-1107_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2566-1107/swissimage-dop10_2020_2566-1107_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2567-1106/swissimage-dop10_2020_2567-1106_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2567-1106/swissimage-dop10_2020_2567-1106_2_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2567-1107/swissimage-dop10_2020_2567-1107_0.1_2056.tif',
         'https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2567-1107/swissimage-dop10_2020_2567-1107_2_2056.tif']


def suppr_doublons_list_ortho(lst):
    """supprime les doublons de no de feuilles et garde uniquement la plus récente"""
    dic = {}
    for url in lst:
        #exemple url
        #https://data.geo.admin.ch/ch.swisstopo.swissimage-dop10/swissimage-dop10_2020_2567-1107/swissimage-dop10_2020_2567-1107_2_2056.tif
        #on extrait le dernier élément en splitant par /
        #on ne grade pas l'extension [:-4]
        # et on split par _ pour récupérer nom,an,noflle,taille_px,epsg
        nom,an,noflle,taille_px,epsg = url.split('/')[-1][:-4].split('_')
        dic.setdefault((noflle,float(taille_px)),[]).append((an,url))
    res = []
    for noflle,lst in dic.items():
        an, url = sorted(lst,reverse = True)[0]
        res.append(url)
    return res
    
# Main function
def main():
    
    #pprint(suppr_doublons_list_ortho(LST))

    origine = doc[CONTAINER_ORIGIN]
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)

    if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
        c4d.gui.MessageDialog("Activez une vue de haut")
        return True

    mini, maxi, larg, haut = empriseVueHaut(bd, origine)

    xmin,ymin,xmax,ymax = mini.x,mini.z,maxi.x,maxi.z

    url = 'https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissimage-dop10'
    lst = get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax)
    pprint(lst)


# Execute main(lst)
if __name__=='__main__':
    main()