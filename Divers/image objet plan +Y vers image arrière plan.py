import c4d
from math import pi

Pperspective =  0,
Pparallel		 =  1,
Pleft				 =  2
Pright			 =  3,
Pfront			 =  4,
Pback			   =  5,
Ptop				 =  6,
Pbottom			 =  7,
Pmilitary		 =  8,
Pfrog			   =  9,
Pbird				 = 10,
Pgentleman	 = 11,
Pisometric	 = 12,
Pdimetric    = 13,
Pspherical	 = 14,


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


def angle360(rad):
    rad = -(rad)
    if rad < 0:
        rad = 2*pi -abs(rad)
        print(rad)
    return rad % (2*pi)


# Main function
def main():
    plane = op
    
    if not plane.CheckType(c4d.Oplane):
        c4d.gui.MessageDialog("Ne fonctionne qu'avec une objet plan")
        return
    if not plane[c4d.PRIM_AXIS] == c4d.PRIM_AXIS_YP:
        c4d.gui.MessageDialog("Le plan n'est pas en orientation +Y")
        return


    tag = op.GetTag(c4d.Ttexture)
    
    if not tag :
        c4d.gui.MessageDialog("Il n'y a pas de propriété matériau sur l'objet sélectionné")
        return
    mat = tag[c4d.TEXTURETAG_MATERIAL]
    
    shd = mat[c4d.MATERIAL_COLOR_SHADER]
    #TODO rechercher tous les shader image ??
    fn_img = None
    if shd:
        if shd.CheckType(c4d.Xbitmap):
            fn_img = shd[c4d.BITMAPSHADER_FILENAME]
            
    if not fn_img:
        c4d.gui.MessageDialog("Pas d'image dans le canal couleur")
        return
    
    
    bd = doc.GetActiveBaseDraw()
    if bd.HasCameraLink():
        cam = bd.GetSceneCamera(doc)
    else:
        cam = bd.GetEditorCamera()

    if cam.GetProjection() == c4d.Ptop:
        bd[c4d.BASEDRAW_DATA_PICTURE] = fn_img
        bd[c4d.BASEDRAW_DATA_SIZEX] = plane[c4d.PRIM_PLANE_WIDTH]
        bd[c4d.BASEDRAW_DATA_SIZEY] = plane[c4d.PRIM_PLANE_HEIGHT]
        pos = plane.GetAbsPos()
        
        bd[c4d.BASEDRAW_DATA_OFFSETX] = pos.x
        bd[c4d.BASEDRAW_DATA_OFFSETY] = pos.z
        
        rotation = angle360(plane.GetAbsRot().x)
        print(c4d.utils.RadToDeg(rotation))
        
        bd[c4d.BASEDRAW_DATA_PICTURE_ROTATION] = rotation
        
    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()