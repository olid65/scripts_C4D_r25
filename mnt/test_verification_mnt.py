import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def getSizeXZ(pts):
    x = [p.x for p in pts]
    z = [p.z for p in pts]
    
    return (round(max(x)-min(x),3), round(max(z)-min(z),3))

# Main function
def main():
    poly = op.GetPolygon(0)
    getPts = lambda poly : [op.GetPoint(poly.a),op.GetPoint(poly.b),op.GetPoint(poly.c),op.GetPoint(poly.d)]
    pts = getPts(poly)
    size = getSizeXZ(pts)
    errors =0
    for i in range(op.GetPolygonCount()):
        p =  op.GetPolygon(0)
        pts = getPts(poly)
        if getSizeXZ(pts)!= size: errors +=1
    
    if not errors :
        txt = "MNT ok"
    else :
        txt = f'Il y a {errors} polygones non conformes'
    
    c4d.gui.MessageDialog(txt)
    
# Execute main()
if __name__=='__main__':
    main()