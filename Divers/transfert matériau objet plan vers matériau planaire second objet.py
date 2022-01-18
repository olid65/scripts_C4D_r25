import c4d
from math import pi


#Sélectionner d'abord l'objet plan puis l'objet sur lequel on veut mettre le matériau
#s'il n'y a pas déjà une propriété matériau avec ce matériau, crée la propriété
#ajuste selon le plan (si la propriété existe, la modifie)
#ne fonctionnne que pour les plans en vue de haut !



#TODO : il y a encore des soucis si l'objet source est en enfant d'un autre objet
#régler ces histoires de matrices de rotation pour l'instant c'est du bricolage!!!!!!
#voir ligne 93



# Main function
def main():
    try :
        plane, obj_dst = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    except:
        c4d.gui.MessageDialog("Vous devez sélectioner deux objets, l'objet plan avec le matériau, puis l'objet de destination")
        return
    if not plane.CheckType(c4d.Oplane):
        c4d.gui.MessageDialog("Le premier objet sélectionné doit être un objet plan")
        return
    if not plane[c4d.PRIM_AXIS] == c4d.PRIM_AXIS_YP:
        c4d.gui.MessageDialog("Le plan n'est pas en orientation +Y")
        return


    tag = plane.GetTag(c4d.Ttexture)

    if not tag :
        c4d.gui.MessageDialog("Il n'y a pas de propriété matériau sur l'objet sélectionné")
        return
    mat = tag[c4d.TEXTURETAG_MATERIAL]

    tag_dst = None

    #on regarde s'il y a déjà un tag matériau en mode planaire avec le matériau
    for t in obj_dst.GetTags():
        if t.CheckType(c4d.Ttexture) and \
            t[c4d.TEXTURETAG_MATERIAL] == mat and \
            t[c4d.TEXTURETAG_PROJECTION]== c4d.TEXTURETAG_PROJECTION_FLAT:
            tag_dst = t
    #sinon on crée un matériau
    if not tag_dst:
        tag_dst = c4d.BaseTag(c4d.Ttexture)
        tag_dst[c4d.TEXTURETAG_MATERIAL] = mat
        tag_dst[c4d.TEXTURETAG_PROJECTION]= c4d.TEXTURETAG_PROJECTION_FLAT
        pred = None
        if obj_dst.GetTags():
            pred = obj_dst.GetTags()[-1]
        obj_dst.InsertTag(tag_dst,pred)

    #réglage du tag
    
    ml = c4d.Matrix(plane.GetMg() *~obj_dst.GetUpMg()* ~obj_dst.GetMl())
    tag_dst.SetMl(ml)
    
    #tag_dst.SetRot(c4d.Vector())

    tag_dst[c4d.TEXTURETAG_TILE] = False
    tag_dst[c4d.TEXTURETAG_ROTATION,c4d.VECTOR_Y] = -pi/2


    tag_dst[c4d.TEXTURETAG_SIZE,c4d.VECTOR_X] = plane[c4d.PRIM_PLANE_WIDTH]/2
    tag_dst[c4d.TEXTURETAG_SIZE,c4d.VECTOR_Y] = plane[c4d.PRIM_PLANE_HEIGHT]/2

    #rot = plane.GetMg().v1 * ~obj_dst.GetMl()
    rotx = plane.GetAbsRot().x - obj_dst.GetAbsRot().x

    #tag_dst[c4d.TEXTURETAG_ROTATION,c4d.VECTOR_X] = ml.v1.x

    pos = plane.GetMg().off *~obj_dst.GetUpMg()* ~obj_dst.GetMl()
    tag_dst[c4d.TEXTURETAG_POSITION] = pos

    #tag_dst[c4d.TEXTURETAG_POSITION]

    c4d.EventAdd()

    return
# Execute main()
if __name__=='__main__':
    main()