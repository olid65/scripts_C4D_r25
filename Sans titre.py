import c4d
from pprint import pprint
import sys
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def groupByLayer(lst_obj, doc,parent = None):
    #dic = {obj.GetLayerObject(doc).GetName():value for obj in lst_obj if obj.GetLayerObject(doc)}
    dic = {}
    for obj in lst_obj:
        lyr = obj.GetLayerObject(doc)
        if lyr:
            dic.setdefault(lyr.GetName(),[]).append(obj)
    pred = None
    for name,lst in sorted(dic.items()):
        nullo = c4d.BaseObject(c4d.Onull)
        nullo.SetName(name)
        for o in lst:
            o.InsertUnder(nullo)
        doc.InsertObject(nullo,parent = parent, pred = pred)
        pred = nullo

# Main function
def main():
    groupByLayer(op.GetChildren(), doc,parent = op)
    c4d.EventAdd()
# Execute main()
if __name__=='__main__':
    main()