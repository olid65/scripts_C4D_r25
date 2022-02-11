import c4d
import json
import urllib.request, urllib.error, urllib.parse
from  random import random

import sys

#ATTENTION A MODIFIER POUR PLUGIN **********************************
sys.path.append('/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/plugins/SITG_C4D/libs')

from importArbresShapePoint import create_mograph_cloner

ARBRES_SOURCES = doc.SearchObject('sources_vegetation')


CONTAINER_ORIGIN = 1026473

ID_LYR_ARBRES_ISOLES = 0
ID_LYR_COUV_SOL = 1

NAMES_MNT = ['MNT','swissalti3d']

RAPORT_HAUTEUR_DIAMETRE_MIN = 0.3

ESRI_GEOM = ['esriGeometryPoint',
             'esriGeometryMultipoint',
             'esriGeometryPolyline',
             'esriGeometryPolygon',
            ]

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True
DELTA_ALT = 100

def spline2json(sp,origine):
    """pour géométrie JSON à mettre sous geometry de la requête
       et indiquer sous geometryType=esriGeometryPolygon"""       
    res = {}    
    res["spatialReference"] = {"wkid" : 2056}
    mg = sp.GetMg()    
    sp = sp.GetRealSpline()
    if not sp: return None   
    pts = [p*mg+origine for p in sp.GetAllPoints()]

    nb_seg = sp.GetSegmentCount()
    if not nb_seg:
        res["rings"] = [[[p.x,p.z] for p in pts]]
    
    else:
        res["rings"] = []
        id_pt = 0
        for i in range(nb_seg):
            cnt = sp.GetSegment(i)['cnt']
            res["rings"].append([[p.x,p.z] for p in pts[id_pt:id_pt+cnt]])
            id_pt+=cnt
    return json.dumps(res)

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    #return mini, maxi, largeur, hauteur
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

def getMinMaxY(obj):
    """renvoie le minY et le maxY en valeur du monde d'un objet"""
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT

def pointsOnSurface(op,mnt):
    mg_op = op.GetMg()
    op = op.GetClone()
    op.SetMg(mg_op)
    grc = c4d.utils.GeRayCollider()
    grc.Init(mnt)


    mg_mnt = mnt.GetMg()
    invmg_mnt = ~mg_mnt
    invmg_op = ~op.GetMg()

    minY,maxY = getMinMaxY(mnt)

    ray_dir = ((c4d.Vector(0,0,0)*invmg_mnt) - (c4d.Vector(0,1,0)*invmg_mnt)).GetNormalized()
    length = maxY-minY
    for i,p in enumerate(op.GetAllPoints()):
        p = p*mg_op
        dprt = c4d.Vector(p.x,maxY,p.z)*invmg_mnt
        intersect = grc.Intersect(dprt,ray_dir,length)
        if intersect :
            pos = grc.GetNearestIntersection()['hitpos']
            op.SetPoint(i,pos*mg_mnt*invmg_op)

    op.Message(c4d.MSG_UPDATE)
    return op



def get_json_from_url(url):
    req = urllib.request.Request(url=url)
    try :
        resp = urllib.request.urlopen(req)

    except urllib.error.HTTPError as e:
        print(f'HTTPError: {e.code}')
        return None

    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        # ...
        print(f'URLError: {e.reason}')
        return None

    else:
        # 200
        data = json.loads(resp.read().decode("utf-8"))
        return data

    return None

def createSpline(pts,segments, name):
    pcnt = len(pts)
    sp = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    sp[c4d.SPLINEOBJECT_CLOSED] = True
    sp.SetAllPoints(pts)
    sp.SetName(name)

    #ajout des segments s'il y en a plus que 1
    if len(segments)>1:
        sp.ResizeObject(pcnt, len(segments))
        for i,cnt in enumerate(segments):
            sp.SetSegment(i,cnt,closed = True)
    sp.Message(c4d.MSG_UPDATE)
    return sp

def getMNT(doc, obj):
    while obj:
        for name in NAMES_MNT:
            if name in obj.GetName():
                return obj
            res = getMNT(doc, obj.GetDown())
            if res : return res
        obj = obj.GetNext()
    return None


# Main function
def main():
    
    origine = doc[CONTAINER_ORIGIN]

    if not origine:
        print("pas d'origine")
        return
    
    #EXEMPLE DEPUIS UNE SPLINE SELECTIONNEE
    url_base = 'https://hepiadata.hesge.ch/arcgis/rest/services/suisse/TLM_C4D_couverture_sol/FeatureServer/'
    lyr_arbres_isoles = f'/{ID_LYR_ARBRES_ISOLES}/query?'
    if op and op.GetRealSpline():
        poly_json = spline2json(op,origine)
        if poly_json:
            params = { 
                        "geometry": poly_json,
                        "geometryType": "esriGeometryPolygon", 
                        "returnGeometry":"true",
                        "returnZ": "true",
                        "spatialRel":"esriSpatialRelIntersects",
                        "f":"json"
                    }    
                     
            query_string = urllib.parse.urlencode( params ) 
            url_arbres_isoles = url_base+ lyr_arbres_isoles + query_string
            print(url_arbres_isoles)
            data = get_json_from_url(url_arbres_isoles)
            print(data.get('geometryType','prout'))
    else:
        print("Pas de poly_json, est-ce qu'une spline a biem été sélectionnée")
    return

    #EXEMPLE DEPUIS ENVELOPPE (Bbox : xmin,ymin,xmax,ymax)
    xmin,ymin,xmax,ymax = 0,0,0,0

    if op:
        if op.CheckType(c4d.Opolygon):
            xmin,ymin,xmax,ymax = empriseObject(op, origine)
        else:
            xmin,ymin,xmax,ymax = empriseObject(op.GetCache(), origine)

    if not xmin:
        print("pas d'objet sélectionné")
        return


    #xmin,ymin,xmax,ymax = 2566869.6511530234,1106946.5383559298,2568339.9402697803,1108134.5440385668

    url_base = 'https://hepiadata.hesge.ch/arcgis/rest/services/suisse/TLM_C4D_couverture_sol/FeatureServer'

    #arbres isoles
    lyr_arbres_isoles = f'/{ID_LYR_ARBRES_ISOLES}/'
    query = f'query?geometry={xmin},{ymin},{xmax},{ymax}&returnZ=true&geometryType=esriGeometryEnvelope&f=json'

    url_arbres_isoles = url_base+lyr_arbres_isoles+query
    


    data = get_json_from_url(url_arbres_isoles)

    pts = []
    for feat in data['features']:
        geom = feat['geometry']

        pts.append(c4d.Vector(geom['x'],geom['z'],geom['y'])-origine)

    arbres_pts_sommet = c4d.PolygonObject(len(pts),0)
    arbres_pts_sommet.SetName('arbres_isoles_swisstopo_sommets')
    arbres_pts_sommet.SetAllPoints(pts)
    arbres_pts_sommet.Message(c4d.MSG_UPDATE)
    doc.InsertObject(arbres_pts_sommet)

    ######################################
    #projection des points sur le MNT
    #######################################
    mnt = getMNT(doc, doc.GetFirstObject())

    hauteurs = []
    diametres = []

    if mnt and mnt.CheckType(c4d.Opolygon):
        arbres_pts_base = pointsOnSurface(arbres_pts_sommet,mnt)
        arbres_pts_base.SetName('arbres_isoles_swisstopo_collets')
        doc.InsertObject(arbres_pts_base)

        #TODO : que faire quand la hauteur == 0
        hauteurs = [pt_sommet.y-pt_base.y for pt_sommet,pt_base in zip(arbres_pts_sommet.GetAllPoints(),arbres_pts_base.GetAllPoints())]

        rapport = RAPORT_HAUTEUR_DIAMETRE_MIN + random()*RAPORT_HAUTEUR_DIAMETRE_MIN
        diametres = [haut*rapport for haut in hauteurs]
        
        if not ARBRES_SOURCES:
            print('ATTENTION PAS D?ARBRES SOURCE')

        create_mograph_cloner(doc, arbres_pts_base.GetAllPoints(), hauteurs, diametres, ARBRES_SOURCES, centre=None, name=None)

    #couverture du sol

    #catégories dans le champ OBJEKTART que l'on récupère'
    categories ={'Gebueschwald':'Forêt buissonnante',
                 'Wald':'Forêt',
                 'Wald%20offen': 'Forêt claisemée',
                 'Gehoelzflaeche':'Zone boisée',
                 }

    #categories ={'Wald':'Forêt',
                 #'Wald offen': 'Forêt claisemée',}

    lyr_couv_sol = f'/{ID_LYR_COUV_SOL}/'

    res = c4d.BaseObject(c4d.Onull)
    res.SetName('couverture_sol')

    sql = ''

    for i,cat in enumerate(categories.keys()):

        if i>0 :
            sql+=' OR '

        sql+=f"OBJEKTART='{cat}'"

    #urllib.parse.quote sert à remplacer les caractère spéciaux par le code ascii
    #on doit passer par ça notamment pour les espaces !
    print(sql)
    sql= urllib.parse.quote(sql)


    query = f"query?geometry={xmin},{ymin},{xmax},{ymax}&returnZ=true&outFields=OBJEKTART&orderByFields=OBJEKTART&where={sql}&geometryType=esriGeometryEnvelope&f=json"

    url_couv_sol = url_base+lyr_couv_sol+query

    #url_couv_sol = urllib.parse.urlencode(url_couv_sol, quote_via=urllib.parse.quote)

    print(url_couv_sol)


    data = get_json_from_url(url_couv_sol)
    if not data:
        print('pas de data')
        return

    #stockage du nombre de points par segement
    segments = []
    pts = []
    cat = None

    for feat in data['features']:
        if not cat :
            cat = feat['attributes']['objektart']

        #vu que lq requête trie par OBJEKTART
        #si la catégorie change on crée la spline
        #et on efface les listes
        if cat!= feat['attributes']['objektart']:
            sp = createSpline(pts,segments, name = categories[cat])
            sp.InsertUnderLast(res)

            #on vide les listes
            pts.clear()
            segments.clear()
            cat = feat['attributes']['objektart']

        geom = feat['geometry']
        for ring in geom['rings']:
            for i,(x,y,z) in enumerate(ring):
                #ATTENTION JE N'AI PAS UTILISE LE Z POUR POUVOIR DECOUPER LES SPLINES ENSUITE
                pts.append(c4d.Vector(x,0,y)-origine)
            segments.append(i+1)

    sp = createSpline(pts,segments,name = categories[cat])
    sp.InsertUnderLast(res)

    doc.InsertObject(res)
    c4d.EventAdd()
    return

    pcnt = len(pts)
    if pcnt:
        sp = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
        sp[c4d.SPLINEOBJECT_CLOSED] = True
        sp.SetAllPoints(pts)
        sp.SetName(categories[cat])

        #ajout des segements s'il y en a plus que 1
        if len(segments)>1:
            sp.ResizeObject(pcnt, len(segments))
            for i,cnt in enumerate(segments):
                sp.SetSegment(i,cnt,closed = True)
        sp.Message(c4d.MSG_UPDATE)
        sp.InsertUnderLast(res)
    doc.InsertObject(res)
    c4d.EventAdd()

    return



# Execute main()
if __name__=='__main__':
    main()