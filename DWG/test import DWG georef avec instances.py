import c4d
import os
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

TXT_NOT_DWG = "Ce n'est pas un document dwg !"
TXT_PB_OPEN_DWG = "Problème à l'ouverture du fichier dwg !"

DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"

CONTAINER_ORIGIN =1026473

ALERT_SIZE_FN = 10 #taille pour alerter si un document est trop gros en Mo

#Emprise des coordonnées
CH_XMIN, CH_YMIN, CH_XMAX, CH_YMAX = 1988000.00, 87000.00, 2906900.00, 1421600.00


def scale_and_translation(o,scale_factor,doc):
    #suppression du tag matériau
    tag = o.GetTag(c4d.Ttexture)
    if tag :
        tag.Remove()
    mg = o.GetMg()
    pos = mg.off
    pos = pos*scale_factor
    if not doc[CONTAINER_ORIGIN]:
            doc[CONTAINER_ORIGIN] = c4d.Vector(pos.x,0,pos.z)
    if o.CheckType(c4d.Opoint):
            pts = [pt*mg*scale_factor -pos for pt in o.GetAllPoints()]
            o.SetAllPoints(pts)
            o.Message(c4d.MSG_UPDATE)
    mg_new = c4d.Matrix(off = pos-doc[CONTAINER_ORIGIN])
    o.SetMg(mg_new)
    return

def scale_and_translationOnHierarchy(obj,scale_factor,doc):
    while obj:
        scale_and_translation(obj,scale_factor,doc)
        scale_and_translationOnHierarchy(obj.GetDown(),scale_factor,doc)
        obj = obj.GetNext()

def getAllPoints(obj,stop,pts=[]):
    while obj:
        if obj.CheckType(c4d.Opoint):
            mg = obj.GetMg()
            pts.extend([p*mg for p in obj.GetAllPoints()])
        getAllPoints(obj.GetDown(),stop,pts)
        if obj ==stop :
            return pts
        obj = obj.GetNext()   
    return pts 

def getHierarchyCenter(obj_parent):
    pts = getAllPoints(obj_parent,obj_parent,pts=[])
    if not pts : return None
    xs = [p.x for p in pts]
    zs = [p.z for p in pts]
    xmin = min(xs)
    xmax = max(xs)
    zmin = min(zs)
    zmax = max(zs)
    centre = c4d.Vector((xmin+xmax)/2,0,(zmin+zmax)/2)
    deltax = xmax-xmin
    deltaz = zmax-zmin
    return centre,deltax,deltaz
    
# Main function
def main():
    obj_parent = op
    #on calcule le centre de tous les points de la hiérarchie
    #(ne tient pas compte de la position des objets !)
    temp = getHierarchyCenter(obj_parent)
    if not temp:
        print("pas de points")
        return
    centre,deltax,deltaz = temp
    #TODO : vérifier que l'on n'a pas un ou plusieurs objet à 0 et les autres aux coordonnées'
    
    #calcul de l'échelle
    #on regarde la position de l'objet et on calcule en fonction des coordonnées nationales
    scale_factor = 0.0001
    #c'est un peu une méthode bourrin...
    #je pars de l'échelle de base et je fais chaque fois x10
    #en regardant si les coordonnée du premeir objet entre dans les coordonnées suisses..
    #si i arrive à la fin c'est que 
    for i in range(10):
        if CH_XMIN < centre.x*scale_factor < CH_XMAX and CH_YMIN < centre.z*scale_factor < CH_YMAX:
            break
        scale_factor*=10
    if i == 9:
        c4d.gui.MessageDialog("Problème d'échelle")
        return
    print(scale_factor)   

    #si le doc n'est pas géoref  :
    if not doc[CONTAINER_ORIGIN]:
        #on met l'origine du doc au centre
        doc[CONTAINER_ORIGIN] = centre
        
    scale_and_translationOnHierarchy(obj_parent.GetDown(),scale_factor,doc)
    c4d.EventAdd()
        
    return

# Execute main()
if __name__=='__main__':
    main()