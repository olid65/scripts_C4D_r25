import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


def decoupeSpline(sp1,sp2):
    splinemask = c4d.BaseObject(1019396 )#spline_mask    
    splinemask[c4d.MGSPLINEMASKOBJECT_MODE]=c4d.MGSPLINEMASKOBJECT_MODE_AND
    splinemask[c4d.MGSPLINEMASKOBJECT_AXIS] =c4d.MGSPLINEMASKOBJECT_AXIS_XZ
    splinemask[c4d.MGSPLINEMASKOBJECT_CREATECAP] = False
    
    sp1_clone = sp1.GetClone()
    sp1_clone.SetMg(c4d.Matrix(sp1.GetMg()))
    
    sp2_clone = sp2.GetClone()
    sp2_clone.SetMg(c4d.Matrix(sp2.GetMg()))
    
    sp2_clone.InsertUnder(splinemask)
    sp1_clone.InsertUnder(splinemask)
    
    doc_temp = c4d.documents.BaseDocument()
    doc_temp.InsertObject(splinemask)
    
    doc_poly = doc_temp.Polygonize()
    
    res = doc_poly.GetFirstObject()
    
    if res :
        res = res.GetClone() 
        res.SetMg(c4d.Matrix(res.GetMg()))
        
    c4d.documents.KillDocument(doc_poly)
    c4d.documents.KillDocument(doc_temp)
    return res   
    
    
    
    
    

# Main function
def main():
    
    sp1,sp2,*a = doc.GetActiveObjects(0)
    sp = decoupeSpline(sp1,sp2)
    if poly :
        doc.InsertObject(sp)
    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()