import c4d
import os.path
import subprocess

import sys

sys.path.append('/Users/olivierdonze/opt/anaconda3/lib/python3.8/site-packages')
from geojson import Polygon, Feature, FeatureCollection, dump


CONTAINER_ORIGIN = 1026473
# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

DIC_FORMATS = {
                'GeoJSON':'.geojson',
                'ESRI Shapefile':'.shp',
                'DXF':'.dxf',
                }
                
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

# Main function
def main():
    #sp = op
    path_ogr2ogr = '/Applications/QGIS.app/Contents/MacOS/bin/ogr2ogr'
    
    fn_src = '/Users/olivierdonze/Documents/TEMP/geojson/test2.geojson'
    
    format_res = 'GeoJSON'
    
    buffer_size = 20
    
    fn_res = os.path.splitext(fn_src)[0]+f'buffer{buffer_size}m{DIC_FORMATS[format_res]}'

    origine = doc[CONTAINER_ORIGIN]
    
    features = []
    for i,sp in enumerate(doc.GetActiveObjects(0)):
        poly = spline2geojson_polygon(sp.GetRealSpline(),origine = origine) 
        #poly = Polygon([
                        #[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.38, 57.322)],
                        #[(-5.21, 23.51), (15.21, -10.81), (-20.51, 1.51), (-5.21, 23.51)]
                        #])   
        #print(poly)
        #print(poly.is_valid)
        #print(poly.errors())
        features.append(Feature(geometry=poly, properties={"id": i}))
    crs = {
              "type": "name",
              "properties": {
                  "name": "EPSG:2056"
              }
            }
    
    feature_collection = FeatureCollection(features, crs=crs)
    
    with open(fn_src, 'w') as f:
       dump(feature_collection, f, indent = 4)

    nom,ext = os.path.splitext(fn_src)
    nom_src = os.path.basename(fn_src)[:-len(ext)]

    if os.path.isfile(fn_res):
        rep = c4d.gui.QuestionDialog(f"Le fichier {os.path.basename(fn_res)} existe déjà, il va être remplacé. Voulez-vous continuer ?")
        if not rep : return



    req = f'{path_ogr2ogr} "{fn_res}" "{fn_src}" -dialect sqlite -sql "SELECT ST_Buffer(geometry, {buffer_size}) AS geometry,* FROM """{nom_src}"""" -f "{format_res}"'
    output = subprocess.check_output(req,shell=True)
    print(output)

# Execute main()
if __name__=='__main__':
    main()