import c4d
from c4d import gui
#Welcome to the world of Python

def selectContour(op):

    nb = c4d.utils.Neighbor()
    nb.Init(op)
    bs = op.GetSelectedEdges(nb,c4d.EDGESELECTIONTYPE_SELECTION)
    bs.DeselectAll()
    for i,poly in enumerate(op.GetAllPolygons()):
        inf = nb.GetPolyInfo(i)
        if nb.GetNeighbor(poly.a, poly.b, i)==-1:
            bs.Select(inf['edge'][0])

        if nb.GetNeighbor(poly.b, poly.c, i)==-1: 
            bs.Select(inf['edge'][1])
            
        
        #si pas triangle
        if not poly.c == poly.d :
            if nb.GetNeighbor(poly.c, poly.d, i)==-1: 
                bs.Select(inf['edge'][2])
                
        if nb.GetNeighbor(poly.d, poly.a, i)==-1: 
            bs.Select(inf['edge'][3])        
        
    op.SetSelectedEdges(nb,bs,c4d.EDGESELECTIONTYPE_SELECTION)

def edge2spline(op):
    
    res = c4d.utils.SendModelingCommand(command = c4d.MCOMMAND_EDGE_TO_SPLINE,
                                    list = [op],
                                    mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                    doc = doc)
    return op.GetDown()


def main():
    selectContour(op)
    sp = edge2spline(op)
    doc.SetActiveObject(sp)
    c4d.EventAdd()

if __name__=='__main__':
    main()
