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

    mailleur = c4d.BaseObject(c4d.Ovolumemesher)
    vol_builder = c4d.BaseObject(c4d.Ovolumebuilder)
    vol_builder.InsertUnder(mailleur)
    #dans ce cas le nom correspond à l'alt
    alts = [float(o.GetName()) for o in op.GetChildren()]
    ymin = min(alts)
    ymax = max(alts)
    equidist = alts[1]-alts[0]

    #res = c4d.BaseObject(c4d.Onull)
    mailleur.SetMg(c4d.Matrix(op.GetMg()))
    for sp in op.GetChildren():
        alt = float(sp.GetName())
        clone_sp = sp.GetClone()
        extr = c4d.BaseObject(c4d.Oextrude)
        extr[c4d.EXTRUDEOBJECT_DIRECTION] = c4d.EXTRUDEOBJECT_DIRECTION_Y
        #
        extr[c4d.EXTRUDEOBJECT_EXTRUSIONOFFSET] = -(alt-ymin+equidist)

        extr.SetName(sp.GetName())
        clone_sp.InsertUnder(extr)
        extr.InsertUnderLast(vol_builder)


    doc.InsertObject(mailleur)
    c4d.EventAdd()



# Execute main()
if __name__=='__main__':
    main()