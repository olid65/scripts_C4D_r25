import c4d
import shapefile as shp
import os.path
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    fn = '/Users/olivierdonze/Documents/TEMP/swissbuildings3_tests/ogr/swissbuildings_3_Building_solid.shp'
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    r = shp.Reader(fn)
    
    xmin,ymin,xmax,ymax = r.bbox
    centre = c4d.Vector((xmin+xmax)/2,0,(ymax+ymin)/2)
    
    # géométries
    shapes = r.shapes()
    
    nbre = 0
    for shape in shapes:
        pts = [c4d.Vector(x,z,y)-centre for (x,y),z in zip(shape.points,shape.z)]
        nb_pts = len(pts)
        polys = []
        
        pred = 0
        for i in shape.parts:
            if pred:
                nb_pts_poly = i-pred
                print(nb_pts_poly)
                return
            
            poly = c4d.CPolygon(i,i+1,i+2,i+3)
            polys.append(poly)
            pred = i
            
        
        po =c4d.PolygonObject(nb_pts,len(polys))
        #TODO : tag phong !
        po.SetAllPoints(pts)
        for i,poly in enumerate(polys):
            po.SetPolygon(i,poly)

        po.Message(c4d.MSG_UPDATE)
        po.InsertUnderLast(res)
    
    doc.InsertObject(res)
    c4d.EventAdd()
    return
    
    
# Execute main()
if __name__=='__main__':
    main()