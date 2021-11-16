import c4d
import shapefile

CONTAINER_ORIGIN = 1026473

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    fn = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/arbres_vernayaz.shp'
    
    reader = shapefile.Reader(fn)
    print(reader.shapeType)
    print(reader.shapeType in [shapefile.POINTZ])
    
    xmin, ymin, xmax, ymax = reader.bbox
    centre = c4d.Vector((xmin + xmax) / 2, 0, (ymax + ymin) / 2)
    
    pts = []
    for shp in reader.iterShapes():
        pts+= [c4d.Vector(x, z, y)-centre for (x, y), z in zip(shp.points, shp.z)]
    
    pts_obj = c4d.PolygonObject(len(pts),0)
    pts_obj.SetAllPoints(pts)
    pts_obj.Message(c4d.MSG_UPDATE)
    
    origin = doc[CONTAINER_ORIGIN]
    if not origin:
        doc[CONTAINER_ORIGIN] = centre
        origin = doc[CONTAINER_ORIGIN]
    
    pts_obj.SetAbsPos(centre-origin)
    doc.InsertObject(pts_obj)
    c4d.EventAdd()
    

# Execute main()
if __name__=='__main__':
    main()