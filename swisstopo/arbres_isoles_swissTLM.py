import c4d
import os
import shapefile

CONTAINER_ORIGIN = 1026473

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

NOM_MNT = 'swissalti3d_50cm'
NOM_MNT2 = 'swissalti3d_2m'


DELTA_ALT = 100

def getMinMaxY(obj):
    """renvoie le minY et le maxY en valeur du monde d'un objet"""
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT

def pointsOnSurface(op,mnt):
    grc = c4d.utils.GeRayCollider()
    grc.Init(mnt)

    mg_op = op.GetMg()
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

# Main function
def main():
    fn = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/meyrin_arbres.shp'

    mnt = doc.SearchObject(NOM_MNT)

    if not mnt :
        mnt = doc.SearchObject(NOM_MNT2)

    if not mnt :
        c4d.MessageDialog('Pas de MNT trouvé')
        return

    reader = shapefile.Reader(fn)
    #print(reader.shapeType)
    #print(reader.shapeType in [shapefile.POINTZ])

    xmin, ymin, xmax, ymax = reader.bbox
    centre = c4d.Vector((xmin + xmax) / 2, 0, (ymax + ymin) / 2)

    pts = []
    alts_sommet = []
    for shp in reader.iterShapes():
        #TODO appremment ce n'est pas optimal de rajouter les points comme ça
        #.append est plus rapide'
        pts+= [c4d.Vector(x, 0, y)-centre for x, y in shp.points]
        alts_sommet+= [z for z in shp.z]


    nb_pts = len(pts)
    pts_obj = c4d.PolygonObject(nb_pts,0)
    pts_obj.SetName(os.path.basename(fn)+'_pts')
    pts_obj.SetAllPoints(pts)
    pts_obj.Message(c4d.MSG_UPDATE)

    origin = doc[CONTAINER_ORIGIN]
    if not origin:
        doc[CONTAINER_ORIGIN] = centre
        origin = doc[CONTAINER_ORIGIN]

    pts_obj.SetAbsPos(centre-origin)
    # projection des points sur le mnt
    pointsOnSurface(pts_obj,mnt)
    
    #calcul des hauteurs d'arbres
    hauteurs = [(alt_sommet-pos_base.y)for alt_sommet,pos_base in zip(alts_sommet,pts_obj.GetAllPoints())]
    print(hauteurs)
        

    tag = c4d.VertexColorTag(nb_pts)
    tag[c4d.ID_VERTEXCOLOR_DRAWPOINTS] = True

    data = tag.GetDataAddressW()
    green = c4d.Vector4d(0.0, 1.0, 0.0, 1.0)
    for idx in range(nb_pts):
        c4d.VertexColorTag.SetPoint(data, None, None, idx, green)
    pts_obj.InsertTag(tag)


    doc.InsertObject(pts_obj)
    c4d.EventAdd()


# Execute main()
if __name__=='__main__':
    main()