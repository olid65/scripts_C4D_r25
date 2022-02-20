import c4d
import os.path

import sys

sys.path.append('/Users/olivierdonze/opt/anaconda3/lib/python3.8/site-packages')
from geojson import Polygon, LineString, MultiLineString, Feature, FeatureCollection, dump


CONTAINER_ORIGIN = 1026473


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def spline2geojson_polygon(sp,origine = c4d.Vector(0)):
    mg = sp.GetMg()

    pts = [c4d.Vector(p)*mg+origine for p in sp.GetAllPoints()]
    pts = [(p.x,p.z) for p in pts]

    #mono segment
    if not sp.GetSegmentCount():
        #attention il faut que le dernier point corresponde au premier !
        pts.append(pts[0])
        poly = Polygon([pts])

    #multi segments
    else:
        pts_seg = []
        id_pt = 0
        for i in range(sp.GetSegmentCount()):
            cnt = sp.GetSegment(i)['cnt']
            #lst_pts = []
            lst_pts = pts[id_pt:id_pt+cnt]
            #attention il faut que le dernier point du segment corresponde au premier !
            lst_pts.append(lst_pts[0])
            pts_seg.append(lst_pts)
            id_pt+=cnt
        poly = Polygon(pts_seg)
    return poly

def spline2geojson_polyline(sp,origine = c4d.Vector(0)):
    mg = sp.GetMg()

    pts = [c4d.Vector(p)*mg+origine for p in sp.GetAllPoints()]
    pts = [(p.x,p.z) for p in pts]

    #mono segment -> LineString
    if not sp.GetSegmentCount():
        poly = LineString(pts)

    #multi segments  -> MultiLineString
    else:
        pts_seg = []
        id_pt = 0
        for i in range(sp.GetSegmentCount()):
            cnt = sp.GetSegment(i)['cnt']
            #lst_pts = []
            lst_pts = pts[id_pt:id_pt+cnt]
            pts_seg.append(lst_pts)
            id_pt+=cnt
        poly = MultiLineString(pts_seg)
    return poly

#################################################################################
# MAIN
#################################################################################

def splines2geojson(lst_splines, fn_dst, origine = c4d.Vector(0),epsg = 2056):
    """ Génére un fichier geojson depuis une liste de splines,
        Si les splines sont fermées -> polygones
        sinon -> polylignes"""
    features = []
    for i,sp in enumerate(lst_splines):
        if sp[c4d.SPLINEOBJECT_CLOSED]:
            poly = spline2geojson_polygon(sp.GetRealSpline(),origine = origine)
        else:
            poly = spline2geojson_polyline(sp.GetRealSpline(),origine = origine)

        #print(poly.is_valid)
        #print(poly.errors())
        features.append(Feature(geometry=poly, properties={"id": i+1, "name": f"{sp.GetName()}"}))
    crs = {
              "type": "name",
              "properties": {
                  "name": f"EPSG:{epsg}"
              }
            }

    feature_collection = FeatureCollection(features, crs=crs)

    with open(fn_dst, 'w') as f:
       dump(feature_collection, f, indent = 4)

    if os.path.isfile(fn_dst):
        return True

    return False

# Main function
def main():
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        origine = c4d.Vector(0)
    fn_dst = '/Users/olivierdonze/Documents/TEMP/geojson/export_splines.geojson'
    lst_splines = [sp for sp in doc.GetActiveObjects(0) if sp.GetRealSpline()]
    if not lst_splines:
        c4d.gui.MessageDialog("Pas de spline sélectionnée")
        return
    splines2geojson(lst_splines, fn_dst, origine = origine,epsg = 2056)

# Execute main()
if __name__=='__main__':
    main()