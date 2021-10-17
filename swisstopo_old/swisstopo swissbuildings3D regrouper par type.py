import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

PREFIXE = 'SWISSBUILDINGS3D'

def connect(lst_obj,name,doc):
    nb_pts = 0
    nb_poly = 0
    
    for i,obj in enumerate(lst_obj):
        nb_pts+=obj.GetPointCount()
        nb_poly+=obj.GetPolygonCount()
        
    res = c4d.PolygonObject(nb_pts,nb_poly)
    res.SetName(name)
    id_pt_dprt=0
    id_poly_dprt =0
    
    for obj in lst_obj:
        mg = obj.GetMg()
        for i,pt in enumerate(obj.GetAllPoints()):
            res.SetPoint(i+id_pt_dprt,c4d.Vector(pt*mg))
        for i,poly in enumerate(obj.GetAllPolygons()):
            poly.a += id_pt_dprt
            poly.b += id_pt_dprt
            poly.c += id_pt_dprt
            poly.d += id_pt_dprt
            
            res.SetPolygon(i+id_poly_dprt,poly)
        id_pt_dprt+=obj.GetPointCount()
        id_poly_dprt += obj.GetPolygonCount()    

    res.Message(c4d.MSG_UPDATE)
    
    return res

# Main function
def main():
    nb_car_prefixe = len(PREFIXE)
    
    dic = {}
    
    for nobj in doc.GetActiveObjects(0):
        name = nobj.GetName()
        if len(name)<nb_car_prefixe or name[:nb_car_prefixe] != PREFIXE:
            continue
        
        for ssobj in nobj.GetChildren():
            lst = [o for o in ssobj.GetChildren() if o.CheckType(c4d.Opolygon)]
            if lst :
                dic.setdefault(ssobj.GetName(),[]).extend(lst)   
    
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(PREFIXE+'_connect_par_type')
    for k,lst in dic.items():
        poly_obj = connect(lst,k,doc)
        poly_obj.InsertUnder(res)
    
    doc.InsertObject(res)
    c4d.EventAdd()
            

# Execute main()
if __name__=='__main__':
    main()