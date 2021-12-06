import c4d
import os
import random
import math



# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

DIAMETRE_ARBRE_SOURCE = 10
NOM_SOURCE_VEGETATION = 'sources_vegetation'

FN_ARBRES_SOURCES = '/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/plugins/SITG_C4D/__arbres_2018__.c4d'
    
TXT_NOT_DWG = "Ce n'est pas un document dwg !"
TXT_PB_OPEN_DWG = "Problème à l'ouverture du fichier dwg !"

########################################
#DIALOG pour afficher les layers
#####################################

class DlgList(c4d.gui.GeDialog):
    ID_BTON_SELECT_ALL = 1000
    ID_BTON_DESELECT_ALL = 1001

    ID_START_CHECK = 2000

    ID_BTON_OK = 3000
    ID_BTON_CANCEL = 3001

    TXT_SELECT_ALL = 'Tout séléctionner'
    TXT_DESELECT_ALL = 'Tout déséléctionner'

    TXT_OK = 'OK'
    TXT_CANCEL = 'Annuler'

    MARGIN = 20

    def __init__(self,lst, title = ''):
        self.title = title
        self.lst = lst
        self.len_lst = len(lst)

    def CreateLayout(self):

        self.SetTitle(self.title)

        #BOUTONS DE SELECTION
        self.GroupBegin(500,flags=c4d.BFH_SCALE, cols=2, rows=1, title='', groupflags=0, initw=0, inith=0)
        self.GroupBorderSpace(self.MARGIN,self.MARGIN,self.MARGIN,self.MARGIN)
        self.AddButton(self.ID_BTON_SELECT_ALL, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_SELECT_ALL)
        self.AddButton(self.ID_BTON_DESELECT_ALL, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_DESELECT_ALL)
        self.GroupEnd()

        #CHECKBOXES depuis la liste
        self.ScrollGroupBegin(400, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, scrollflags =c4d.SCROLLGROUP_VERT, initw=80, inith=100)
        self.GroupBegin(600, flags=c4d.BFH_LEFT, cols=1, rows=len(self.lst), title='', groupflags=0, initw=0, inith=0)
        self.GroupBorderSpace(self.MARGIN,0,0,0)
        for i,el in enumerate(self.lst):
            self.AddCheckbox(self.ID_START_CHECK+i,c4d.BFH_SCALE, 100, 10, el)
        self.GroupEnd()
        self.GroupEnd()

        #OK/CANCEL buttons
        self.GroupBegin(700, flags=c4d.BFH_SCALE, cols=2, rows=1, title='', groupflags=0, initw=0, inith=0)
        self.GroupBorderSpace(self.MARGIN,self.MARGIN,self.MARGIN,self.MARGIN)
        self.AddButton(self.ID_BTON_OK, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_OK)
        self.AddButton(self.ID_BTON_CANCEL, flags=c4d.BFH_SCALE, initw=150, inith=10, name=self.TXT_CANCEL)
        self.GroupEnd()


    def Command(self, id, msg):

        if id == self.ID_BTON_SELECT_ALL:
            for i in range(self.len_lst):
                self.SetBool(self.ID_START_CHECK+i, True)

        if id == self.ID_BTON_DESELECT_ALL:
            for i in range(self.len_lst):
                self.SetBool(self.ID_START_CHECK+i, False)

        if id == self.ID_BTON_OK:
            res = []
            for i,el in enumerate(self.lst):
                if self.GetBool(self.ID_START_CHECK+i):
                    res.append(el)

            self.lst.clear()
            self.lst+=res
            self.Close()

        if id == self.ID_BTON_CANCEL:
            self.lst.clear()
            self.Close()


def getLayers(root,lst=[]):

    lyr = root.GetDown()

    while lyr:
        lst.append(lyr)
        getLayers(lyr,lst)
        lyr = lyr.GetNext()
    return lst

def getLayersDict(root,dic = {}):
    """renvoie un dictionnaire nom_layer:layer"""
    lyr = root.GetDown()

    while lyr:
        dic[lyr.GetName()] = lyr
        getLayersDict(lyr,dic)
        lyr = lyr.GetNext()
    return dic

def isCircle(obj, nb_pts_min = 5, tolerance = 0.001):

    #objet point
    if not obj.CheckType(c4d.Opoint) : return False

    #points minimum
    if obj.GetPointCount()<nb_pts_min : return False

    #distances au carré (plus rapide à calculer)
    squared_lengthes = [p.GetLengthSquared() for p in obj.GetAllPoints()]
    #différence entre le maxi et le mini
    dif = max(squared_lengthes)-min(squared_lengthes)

    if dif>tolerance : return False

    return True

def getCirclesInLayers(obj_root,layers, lst =[]):
    obj = obj_root
    while obj:
        if obj[c4d.ID_LAYER_LINK] in layers:
            if isCircle(obj):
                lst.append(obj)
        getCirclesInLayers(obj.GetDown(),layers,lst)
        obj = obj.GetNext()
    return lst


# Main function
def main():
    
    fn = '/Users/olivierdonze/Documents/Mandats/Cite_de_la_musique/export_vw/arbres_abattus-dwg/arbres_abattus.dwg'
    fn = c4d.storage.LoadDialog()
    
    if not fn : return
    
    if not fn[-4:] == '.dwg':
        c4d.gui.MessageDialog(TXT_NOT_DWG)
        return

    doc_dwg = c4d.documents.LoadDocument(fn, c4d.SCENEFILTER_OBJECTS, thread=None)
    
    if not doc_dwg:
        c4d.gui.MessageDialog(TXT_PB_OPEN_DWG)
        return


    #Liste des calques pour choix dans dialogue
    lst_lyr = getLayers(doc_dwg.GetLayerObjectRoot())
    dict_lyr = {lyr.GetName():lyr for lyr in lst_lyr}
    lst_lyr_names = [lyr.GetName() for lyr in lst_lyr ]

    #DIALOGUE CHOIX LAYERS
    dlg = DlgList(lst_lyr_names)
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE)
    
    if not lst_lyr_names : return
    
    #RECUPERATION DES CERCLES DANS LES LAYERS CHOISIS
    lst_lyr_choice = [dict_lyr[name_lyr] for name_lyr in lst_lyr_names]
        
    
    lst_circles = getCirclesInLayers(doc_dwg.GetFirstObject(),lst_lyr_choice)    
    if not lst_circles : return
    
    #SOURCES VEGETATION
    source_arbres = doc.SearchObject(NOM_SOURCE_VEGETATION)
    if not source_arbres:
        if os.path.isfile(FN_ARBRES_SOURCES):
            doc_srce_arbres = c4d.documents.LoadDocument(FN_ARBRES_SOURCES, c4d.SCENEFILTER_OBJECTS, thread=None)
            srce = doc_srce_arbres.SearchObject(NOM_SOURCE_VEGETATION)
            if srce : 
                source_arbres=srce.GetClone()
                source_arbres[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_OFF
                source_arbres[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.OBJECT_OFF                
                doc.InsertObject(source_arbres)
            c4d.documents.KillDocument(doc_srce_arbres)
    
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(fn))
    
    #dictionnaire avec tous les layers existants du doc
    lyr_root = doc.GetLayerObjectRoot()
    dict_layers_doc = getLayersDict(lyr_root)
    
    for circle in lst_circles:
        pos = circle.GetMg().off
        radius = circle.GetPoint(0).GetLength()
        inst = c4d.BaseObject(c4d.Oinstance)
        inst[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_SINGLEINSTANCE
        
        #récupération du layer, s'il n'existe pas on le clone dans le document
        lyr_dwg = circle[c4d.ID_LAYER_LINK]
        if lyr_dwg:
            lyr = dict_layers_doc.get(lyr_dwg.GetName(),None)
            if not lyr:
                lyr = lyr_dwg.GetClone()
                lyr.InsertUnder(lyr_root)
                dict_layers_doc[lyr.GetName()]=lyr
            inst[c4d.ID_LAYER_LINK] = lyr    
        
        #source des instances
        if source_arbres and source_arbres.GetChildren():
            inst[c4d.INSTANCEOBJECT_LINK] = random.choice(source_arbres.GetChildren())
        
        #récupération uniquement de la position, l'axe dwg étant en général tourné
        mg = c4d.Matrix()
        mg.off = c4d.Vector(pos)
        inst.SetMg(mg)
        
        #Echelle
        scale = c4d.Vector(radius*2/DIAMETRE_ARBRE_SOURCE)
        
        #Rotation Aléatoire
        rot = random.random() * 2 * math.pi
        inst.SetAbsRot(c4d.Vector(rot,0,0))
        
        
        inst.SetAbsScale(scale)
        inst.InsertUnderLast(res)
        continue
        clone = circle.GetClone()
        clone.SetMg(circle.GetMg())
        clone.InsertUnderLast(res)
    
    c4d.documents.KillDocument(doc_dwg)  
    doc.InsertObject(res)
    c4d.EventAdd()
    
    return

# Execute main()
if __name__=='__main__':
    main()