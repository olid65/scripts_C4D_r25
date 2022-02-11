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





# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True
DELTA_ALT = 100

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

    xmin,ymin,xmax,ymax = 0,0,0,0

    if op:
        if op.CheckType(c4d.Opoint):
            xmin,ymin,xmax,ymax = empriseObject(op, origine)
        else:
            xmin,ymin,xmax,ymax = empriseObject(op.GetCache(), origine)

    if not xmin:
        print("pas d'objet sélectionné")
        return
    
    #xmin,ymin,xmax,ymax = 2566869.6511530234,1106946.5383559298,2568339.9402697803,1108134.5440385668

    url_base = 'https://hepiageo2.hesge.ch/server/rest/services/geneve/bati3D/FeatureServer/4/query?'
    
    #'https://hepiageo2.hesge.ch/server/rest/services/geneve/bati3D/FeatureServer/4/query?where=&objectIds=&time=&geometry=2496288.0798143214%2C1121311.614405471%2C2496688.9497447824%2C1121547.8513968394&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&gdbVersion=&historicMoment=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=true&returnM=true&multipatchOption=xyFootprint&resultOffset=&resultRecordCount=&returnTrueCurves=false&returnExceededLimitFeatures=false&quantizationParameters=&returnCentroid=false&sqlFormat=none&resultType=&featureEncoding=esriDefault&datumTransformation=&f=pjson'
    #'quantizationParameters=&returnCentroid=false&sqlFormat=none&resultType=&featureEncoding=esriDefault&datumTransformation=&f=pjson''
    
    params = { 
        "where": "", 
        "objectIds": "", 
        "time": "",  
        "geometry": f"{xmin},{ymin},{xmax},{ymax}" ,
        "inSR": "",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": "", 
        "units": "esriSRUnit_Foot", 
        "relationParam": "",
        "outFields": "", 
        "returnGeometry": "true", 
        "maxAllowableOffset": "", 
        "geometryPrecision": "", 
        "outSR": "",
        "havingClause": "", 
        "gdbVersion": "", 
        "historicMoment": "", 
        "returnDistinctValues": "false", 
        "returnIdsOnly": "false", 
        "returnCountOnly": "false",
        "returnExtentOnly": "false",
        "orderByFields": "",
        "groupByFieldsForStatistics": "",
        "outStatistics": "",      
        "returnZ": "true" ,
        "returnM": "true",
        "multipatchOption": "xyFootprint",
        "resultOffset": "",
        "resultRecordCount": "", 
        "returnTrueCurves": "false", 
        "returnExceededLimitFeatures": "false", 
        "quantizationParameters": "", 
        "returnCentroid": "false", 
        "sqlFormat": "none", 
        "resultType": "",
        "featureEncoding": "esriDefault",
        "datumTransformation": "",
        "geometryType": "esriGeometryEnvelope" ,
        "f": "json" ,
    }    
     
    query_string = urllib.parse.urlencode( params )
    
    print(url_base + query_string)
    return



# Execute main()
if __name__=='__main__':
    main()