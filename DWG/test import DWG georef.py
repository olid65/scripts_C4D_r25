import c4d
import os.path
import re


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

#TODO : fusionner les layers si on fait plusieurs imports
#TODO : comment déceler un fichier non géoref ?

TXT_NOT_DWG = "Ce n'est pas un document dwg !"
TXT_PB_OPEN_DWG = "Problème à l'ouverture du fichier dwg !"

DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"

CONTAINER_ORIGIN =1026473

ALERT_SIZE_FN = 10 #taille pour alerter si un document est trop gros en Mo


def import_DWG_georef(fn,doc):
    
    if not fn : return False
    
    #le doc doit être en mètres
    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()

    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata

    if not fn[-4:] == '.dwg':
        c4d.gui.MessageDialog(TXT_NOT_DWG)
        return False
    #contrôle de la taille du fichier
    #le problème est qu'il faut forcément tout importer avant de voir si c'est géoréférencé
    #et si il y a trop d'éléments C4D rame à mort !'
    size = round(os.path.getsize(fn)/1000000,1)
    if size > ALERT_SIZE_FN:
        rep = c4d.gui.QuestionDialog( f"le fichier dépasse les {ALERT_SIZE_FN}Mo ({size}Mo).\n"\
                                       "Il est conseillé de supprimer tous les calques inutiles avant l'import\n"\
                                       "L'import risque d'être long, voulez-vous vraiment continuer ?")
        if not rep:
            return False

    c4d.documents.MergeDocument(doc,fn, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MERGESCENE, thread=None)
    #if not doc_dwg:
        #c4d.gui.MessageDialog(TXT_PB_OPEN_DWG)
        #return

    origine = doc[CONTAINER_ORIGIN]

    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    obj_parent = doc.GetFirstObject()

    scale_factor = None

    for o in obj_parent.GetChildren():
        #print(o.GetLayerObject(doc))
        clone = o.GetClone()
        #suppression du tag matériau
        tag = clone.GetTag(c4d.Ttexture)
        if tag :
            tag.Remove()
        mg = o.GetMg()
        pos = mg.off

        #Facteur d'échelle : si pas encore définit
        #on regarde la position de l'objet et on calcule en fonction des coordonnées nationales
        if not scale_factor:
            scale_factor = 0.0001
            #c'est un peu une méthode bourrin...
            #je pars de l'échelle de base et je fais chaque fois x10
            #en regardant si les coordonnée du premeir objet entre dans les coordonnées suisses..
            #si i arrive à la fin c'est que
            for i in range(10):
                if CH_XMIN < pos.x*scale_factor < CH_XMAX and CH_YMIN < pos.z*scale_factor < CH_YMAX:
                    break
                scale_factor*=10
            if i == 9:
                c4d.gui.MessageDialog("Problème d'échelle")
                return
            print(scale_factor)
        pos = pos*scale_factor
        
        if not origine:
            doc[CONTAINER_ORIGIN] = c4d.Vector(pos.x,0,pos.z)
            print(pos)
            origine = doc[CONTAINER_ORIGIN]

        if o.CheckType(c4d.Opoint):
            pts = [pt*mg*scale_factor -pos for pt in clone.GetAllPoints()]
            clone.SetAllPoints(pts)
            clone.Message(c4d.MSG_UPDATE)

        mg_clone = c4d.Matrix(off = pos-origine)
        clone.InsertUnderLast(res)
        clone.SetMg(mg_clone)

    doc.InsertObject(res)

    #suppression de l'objet source
    obj_parent.Remove()
    c4d.EventAdd()
    


#Emprise des coordonnées
CH_XMIN, CH_YMIN, CH_XMAX, CH_YMAX = 1988000.00, 87000.00, 2906900.00, 1421600.00


# Main function
def main():
    doc = c4d.documents.GetActiveDocument()
    fn = c4d.storage.LoadDialog()
    import_DWG_georef(fn,doc)
    return
    
    
    
    #le doc doit être en mètres
    doc = c4d.documents.GetActiveDocument()

    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()

    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata

    #fn = '/Users/olivierdonze/Downloads/Dessin2(1).dwg'
    #fn = '/Users/olivierdonze/switchdrive/Mandats/Cite_de_la_musique/doc_base/1786_20210225_Plan des aménagement extérieurs.dwg'
    #fn = c4d.storage.LoadDialog()

    if not fn : return

    if not fn[-4:] == '.dwg':
        c4d.gui.MessageDialog(TXT_NOT_DWG)
        return

    #contrôle de la taille du fichier
    #le problème est qu'il faut forcément tout importer avant de voir si c'est géoréférencé
    #et si il y a trop d'éléments C4D rame à mort !'
    size = round(os.path.getsize(fn)/1000000,1)
    if size > ALERT_SIZE_FN:
        rep = c4d.gui.QuestionDialog( f"le fichier dépasse les {ALERT_SIZE_FN}Mo ({size}Mo).\n"\
                                       "Il est conseillé de supprimer tous les calques inutiles avant l'import\n"\
                                       "L'import risque d'être long, voulez-vous vraiment continuer ?")
        if not rep:
            return

    c4d.documents.MergeDocument(doc,fn, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MERGESCENE, thread=None)

    #if not doc_dwg:
        #c4d.gui.MessageDialog(TXT_PB_OPEN_DWG)
        #return

    origine = doc[CONTAINER_ORIGIN]

    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    obj_parent = doc.GetFirstObject()

    scale_factor = None

    for o in obj_parent.GetChildren():
        #print(o.GetLayerObject(doc))
        clone = o.GetClone()
        #suppression du tag matériau
        tag = clone.GetTag(c4d.Ttexture)
        if tag :
            tag.Remove()
        mg = o.GetMg()
        pos = mg.off

        #Facteur d'échelle : si pas encore définit
        #on regarde la position de l'objet et on calcule en fonction des coordonnées nationales
        if not scale_factor:
            scale_factor = 0.0001
            #c'est un peu une méthode bourrin...
            #je pars de l'échelle de base et je fais chaque fois x10
            #en regardant si les coordonnée du premeir objet entre dans les coordonnées suisses..
            #si i arrive à la fin c'est que
            for i in range(10):
                if CH_XMIN < pos.x*scale_factor < CH_XMAX and CH_YMIN < pos.z*scale_factor < CH_YMAX:
                    break
                scale_factor*=10
            if i == 9:
                c4d.gui.MessageDialog("Problème d'échelle")
                return
            print(scale_factor)
        pos = pos*scale_factor
        #print(pos)
        if not origine:
            doc[CONTAINER_ORIGIN] = c4d.Vector(pos.x,0,pos.z)
            print(pos)
            origine = doc[CONTAINER_ORIGIN]
        #mg.off = pos-origine

        if o.CheckType(c4d.Opoint):
            pts = [pt*mg*scale_factor -pos for pt in clone.GetAllPoints()]
            clone.SetAllPoints(pts)
            clone.Message(c4d.MSG_UPDATE)

        mg_clone = c4d.Matrix(off = pos-origine)
        clone.InsertUnderLast(res)
        clone.SetMg(mg_clone)

    doc.InsertObject(res)

    #suppression de l'objet source
    obj_parent.Remove()
    c4d.EventAdd()




# Execute main()
if __name__=='__main__':
    main()