import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


def socleFromSpline(sp, offset,flat = False):
    
    # The real spline representation.
    sp = sp.GetRealSpline()
    mg = c4d.Matrix(sp.GetMg())
    
    if not sp:
        return None

    nb_pts = sp.GetPointCount()
    nb_segments = sp.GetSegmentCount()

    #quand il y a un seul segment GetSegmentCount() renvoie 0
    if not nb_segments : nb_segments =1


    if sp[c4d.SPLINEOBJECT_CLOSED]:
        nb_polygons = nb_pts

    else:
        nb_polygons = nb_pts-nb_segments

    print(nb_polygons)
    res = c4d.PolygonObject(nb_pts * 2, nb_polygons)

    if flat:
        alt_base = min([p.y for p in sp.GetAllPoints()])
        pts = [c4d.Vector(p) for p in sp.GetAllPoints()]
        pts+= [c4d.Vector(p.x,alt_base,p.z) for p in sp.GetAllPoints()]

    else:
        pts = [c4d.Vector(p) for p in sp.GetAllPoints()]
        pts+= [c4d.Vector(p.x,p.y-offset,p.z) for p in sp.GetAllPoints()]

    res.SetAllPoints(pts)

    id_pt = 0
    id_poly = 0
    for id_seg in range(nb_segments):
        if nb_segments ==1:
            cnt = nb_pts
        else:
            cnt = sp.GetSegment(id_seg)['cnt']
        print('----->',cnt)
        for i in range(cnt-1):
            a = id_pt+i
            b = a+1
            c = b+nb_pts
            d = c-1
            poly = c4d.CPolygon(b,a,d,c)
            print(a,b,c,d)
            res.SetPolygon(id_poly,poly)
            id_poly+=1

        if sp[c4d.SPLINEOBJECT_CLOSED]:
            a = id_pt
            b = id_pt+i+1
            c = b+nb_pts
            d = a+nb_pts
            print(a,b,c,d)
            poly = c4d.CPolygon(b,a,d,c)
            res.SetPolygon(id_poly,poly)
            id_poly+=1

        id_pt+=i+2


    res.SetMg(mg)

    res.Message(c4d.MSG_UPDATE)
    return res



# Main function
def main():
    sp = op
    offset = 100
    poly = socleFromSpline(sp, offset,flat = False)
    if poly:
        doc.InsertObject(poly)
        c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()