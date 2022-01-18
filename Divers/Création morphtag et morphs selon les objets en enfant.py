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
    
    morphTag = c4d.modules.character.CAPoseMorphTag()
    op.InsertTag(morphTag)
    morphTag[c4d.ID_CA_POSE_POINTS] = True
    
    for o in op.GetChildren():
        # create new morph  
        morph = morphTag.AddMorph()  
        print(morph)
        if morph is None:  
             return  
          
        morph.SetName(o.GetName())  
          
        # select latest morph  
        count = morphTag.GetMorphCount()  
        morphTag.SetActiveMorphIndex(count-1)  
          
        # set "Target"  
        morphTag[c4d.ID_CA_POSE_TARGET] = o  
      
    c4d.EventAdd()  

    


# Execute main()
if __name__=='__main__':
    main()