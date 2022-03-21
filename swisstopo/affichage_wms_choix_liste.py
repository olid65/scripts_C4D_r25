import c4d
import os
import json
from pprint import pprint
import urllib.request

#from c4d.plugins import GeLoadString as txt
from datetime import datetime

CONTAINER_ORIGIN =1026473

NOT_SAVED_TXT = "Le document doit être enregistré pour pouvoir copier les textures dans le dossier tex, vous pourrez le faire à la prochaine étape\nVoulez-vous continuer ?"
DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"
O_DEFAUT = c4d.Vector(2500000.00,0.0,1120000.00)

FORMAT = 'png'
NOM_DOSSIER_IMG = 'tex/__back_image'

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True
def empriseVueHaut(bd,origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"]-dimension["cl"]
    hauteur = dimension["cb"]-dimension["ct"]

    mini =  bd.SW(c4d.Vector(0,hauteur,0)) + origine
    maxi = bd.SW(c4d.Vector(largeur,0,0)) + origine

    return  mini,maxi,largeur,hauteur

def display_wms_swisstopo(layer):
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



    #si le document n'est pas enregistré on enregistre
    path_doc = doc.GetDocumentPath()

    while not path_doc:
        rep = c4d.gui.QuestionDialog(NOT_SAVED_TXT)
        if not rep : return
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()

    dossier_img = os.path.join(path_doc,NOM_DOSSIER_IMG)

    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        doc[CONTAINER_ORIGIN] = O_DEFAUT
        origine = doc[CONTAINER_ORIGIN]
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)
    if not camera[c4d.CAMERA_PROJECTION]== c4d.Ptop:
        c4d.gui.MessageDialog("""Ne fonctionne qu'avec une caméra en projection "haut" """)
        return

    #pour le format de la date regarder : https://docs.python.org/fr/3/library/datetime.html#strftime-strptime-behavior
    dt = datetime.now()
    suffixe_time = dt.strftime("%y%m%d_%H%M%S")

    fn = f'ortho{suffixe_time}.png'
    fn_img = os.path.join(dossier_img,fn)

    if not os.path.isdir(dossier_img):
            os.makedirs(dossier_img)


    mini,maxi,width_img,height_img = empriseVueHaut(bd,origine)

    bbox = f'{mini.x},{mini.z},{maxi.x},{maxi.z}'

    url = f'http://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={layer}&STYLES=default&CRS=EPSG:2056&BBOX={bbox}&WIDTH={width_img}&HEIGHT={height_img}&FORMAT=image/png'


    try:
        x = urllib.request.urlopen(url)

        with open(fn_img,'wb') as saveFile:
            saveFile.write(x.read())

    except Exception as e:
        print(str(e))

    #on récupère l'ancienne image
    old_fn = os.path.join(dossier_img,bd[c4d.BASEDRAW_DATA_PICTURE])


    bd[c4d.BASEDRAW_DATA_PICTURE] = fn
    bd[c4d.BASEDRAW_DATA_SIZEX] = maxi.x-mini.x
    bd[c4d.BASEDRAW_DATA_SIZEY] = maxi.z-mini.z


    bd[c4d.BASEDRAW_DATA_OFFSETX] = (maxi.x+mini.x)/2 -origine.x
    bd[c4d.BASEDRAW_DATA_OFFSETY] = (maxi.z+mini.z)/2-origine.z
    #bd[c4d.BASEDRAW_DATA_SHOWPICTURE] = False

    #suppression de l'ancienne image
    #TODO : s'assurer que c'est bien une image générée NE PAS SUPPRIMER N'IMPORTE QUOI !!!
    if os.path.exists(old_fn):
        try : os.remove(old_fn)
        except : pass
    c4d.EventAdd(c4d.EVENT_FORCEREDRAW)


class DlgBbox(c4d.gui.GeDialog):
    COMBO_LAYERS = 1001
    BTON_REFRESH = 1002
    MARGIN = 10
    layers = []

    def CreateLayout(self):

        #lecture du json layers
        fn = 'wms.geo.admin.ch_layers_only.json'
        fn = os.path.join(os.path.dirname(__file__),fn)
        self.lst_urls = []
        self.lst_layers = []
        with open(fn) as  f:
            data = json.loads(f.read())

            for lyr in data:
                self.lst_layers.append(lyr['Title'])
                self.lst_urls.append(lyr['Name'])


        self.SetTitle("swisstopo display")
        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=1, rows=2)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)

        self.AddComboBox(self.COMBO_LAYERS, flags=c4d.BFH_LEFT, initw=500, inith=0, specialalign=False, allowfiltering=True)

        if self.lst_layers:
            for i,lyr in enumerate(self.lst_layers):
                self.AddChild(self.COMBO_LAYERS,i+1,lyr)

        self.AddButton(self.BTON_REFRESH, flags=c4d.BFH_MASK, initw=0, inith=0, name="rafraîchir la vue")

        self.GroupEnd()

        return True

    def Command(self, id, msg):
        if id == self.COMBO_LAYERS:
            i = self.GetInt32(self.COMBO_LAYERS)-1
            display_wms_swisstopo(self.lst_urls[i])
            #print(self.lst_urls[i])
            #print(self.lst_layers[i])
            #print('-'*20)

        if id==self.BTON_REFRESH:
            i = self.GetInt32(self.COMBO_LAYERS)-1
            display_wms_swisstopo(self.lst_urls[i])

        return True

# Main function
def main():
    global dlg
    dlg = DlgBbox()
    dlg.Open(c4d.DLG_TYPE_ASYNC)

# Execute main()
if __name__=='__main__':
    main()