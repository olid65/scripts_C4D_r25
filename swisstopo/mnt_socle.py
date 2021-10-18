import c4d

EPAISSEUR = 20 #épaisseur du socle depuis le points minimum

def selectEdgesContour(op):

    nb = c4d.utils.Neighbor(op)
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


def main():
    mg = op.GetMg()
    alts = [(p*mg).y for p in op.GetAllPoints()]
    alt_min = min(alts) - EPAISSEUR

    doc.StartUndo()
    
    #tag de selelction de polygone
    tag_sel_terrain = c4d.SelectionTag(c4d.Tpolygonselection)
    bs = tag_sel_terrain.GetBaseSelect()
    bs.SelectAll(op.GetPolygonCount())
    tag_sel_terrain[c4d.ID_BASELIST_NAME] = 'mnt'
    
    op.InsertTag(tag_sel_terrain)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,tag_sel_terrain)

    doc.AddUndo(c4d.UNDOTYPE_CHANGE,op)
    #Sélection des arrêtes du contour
    selectEdgesContour(op)
    #Extrusion à zéro
    settings = c4d.BaseContainer()                 # Settings
    settings[c4d.MDATA_EXTRUDE_OFFSET] = 0      # Length of the extrusion
    
    res = c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_EXTRUDE_TOOL,
                                    list = [op],
                                    mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                    bc = settings,
                                    doc = doc)
                                    
                                    
    #Valeurs commune des points                                
    
    settings = c4d.BaseContainer()                 # Settings
    settings[c4d.MDATA_SETVALUE_SETY] = c4d.MDATA_SETVALUE_SET_SET  
    settings[c4d.MDATA_SETVALUE_VAL] = c4d.Vector(0,alt_min,0)
    #settings[c4d.TEMP_MDATA_SETVALUE_VAL_Y] = -2000
    settings[c4d.MDATA_SETVALUE_SYSTEM] = c4d.MDATA_SETVALUE_SYSTEM_WORLD
    
    res = c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_SETVALUE_TOOL,
                                    list = [op],
                                    mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                    bc = settings,
                                    doc = doc)
    doc.EndUndo()
    c4d.EventAdd()


if __name__=='__main__':
    main()
