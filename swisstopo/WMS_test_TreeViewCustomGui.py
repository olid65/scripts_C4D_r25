import c4d
import os
import json
from pprint import pprint
import urllib.request


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


# Be sure to use a unique ID obtained from http://www.plugincafe.com/.
PLUGIN_ID = 1000050 # TEST ID ONLY



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
    bd[c4d.BASEDRAW_DATA_PICTURE_USEALPHA] = c4d.BASEDRAW_ALPHA_NORMAL
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

class LayerWMS(object):

    def __init__(self,name,title, abstract):
        self.name = name
        self.title = title
        self.abstract = abstract
        self._selected = False

    @property
    def IsSelected(self):
        return self._selected

    def Select(self):
        self._selected = True

    def Deselect(self):
        self._selected = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.title


# TreeView Column IDs.
ID_CHECKBOX = 1
ID_NAME = 2
ID_OTHER = 3

##############################################################################################################################################

class ListView(c4d.gui.TreeViewFunctions):

    def __init__(self, dlg, layers):
        self.dlg = dlg
        self.listOfTexture = list() # Store all objects we need to display in this list
        self.layers = layers
        self.layers_all = layers.copy()
        self.last = None

    def IsResizeColAllowed(self, root, userdata, lColID):
        return True

    def IsTristate(self, root, userdata):
        return False

    def GetColumnWidth(self, root, userdata, obj, col, area):
        return 80  # All have the same initial width

    def IsMoveColAllowed(self, root, userdata, lColID):
        # The user is allowed to move all columns.
        # TREEVIEW_MOVE_COLUMN must be set in the container of AddCustomGui.
        return True

    def GetFirst(self, root, userdata):
        """
        Return the first element in the hierarchy, or None if there is no element.
        """
        rValue = None if not self.layers else self.layers[0]
        return rValue

    def GetDown(self, root, userdata, obj):
        """
        Return a child of a node, since we only want a list, we return None everytime
        """
        return None

    def GetNext(self, root, userdata, obj):
        """
        Returns the next Object to display after arg:'obj'
        """
        rValue = None
        currentObjIndex = self.layers.index(obj)
        nextIndex = currentObjIndex + 1
        if nextIndex < len(self.layers):
            rValue = self.layers[nextIndex]

        return rValue

    def GetPred(self, root, userdata, obj):
        """
        Returns the previous Object to display before arg:'obj'
        """
        rValue = None
        currentObjIndex = self.layers.index(obj)
        predIndex = currentObjIndex - 1
        if 0 <= predIndex < len(self.layers):
            rValue = self.layers[predIndex]

        return rValue

    def GetId(self, root, userdata, obj):
        """
        Return a unique ID for the element in the TreeView.
        """
        return hash(obj)

    def Select(self, root, userdata, obj, mode):
        """
        Called when the user selects an element.
        """
        if mode == c4d.SELECTION_NEW:
            for tex in self.layers:
                tex.Deselect()
            obj.Select()
            display_wms_swisstopo(obj.name)
            self.last = obj
            self.dlg.majTxt()
        elif mode == c4d.SELECTION_ADD:
            obj.Select()
        elif mode == c4d.SELECTION_SUB:
            obj.Deselect()

    def IsSelected(self, root, userdata, obj):
        """
        Returns: True if *obj* is selected, False if not.
        """
        return obj.IsSelected

    def SetCheck(self, root, userdata, obj, column, checked, msg):
        """
        Called when the user clicks on a checkbox for an object in a
        `c4d.LV_CHECKBOX` column.
        """
        if checked:
            obj.Select()
        else:
            obj.Deselect()

    def IsChecked(self, root, userdata, obj, column):
        """
        Returns: (int): Status of the checkbox in the specified *column* for *obj*.
        """
        if obj.IsSelected:
            return c4d.LV_CHECKBOX_CHECKED | c4d.LV_CHECKBOX_ENABLED
        else:
            return c4d.LV_CHECKBOX_ENABLED

    def GetName(self, root, userdata, obj):
        """
        Returns the name to display for arg:'obj', only called for column of type LV_TREE
        """
        return '' # Or obj.texturePath

    def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
        """
        Draw into a Cell, only called for column of type LV_USER
        """
        rgbSelectedColor = c4d.gui.GeUserArea().GetColorRGB(c4d.COLOR_TEXT_SELECTED)
        selectedColor = c4d.Vector(rgbSelectedColor["r"], rgbSelectedColor["g"], rgbSelectedColor["b"]) / 255.0
        txtColor = selectedColor if obj.IsSelected else c4d.Vector(0.2, 0.4, 0.8)
        drawinfo["frame"].DrawSetTextCol(txtColor, drawinfo["bgCol"])

        if col == ID_NAME:
            name = str(obj)
            geUserArea = drawinfo["frame"]
            w = geUserArea.DrawGetTextWidth(name)
            h = geUserArea.DrawGetFontHeight()
            xpos = drawinfo["xpos"]
            ypos = drawinfo["ypos"] + drawinfo["height"]
            drawinfo["frame"].DrawText(name, xpos, int(ypos - h * 1.1))
            xpos = drawinfo["xpos"]
            ypos = drawinfo["ypos"] + drawinfo["height"]

        if col == ID_OTHER:
            name = obj.otherData
            geUserArea = drawinfo["frame"]
            w = geUserArea.DrawGetTextWidth(name)
            h = geUserArea.DrawGetFontHeight()
            xpos = drawinfo["xpos"]
            ypos = drawinfo["ypos"] + drawinfo["height"]
            drawinfo["frame"].DrawText(name, xpos, ypos - h * 1.1)

    def DoubleClick(self, root, userdata, obj, col, mouseinfo):
        """
        Called when the user double-clicks on an entry in the TreeView.

        Returns:
          (bool): True if the double-click was handled, False if the
            default action should kick in. The default action will invoke
            the rename procedure for the object, causing `SetName()` to be
            called.
        """
        c4d.gui.MessageDialog("You clicked on " + str(obj))
        return True

    def DeletePressed(self, root, userdata):
        "Called when a delete event is received."
        for tex in reversed(self.layers):
            if tex.IsSelected:
                self.layers.remove(tex)

##############################################################################################################################################

#TODO : liste déroulante pour choisir des listes de choix prédéfinis (fichiers json)
#-> aussi créer un bouton pour créer des listes

#TODO : fonction pour chercher dans la liste

class TestDialog(c4d.gui.GeDialog):
    
    ID_LST_CHOIX_PREDF = 950
    ID_TXT_SEARCH = 951

    ID_TREEGUI = 1000
    ID_BTON_ADD = 1001
    ID_ABSTRACT_TXT = 1200
    ID_URL_TXT = 1201

    fn_choice = '__layers_choice.json'
    fn_choice = os.path.join(os.path.dirname(__file__),fn_choice)

    def __init__(self,layers):
        self.layers = layers
        self._listView = ListView(self,layers) # Our Instance of c4d.gui.TreeViewFunctions
        self._treegui = None # Our CustomGui TreeView

    def CreateLayout(self):
        
        # Create the TreeView GUI.
        customgui = c4d.BaseContainer()
        customgui.SetBool(c4d.TREEVIEW_BORDER, c4d.BORDER_THIN_IN)
        customgui.SetBool(c4d.TREEVIEW_HAS_HEADER, True) # True if the tree view may have a header line.
        customgui.SetBool(c4d.TREEVIEW_HIDE_LINES, False) # True if no lines should be drawn.
        customgui.SetBool(c4d.TREEVIEW_MOVE_COLUMN, True) # True if the user can move the columns.
        customgui.SetBool(c4d.TREEVIEW_RESIZE_HEADER, True) # True if the column width can be changed by the user.
        customgui.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True) # True if all lines have the same height.
        customgui.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True) # Alternate background per line.
        customgui.SetBool(c4d.TREEVIEW_CURSORKEYS, True) # True if cursor keys should be processed.
        customgui.SetBool(c4d.TREEVIEW_NOENTERRENAME, False) # Suppresses the rename popup when the user presses enter.
        
        self.AddEditText(self.ID_TXT_SEARCH, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,initw=0, inith=0)

        self.GroupBegin(900, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=2, rows=3, title='', groupflags=0, initw=0, inith=0)
        
        
        
        self._treegui = self.AddCustomGui(self.ID_TREEGUI, c4d.CUSTOMGUI_TREEVIEW, "", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 300, 300, customgui)
        if not self._treegui:
            print ("[ERROR]: Could not create TreeView")
            return False
        self.AddMultiLineEditText(self.ID_ABSTRACT_TXT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,initw=0, inith=0, style=c4d.DR_MULTILINE_READONLY| c4d.DR_MULTILINE_WORDWRAP)
        self.AddButton(self.ID_BTON_ADD, c4d.BFH_CENTER, name="Ajouter à la liste")


        self.AddStaticText(self.ID_URL_TXT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, initw=0, inith=0, name='', borderstyle=0)
        self.GroupEnd()
        return True

    def InitValues(self):
        # Initialize the column layout for the TreeView.
        layout = c4d.BaseContainer()
        layout.SetLong(ID_CHECKBOX, c4d.LV_TREE)
        layout.SetLong(ID_NAME, c4d.LV_USER)
        layout.SetLong(ID_OTHER, c4d.LV_USER)
        self._treegui.SetLayout(2, layout)

        # Set the header titles.
        self._treegui.SetHeaderText(ID_CHECKBOX, "")
        self._treegui.SetHeaderText(ID_NAME, "Name")
        self._treegui.SetHeaderText(ID_OTHER, "Other")
        self._treegui.Refresh()

        # Set TreeViewFunctions instance used by our CUSTOMGUI_TREEVIEW
        self._treegui.SetRoot(self._treegui, self._listView, None)


        #
        self.SetString(self.ID_ABSTRACT_TXT,'-')
        self.SetString(self.ID_URL_TXT,'--')
        return True

    def Command(self, id, msg):
        # Click on button
        if id == self.ID_BTON_ADD:
            self.addToChoice([lyr for lyr in self._listView.layers if lyr.IsSelected])

        if id == self.ID_TXT_SEARCH:
            txt = self.GetString(self.ID_TXT_SEARCH).lower()
            if txt:
                new_lyr = [lyr for lyr in self._listView.layers_all if txt in lyr.title.lower()]
                self._listView.layers = new_lyr.copy()
                
                # Refresh the TreeView
                self._treegui.Refresh()
            else:
                self._listView.layers = self._listView.layers_all.copy()
                
                # Refresh the TreeView
                self._treegui.Refresh()
                
        return True

    def majTxt(self):
        if self._listView.last:
            self.SetString(self.ID_ABSTRACT_TXT,self._listView.last.abstract)
            self.SetString(self.ID_URL_TXT,self._listView.last.name)
        return True

    def addToChoice(self,lst, encoding = 'utf-8'):
        
        data = [{'Name':lyr.name,'Title':lyr.title,'Abstract':lyr.abstract} for lyr in lst]
        
        #si le fichier de choix existe on l'ouvre et on fusionne les datas
        data_exist = None
        if os.path.isfile(self.fn_choice):
            with open(self.fn_choice,'r') as f:
                data_exist = json.loads(f.read())
                
        if data_exist:
            for lyr in data_exist:
                if lyr not in data:
                    data.append(lyr)
        #tri de la liste par ordre alpha name 
        #-> TODO trier par organisme (à extraire dans nom) puis titre
        temp = [(lyr['Name'].split('.')[1],lyr['Title'],lyr) for lyr in data]
        data = [lyr for organisme,title,lyr in sorted(temp)]

        with open(self.fn_choice,'w') as f:
            f.write(json.dumps(data,indent=2))
            



# Main function
def getLayersFromJson(fn = '/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/library/scripts/swisstopo/wms.geo.admin.ch_layers_only.json'):


    with open(fn) as f:
        data = json.loads(f.read())

    layers = []
    if data:
        for layer in data:
            layers.append(LayerWMS(layer['Name'],layer['Title'],layer['Abstract']))

    return layers

def main():
    global dlg

    layers = getLayersFromJson()
    dlg = TestDialog(layers)
    dlg.Open(c4d.DLG_TYPE_ASYNC, PLUGIN_ID, defaulth=600, defaultw=600)

# Execute main()
if __name__=='__main__':
    main()