import c4d
from pprint import pprint

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def getAllLayers(lyr,res = {}):
    """fonction recursive qui renvoie un dico
       nom calque, liste de calques"""
    while lyr:
        res.setdefault(lyr.GetName(),[]).append(lyr)
        getAllLayers(lyr.GetDown(),res)
        lyr = lyr.GetNext()
    return res


def parseAllObjects(obj,doc,dico_lyr):
    while obj:
        lyr = obj.GetLayerObject(doc)
        if lyr:
            lst = dico_lyr[lyr.GetName()]
            if len(lst)>1:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE,obj)
                obj.SetLayerObject(lst[0])
        parseAllObjects(obj.GetDown(),doc,dico_lyr)
        obj = obj.GetNext()


# Main function
def main():
    
    doc.StartUndo()
    dico_lyr = getAllLayers(doc.GetLayerObjectRoot().GetDown())
    parseAllObjects(doc.GetFirstObject(),doc,dico_lyr)
    
    lst_lyr_to_remove = []
    for name,lst in dico_lyr.items():
        if len(lst)>1:
            for lyr in lst[1:]:
                lst_lyr_to_remove.append(lyr)
    for lyr in  lst_lyr_to_remove:
        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ,lyr)
        lyr.Remove()
        
    
    doc.EndUndo()
    c4d.EventAdd()
    return
    
    
    #
            
    return
    
    lyr = doc.GetLayerObjectRoot().GetDown()
    while lyr:
        print(lyr.GetName())
        lyr = lyr.GetNext()
        
    

# Execute main()
if __name__=='__main__':
    main()