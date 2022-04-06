import c4d
import os.path
import re


TXT_NOT_DWG = "Ce n'est pas un document dwg !"
TXT_PB_OPEN_DWG = "Problème à l'ouverture du fichier dwg !"

DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"

CONTAINER_ORIGIN =1026473

ALERT_SIZE_FN = 10 #taille pour alerter si un document est trop gros en Mo

#Emprise des coordonnées 
CH_XMIN, CH_YMIN, CH_XMAX, CH_YMAX = 1988000.00, 87000.00, 2906900.00, 1421600.00

def getAllLayers(lyr,res = {}):
    """fonction recursive qui renvoie un dico
       nom calque, liste de calques"""
    while lyr:
        res.setdefault(lyr.GetName(),[]).append(lyr)
        getAllLayers(lyr.GetDown(),res)
        lyr = lyr.GetNext()
    return res


def parseAllObjects(obj,doc,dico_lyr):
    """ fonction récursive pour parcourir les objets
        et leur appliquer le premier calque qui correspond au nom
        (les calques doublons seront ensuite effecés)"""
    while obj:
        lyr = obj.GetLayerObject(doc)
        if lyr:
            lst = dico_lyr[lyr.GetName()]
            if len(lst)>1:
                doc.AddUndo(c4d.UNDOTYPE_CHANGE,obj)
                obj.SetLayerObject(lst[0])
        parseAllObjects(obj.GetDown(),doc,dico_lyr)
        obj = obj.GetNext()

def groupByLayer(lst_obj, doc,parent = None):
    """regroupe la liste d'objet dans un neutre par calque
       si les objet ont une indication de calque"""
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

    fn = c4d.storage.LoadDialog()
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

    #remise par défaut des options d'importation DWG
    #j'ai eu quelques soucis sur un fichier qund les options étaient en mètre -> à investiguer
    plug = c4d.plugins.FindPlugin(c4d.FORMAT_DWG_IMPORT, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        print ("pas de module d'import DWG")
        return 
    op = {}
    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):
        
        import_data = op.get("imexporter",None)
        if not import_data:
            print ("pas de data pour l'import 3Ds")
            return
        
        # Change 3DS import settings
        scale = import_data[c4d.DWGFILTER_SCALE]
        scale.SetUnitScale(1,c4d.DOCUMENT_UNIT_CM)
        import_data[c4d.DWGFILTER_SCALE] = scale
        import_data[c4d.DWGFILTER_CURVE_SUBDIVISION_FACTOR] = 24
        import_data[c4d.DWGFILTER_KEEP_IGES] = False

    doc.StartUndo()
    first_obj = doc.GetFirstObject()
    c4d.documents.MergeDocument(doc,fn, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MERGESCENE, thread=None)
    if doc.GetFirstObject() != first_obj:
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,doc.GetFirstObject())

    origine = doc[CONTAINER_ORIGIN]

    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    obj_parent = doc.GetFirstObject()
    
    scale_factor = None

    for o in obj_parent.GetChildren():
        clone = o.GetClone()
        #suppression du tag matériau
        tag = clone.GetTag(c4d.Ttexture)
        if tag :
            tag.Remove()
        mg = o.GetMg()
        pos = mg.off

        #Facteur d'échelle : si pas encore défini
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
            #print(scale_factor)   
        pos = pos*scale_factor
        #print(pos)
        if not origine:
            doc[CONTAINER_ORIGIN] = c4d.Vector(pos.x,0,pos.z)
            #print(pos)
            origine = doc[CONTAINER_ORIGIN]
        #mg.off = pos-origine
        
        #si on a un objet point (spline ou poly, on le met à l'échelle)
        if o.CheckType(c4d.Opoint):
            pts = [pt*mg*scale_factor -pos for pt in clone.GetAllPoints()]
            clone.SetAllPoints(pts)
            clone.Message(c4d.MSG_UPDATE)
        
        #Attention pour les instances (blocs autocad) il y a un objet ref contenu dans un neutre

        mg_clone = c4d.Matrix(off = pos-origine)
        clone.InsertUnderLast(res)
        clone.SetMg(mg_clone)

    doc.InsertObject(res)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,res)
    
    #suppression de l'objet source
    obj_parent.Remove()

    #suppression des calques en double
    dico_lyr = getAllLayers(doc.GetLayerObjectRoot().GetDown())
    #pprint(dico_lyr)

    #parcours de tous les objet et on attribue le premier calque des deux
    parseAllObjects(doc.GetFirstObject(),doc,dico_lyr)

    #suppression des calques à double
    lst_lyr_to_remove = []
    for name,lst in dico_lyr.items():
        if len(lst)>1:
            for lyr in lst[1:]:
                lst_lyr_to_remove.append(lyr)
    for lyr in  lst_lyr_to_remove:
        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ,lyr)
        lyr.Remove()
        #print(lyr.GetName())
    #il faut vider le dico sinon il reste rempli d'un appel à l'autre !    
    dico_lyr.clear()

    #regroupement des objets dans un neutre par calques
    groupByLayer(res.GetChildren(), doc,parent = res)

    doc.EndUndo()
    c4d.EventAdd()

    return True




# Execute main()
if __name__=='__main__':
    main()