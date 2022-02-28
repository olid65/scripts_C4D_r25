import c4d
from math import pi


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

PRECISION = 0.001

# Main function
def main():
    #on regarde s'il y a 4 points'
    if op.GetPointCount()!= 4:
        return False

    pts = [p*op.GetMg() for p in op.GetAllPoints()]

    #attention un objet plan a les points qui ne tourne pas logiquement
    #il faut prendre le polygone pour avoir le bon sens
    poly = op.GetPolygon(0)

    #on vérifie qu'il y a bien des angles droit
    v1 = pts[poly.b]-pts[poly.a]
    v2 = pts[poly.c]-pts[poly.b]
    v3 = pts[poly.d]-pts[poly.c]
    v4 = pts[poly.a]-pts[poly.d]

    height = v1.GetLength()
    width = v2.GetLength()

    if abs(c4d.utils.GetAngle(v2,v1) - pi/2) > PRECISION : return False
    if abs(c4d.utils.GetAngle(v3,v2) - pi/2) > PRECISION  : return False
    if abs(c4d.utils.GetAngle(v4,v3) - pi/2) > PRECISION  : return False
    if abs(c4d.utils.GetAngle(v1,v4) - pi/2) > PRECISION  : return False

    #calcul du centre
    lst_x = [p.x for p in pts]
    lst_y = [p.y for p in pts]
    lst_z = [p.z for p in pts]

    x = (max(lst_x)+min(lst_x))/2
    y = (max(lst_y)+min(lst_y))/2
    z = (max(lst_z)+min(lst_z))/2
    off = c4d.Vector(x,y,z)

    v3 = v1.GetNormalized()
    v1 = v2.GetNormalized()
    v2 = v1.Cross( v3)

    plane = c4d.BaseObject(c4d.Oplane)
    plane.SetMg(c4d.Matrix(off,v1,v2,v3))

    plane[c4d.PRIM_PLANE_WIDTH] = width
    plane[c4d.PRIM_PLANE_HEIGHT] = height

    doc.InsertObject(plane, pred = op)
    c4d.EventAdd()

    return
    for p1,p2 in zip([p1,p2,p3,p4],[p2,p3,p4,p1]):
        v = p2-p1

        if v.x !=0 and v.z !=0:
            return False
    return True

# Execute main()
if __name__=='__main__':
    main()