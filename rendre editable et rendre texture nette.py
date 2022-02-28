import c4d
from c4d import utils
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


def make_editable(op,doc):
    pred = op.GetPred()
    doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ,op)
    res = utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,
                            list=[op],
                            mode=c4d.MODELINGCOMMANDMODE_ALL,
                            bc=c4d.BaseContainer(),
                            doc=doc)
    
    if res:
        res = res[0]
        if res:
            doc.InsertObject(res, pred = pred)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,res)
            doc.SetActiveObject(res)
            return res
        
    return None

def get_last_texture_tag(op):
    tex_tags = [tag for tag in op.GetTags() if tag.CheckType(c4d.Ttexture)]    
    if tex_tags:
        return tex_tags[-1]    
    return None

def previewsize_last_tex_tag(op, doc, previewsize = c4d. MATERIAL_PREVIEWSIZE_NO_SCALE):
    tag = get_last_texture_tag(op)
    if tag:
        mat = tag[c4d.TEXTURETAG_MATERIAL]
        if mat :
            doc.AddUndo(c4d.UNDOTYPE_CHANGE_SMALL,mat)
            mat[c4d.MATERIAL_PREVIEWSIZE] = previewsize


# Main function
def main():
    doc.StartUndo()
    if not op.CheckType(c4d.Opolygon):
        polyo = make_editable(op,doc)
    else:
        polyo = op
    
    previewsize_last_tex_tag(polyo, doc)
    doc.EndUndo()
    c4d.EventAdd()
        
       
    

# Execute main()
if __name__=='__main__':
    main()