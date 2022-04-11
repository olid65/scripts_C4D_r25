import c4d
import os.path

import sys

sys.path.append('/Users/olivierdonze/opt/anaconda3/lib/python3.8/site-packages')
from geojson import Point, MultiPoint, Polygon, MultiPolygon, LineString, MultiLineString, Feature, FeatureCollection, load


CONTAINER_ORIGIN = 1026473



# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def lst2vec(lst):
    """transformation tuple ou liste coord x,y(z) en vecteur Cinema4D"""
    if len(lst) ==2:
        x,z = lst
        return c4d.Vector(x,0,z)
    elif len(lst) ==3:
        x,z,y = lst
        return c4d.Vector(x,y,z)

def get_centre(pts):
    lst_x = [v.x for v in pts]
    lst_y = [v.y for v in pts]
    lst_z = [v.z for v in pts]
    return c4d.Vector((min(lst_x)+max(lst_x))/2, (min(lst_y)+max(lst_y))/2,(min(lst_z)+max(lst_z))/2)

def point(coord):
    pass

def multipoint(coord):
    pass

def polygon(coord):
    pts = []
    seg = []
    for lst in coord:
        #on supprime le dernier point car c'est le même que le premier
        pts_temp = [lst2vec(l) for l in lst][:-1]
        #stockage du nombre de points par segment
        seg.append(len(pts_temp))
        pts+=pts_temp

    #on calcule le centre des points
    # et on translate tous les points
    centre = get_centre(pts)
    pts = list(map(lambda v: v-centre, pts))
    pcnt = len(pts)
    scnt = len(seg)
    res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    res[c4d.SPLINEOBJECT_CLOSED] = True
    res.SetAllPoints(pts)
    res.SetAbsPos(centre)
    if scnt > 1:
        res.ResizeObject( pcnt, scnt=scnt)
        for i,cnt in enumerate(seg):
            res.SetSegment(i, cnt, closed=True)
    res.Message(c4d.MSG_UPDATE)

    return res

def multipolygon(coord):
    pts = []
    seg = []
    for poly in coord:
        for lst in poly:
            #on supprime le dernier point car c'est le même que le premier
            pts_temp = [lst2vec(l) for l in lst][:-1]
            #stockage du nombre de points par segment
            seg.append(len(pts_temp))
            pts+=pts_temp

    #on calcule le centre des points
    # et on translate tous les points
    centre = get_centre(pts)
    pts = list(map(lambda v: v-centre, pts))
    pcnt = len(pts)
    scnt = len(seg)
    res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    res[c4d.SPLINEOBJECT_CLOSED] = True
    res.SetAllPoints(pts)
    res.SetAbsPos(centre)
    if scnt > 1:
        res.ResizeObject( pcnt, scnt=scnt)
        for i,cnt in enumerate(seg):
            res.SetSegment(i, cnt, closed=True)
    res.Message(c4d.MSG_UPDATE)

    return res

def linestring(coord):
    pts = [lst2vec(p) for p in coord]


    #on calcule le centre des points
    # et on translate tous les points
    centre = get_centre(pts)
    pts = list(map(lambda v: v-centre, pts))
    pcnt = len(pts)
    #scnt = len(seg)
    res = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    res[c4d.SPLINEOBJECT_CLOSED] = False
    res.SetAllPoints(pts)
    res.SetAbsPos(centre)
    res.Message(c4d.MSG_UPDATE)

    return res

def multilinestring(coord):
    pass

dico_func = {
                'Point': point,
                'MultiPoint': multipoint,
                'Polygon': polygon,
                'MultiPolygon': multipolygon,
                'LineString': linestring,
                'MultiLineString':multilinestring,
}

# Main function
def main():
    fn = '/Users/olivierdonze/Documents/TEMP/geojson/export_splines.geojson'
    fn = '/Users/olivierdonze/Documents/TEMP/Martigny_Combe/mnt_esri_test_courbes_poly_5m.geojson'
    fn = c4d.storage.LoadDialog()
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    origine = doc[CONTAINER_ORIGIN]

    with open(fn) as f:
        data = load(f)

        features = data.get('features',None)
        if not features:
            c4d.gui.MessageDialog(f"Pas de features dans le fichier {os.path.basename(fn)}")
            return

        for feature in features:
            geom = feature.get('geometry',None)

            #appelle de la fonction selon le type
            obj = dico_func[geom.get('type',None)](geom['coordinates'])
            pos = obj.GetAbsPos()
            if not origine:
                doc[CONTAINER_ORIGIN] = c4d.Vector(pos)
                origine = doc[CONTAINER_ORIGIN]
            pos-= origine


            #attributs
            attr = feature['properties']
            if attr.get('name',None):
                obj.SetName(attr['name'])

            if attr.get('ELEV_MAX',None):
                obj.SetName(attr['ELEV_MAX'])


            obj.SetAbsPos(pos)
            obj.InsertUnderLast(res)

    doc.InsertObject(res)
    c4d.EventAdd()


# Execute main()
if __name__=='__main__':
    main()