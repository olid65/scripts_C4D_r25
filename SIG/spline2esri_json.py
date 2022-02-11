import c4d
from c4d import gui
# Welcome to the world of Python


CONTAINER_ORIGIN = 1026473

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

{
  "rings" : [[[-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832],
              [-97.06138,32.837]],[[-97.06326,32.759],[-97.06298,32.755],[-97.06153,32.749],
              [-97.06326,32.759]]],
  "spatialReference" : {"wkid" : 2056}
}

def spline2json(sp,origine):
    res = {}
    
    res["spatialReference"] = {"wkid" : 2056}
    mg = sp.GetMg()
    
    sp = sp.GetRealSpline()
    if not sp: return None
    
    pts = [p*mg+origine for p in sp.GetAllPoints()]

    nb_seg = sp.GetSegmentCount()
    if not nb_seg:
        res["rings"] = [[[p.x,p.z] for p in pts]]
    
    else:
        res["rings"] = []
        id_pt = 0
        for i in range(nb_seg):
            cnt = sp.GetSegment(i)['cnt']
            res["rings"].append([[p.x,p.z] for p in pts[id_pt:id_pt+cnt]])
            id_pt+=cnt
    print(res)

# Main function
def main():
    origine = doc[CONTAINER_ORIGIN]
    spline2json(op,origine)

# Execute main()
if __name__=='__main__':
    main()