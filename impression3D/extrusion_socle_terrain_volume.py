import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE,op)
    nb_pts = op.GetPointCount()
    
    #extrusion   
    settings = c4d.BaseContainer()  # Settings
    
    settings[c4d.MDATA_EXTRUDE_OFFSET] = 0.0  # Length of the extrusion
    settings[c4d.MDATA_EXTRUDE_VARIANCE] = 0
    settings[c4d.MDATA_EXTRUDE_SUBDIVISION] = 0
    settings[c4d.MDATA_EXTRUDE_CREATECAPS] = True
    settings[c4d.MDATA_EXTRUDE_ANGLE] = 3.15/2
    settings[c4d.MDATA_EXTRUDE_PRESERVEGROUPS] = True
    
    
    
    res = c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_EXTRUDE_TOOL,    
                                    list=[op],    
                                    mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,  
                                    bc=settings,
                                    doc=doc)

    #on remet les premier points à l'altitude du socle
    alt_base_socle = 0
    for i in range(nb_pts):
        p = op.GetPoint(i)
        p.y = alt_base_socle
        op.SetPoint(i,p)
    
    op.Message(c4d.MSG_UPDATE)
    
    doc.EndUndo()
    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()