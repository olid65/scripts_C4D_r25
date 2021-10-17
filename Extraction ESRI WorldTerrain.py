import c4d,os,sys, json
import webbrowser
import urllib.request


sys.path.append(os.path.dirname(__file__))

import geotif

#print(geotif.getCalageFromGeoTif)
#from geotif import getCalageFromGeoTif



CONTAINER_ORIGIN =1026473

NB_PIXEL_MAX = 4096
TAILE_MAILLE_MIN = 0

#CONTAINER_ORIGIN =1026473
ORIGIN_DEFAULT = c4d.Vector(2500370.00,0.0,1117990.0) # île Rousseau

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

class Bbox(object):
    def __init__(self,mini,maxi):

        self.min = mini
        self.max = maxi
        self.centre = (self.min+self.max)/2
        self.largeur = self.max.x - self.min.x
        self.hauteur = self.max.z - self.min.z
        self.taille = self.max-self.min

    def intersect(self,bbx2):
        """video explicative sur http://www.youtube.com/watch?v=8b_reDI7iPM"""
        return ( (self.min.x+ self.taille.x)>= bbx2.min.x and
                self.min.x <= (bbx2.min.x + bbx2.taille.x) and
                (self.min.z + self.taille.z) >= bbx2.min.z and
                self.min.z <= (bbx2.min.z + bbx2.taille.z))

    def xInside(self,x):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return x>= self.min.x and x<= self.max.x

    def zInside(self,y):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return y>= self.min.z and y<= self.max.z

    def isInsideX(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.xInside(bbox2.xmin)
        maxInside = self.xInside(bbox2.xmax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.xmin < self.min.x and bbox2.xmax > self.max.x : return 2
        return 0

    def isInsideZ(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.zInside(bbox2.ymin)
        maxInside = self.zInside(bbox2.ymax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.ymin < self.min.z and bbox2.ymax > self.max.z : return 2
        return 0

    def ptIsInside(self,pt):
        """renvoie vrai si point c4d est à l'intérieur"""
        return  self.xInside(pt.x) and self.zInside(pt.z)

    def getRandomPointInside(self, y = 0):
        x = self.min.x + random.random()*self.largeur
        z = self.min.z + random.random()*self.hauteur
        return c4d.Vector(x,y,z)

    def GetSpline(self,origine = c4d.Vector(0)):
        """renvoie une spline c4d de la bbox"""
        res = c4d.SplineObject(4,c4d.SPLINETYPE_LINEAR)
        res[c4d.SPLINEOBJECT_CLOSED] = True
        res.SetAllPoints([c4d.Vector(self.min.x,0,self.max.z)-origine,
                           c4d.Vector(self.max.x,0,self.max.z)-origine,
                           c4d.Vector(self.max.x,0,self.min.z)-origine,
                           c4d.Vector(self.min.x,0,self.min.z)-origine])
        res.Message(c4d.MSG_UPDATE)
        return res
    def __str__(self):
        return ('X : '+str(self.min.x)+'-'+str(self.max.x)+'->'+str(self.max.x-self.min.x)+'\n'+
                'Y : '+str(self.min.z)+'-'+str(self.max.z)+'->'+str(self.max.z-self.min.z))

    def GetCube(self,haut = 200):
    	res = c4d.BaseObject(c4d.Ocube)
    	taille = c4d.Vector(self.largeur,haut,self.hauteur)
    	res.SetAbsPos(self.centre)
    	return res

    @staticmethod
    def fromObj(obj,origine = c4d.Vector()):
        """renvoie la bbox 2d de l'objet"""
        mg = obj.GetMg()

        rad = obj.GetRad()
        centre = obj.GetMp()

        #4 points de la bbox selon orientation de l'objet
        pts = [ c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z+rad.z) * mg]

        mini = c4d.Vector(min([p.x for p in pts]),min([p.y for p in pts]),min([p.z for p in pts])) + origine
        maxi = c4d.Vector(max([p.x for p in pts]),max([p.y for p in pts]),max([p.z for p in pts])) + origine

        return Bbox(mini,maxi)

    @staticmethod
    def fromView(basedraw,origine = c4d.Vector()):
        dimension = basedraw.GetFrame()
        largeur = dimension["cr"]-dimension["cl"]
        hauteur = dimension["cb"]-dimension["ct"]

        mini =  basedraw.SW(c4d.Vector(0,hauteur,0)) + origine
        maxi = basedraw.SW(c4d.Vector(largeur,0,0)) + origine
        return Bbox(mini,maxi)



def coordFromClipboard():

    clipboard =  c4d.GetStringFromClipboard()

    if not clipboard : return None

    try :
        res = [float(s) for s in clipboard.split(',')]
        xmin,xmax,ymin,ymax = res
    except :
        return None

    return Bbox(c4d.Vector(xmin,0,ymin),c4d.Vector(xmax,0,ymax))

#####################################################################################
# DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG DIALOG
#####################################################################################

class EsriWorldTerrainDlg (c4d.gui.GeDialog):

    ID_GRP_MAIN = 1000
    ID_TXT_TITRE = 1001
    ID_TXT_REMARQUE = 1002

    ID_GRP_ETENDUE = 1010
    ID_GRPE_COORD = 1030
    ID_XMIN = 1011
    ID_XMAX = 1012
    ID_YMIN = 1013
    ID_YMAX = 1014
    ID_TXT_XMIN = 1015
    ID_TXT_XMAX = 1016
    ID_TXT_YMIN = 1017
    ID_TXT_YMAX = 1018

    ID_GRP_ETENDUE_BTONS = 1020
    ID_BTON_EMPRISE_VUE_HAUT = 1021
    ID_BTON_EMPRISE_OBJET = 1022
    ID_BTON_COLLER_COORDONNEES = 1023


    ID_GRP_TAILLE = 1050
    ID_TXT_TAILLE_MAILLE = 1051
    ID_TAILLE_MAILLE = 1052
    ID_TXT_NB_POLYS_LARG = 10153
    ID_NB_POLYS_LARG =1054

    ID_TXT_NB_POLYS = 1055
    ID_NB_POLYS = 1056
    ID_TXT_NB_POLYS_HAUT = 1057
    ID_NB_POLYS_HAUT = 1058

    ID_GRP_BUTTONS = 1070
    ID_BTON_TEST_JETON = 1071
    ID_BTON_REQUEST = 1072
    ID_BTON_IMPORT_GEOTIF = 1073



    TXT_TITRE = "Extraction ESRI WorldElevation"
    TXT_REMARQUE = "Pour que l'extraction soit possible vous devez disposer d'un compte ESRI"
    TXT_TITRE_GRP_ETENDUE = "Etendue de l'extraction"
    TXT_BTON_EMPRISE_VUE_HAUT = "emprise selon vue de haut"
    TXT_EMPRISE_OBJET = "emprise selon objet sélectionné"
    TXT_COLLER_COORDONNEES = "coller les valeurs du presse papier"

    TXT_TITTRE_GRP_TAILLE = "Taille/définition de l'extraction"

    TXT_TAILLE_MAILLE = "taille de la maille"
    TXT_NB_POLYS_LARG = "     points en largeur"
    TXT_NB_POLYS_HAUT = "     points en hauteur"
    TXT_NB_POLYS = "total de points (en Mio)"

    TXT_BTON_TEST_JETON = "tester la validité du jeton"
    TXT_BTON_REQUEST = "lancer la requête"
    TXT_BTON_IMPORT_GEOTIF = "importer le geotif"

    MSG_NO_OBJECT = "Il n' y a pas d'objet sélectionné !"
    MSG_NO_CLIPBOARD = "Le presse-papier doit contenir 4 valeurs numériques séparées par des virgules dans cet ordre xmin,xmax,ymin,ymax"
    MSG_NO_ORIGIN = "Le document n'est pas géoréférencé, action impossible !"
    MSG_NO_CAMERA_PLAN = """Ne fonctionne qu'avec une caméra active en projection "haut" """

    def __init__(self, doc):
        self.xmin = self.xmax = self.ymin = self.ymax = 0.0
        self.doc = doc
        self.origin = doc[CONTAINER_ORIGIN]
        self.width = self.height = 0

        self.gadgets_taille = []
        self.emprise_OK = False
        self.fn_to_download = None

        return

    def verif_coordonnees(self):
        self.xmin = self.xmin = self.GetFloat(self.ID_XMIN)
        self.xmax = self.GetFloat(self.ID_XMAX)
        self.ymin = self.GetFloat(self.ID_YMIN)
        self.ymax = self.GetFloat(self.ID_YMAX)

        self.width = self.xmax-self.xmin
        self.height = self.ymax - self.ymin

        # si la largeur ou la hauteur sont égales ou inférieures à 0
        # on désactive les champs taille
        # sinon on les active
        self.emprise_OK = self.width and self.height

        if self.emprise_OK:
            self.enableTailleGadgets()
        else:
            self.disableTailleGadgets()

        self.maj_taille()

        print("TODO : verif_coord")

    # ACTIVER/DESACTIVER CHAMPS TAILLE

    def enableTailleGadgets(self):
        for gadget in self.gadgets_taille:
            self.Enable(gadget, True)

    def disableTailleGadgets(self):
        for gadget in self.gadgets_taille:
            self.Enable(gadget, False)

    def maj_taille(self):
        """calcul des champs taille en fonction de la taille de la maille"""
        self.SetFloat(self.ID_TAILLE_MAILLE, self.taille_maille,format = c4d.FORMAT_METER,min=TAILE_MAILLE_MIN)
        self.nb_pts_w = int(self.width/self.taille_maille)+1
        self.nb_pts_h = int(self.height/self.taille_maille)+1
        self.SetInt32(self.ID_NB_POLYS_LARG, self.nb_pts_w)
        self.SetInt32(self.ID_NB_POLYS_HAUT, self.nb_pts_h)
        self.nb_pts = self.nb_pts_w * self.nb_pts_h/1000000.0
        self.SetFloat(self.ID_NB_POLYS, self.nb_pts)


    def verif_taille(self):
        print('verif_taille')

    def emprise_vue_haut(self):

        if not self.origin :
            c4d.gui.MessageDialog(self.MSG_NO_ORIGIN)
            return
        bd = doc.GetActiveBaseDraw()
        camera = bd.GetSceneCamera(doc)

        if not camera[c4d.CAMERA_PROJECTION]== c4d.Ptop:
            c4d.gui.MessageDialog(self.MSG_NO_CAMERA_PLAN)
            return
        bbox = Bbox.fromView(bd, self.origin)
        self.majCoord(bbox)

    def emprise_objet(self):
        if not self.origin :
            c4d.gui.MessageDialog(self.MSG_NO_ORIGIN)
            return
        obj = self.doc.GetActiveObject()
        if not obj :
            c4d.gui.MessageDialog(self.MSG_NO_OBJECT)
            return

        bbox = Bbox.fromObj(obj, self.origin)
        self.majCoord(bbox)

    def majCoord(self,bbox):
        self.SetFloat(self.ID_XMIN, bbox.min.x,format = c4d.FORMAT_METER)
        self.SetFloat(self.ID_XMAX, bbox.max.x,format = c4d.FORMAT_METER)
        self.SetFloat(self.ID_YMIN, bbox.min.z,format = c4d.FORMAT_METER)
        self.SetFloat(self.ID_YMAX, bbox.max.z,format = c4d.FORMAT_METER)
        self.verif_coordonnees()

    def coller_coordonnees(self):
        bbox = coordFromClipboard()
        if bbox:
            self.majCoord(bbox)

        else:
            c4d.gui.MessageDialog(self.MSG_NO_CLIPBOARD)

    def test_jeton(self):
        webbrowser.open('https://elevation.arcgis.com/arcgis/rest/services/WorldElevation/Terrain/ImageServer')

    def requete_MNT(self):
        sr = '2056'
        xmin,ymin,xmyx,ymax = self.getBbox()
        print(self.getBbox())
        width,height  = self.getDefinition()
        #url = 'https://elevation.arcgis.com/arcgis/rest/services/WorldElevation/Terrain/ImageServer/exportImage?f=image&bbox={bbox}&format=tiff&bboxSR={bboxSR}&imageSR={imageSR}&size={size}&pixelType=F32&adjustAspectRatio=true'.format(bbox=bbox,bboxSR=sr,imageSR=sr,size=size)
        url = f"""https://elevation.arcgis.com/arcgis/rest/services/WorldElevation/Terrain/ImageServer/exportImage?f=image&bbox={xmin},{ymin},{xmyx},{ymax}&format=tiff&bboxSR={sr}&imageSR={sr}&size={width},{height}&pixelType=F32&adjustAspectRatio=true&f=pjson"""

        #TEST SITG
        url = f"""https://ge.ch/sitgags2/rest/services/RASTER/MNA_TERRAIN/ImageServer/exportImage/exportImage?f=image&bbox={xmin},{ymin},{xmyx},{ymax}&format=tiff&bboxSR={sr}&imageSR={sr}&size={width},{height}&pixelType=F32&adjustAspectRatio=true&f=pjson"""

        fn_dst = '/Users/olivierdonze/Documents/TEMP/test_mnt3.tif'

        response = urllib.request.urlopen(url)

        status_code = response.getcode()
        print(status_code)
        if status_code ==200:
            with open(fn_dst,'wb') as f:
                f.write(response.read())
            self.fn_to_download = fn_dst

        else :
            print(f"Problème lors de la connection erreur {status_code}")

        print(url)

    def import_geotif(self):
        val_px_x,val_px_y,coord_x,coord_y = geotif.getCalageFromGTif(self.fn_to_download)
        print(f'import geotif : {self.fn_to_download}')
        self.fn_to_download = None

    def getBbox(self):
        return self.GetFloat(self.ID_XMIN), self.GetFloat(self.ID_YMIN),self.GetFloat(self.ID_XMAX),self.GetFloat(self.ID_YMAX)

    def getDefinition(self):
        return self.GetInt32(self.ID_NB_POLYS_LARG), self.GetInt32(self.ID_NB_POLYS_HAUT)


    def Command(self, id, msg):

        # MODIFICATIONS COORDONNEES
        if id == self.ID_XMIN:
            self.xmin = self.GetFloat(self.ID_XMIN)
            self.verif_coordonnees()
        if id == self.ID_XMAX:
            self.xmax = self.GetFloat(self.ID_XMAX)
            self.verif_coordonnees()
        if id == self.ID_YMIN:
            self.ymin = self.GetFloat(self.ID_YMIN)
            self.verif_coordonnees()
        if id == self.ID_YMAX:
            self.ymax = self.GetFloat(self.ID_YMAX)
            self.verif_coordonnees()

        # BOUTONS COORDONNEES
        if id == self.ID_BTON_EMPRISE_VUE_HAUT:
            self.emprise_vue_haut()

        if id == self.ID_BTON_EMPRISE_OBJET:
            self.emprise_objet()

        if id == self.ID_BTON_COLLER_COORDONNEES:
            self.coller_coordonnees()


        # CHAMPS TAILLE
        if id == self.ID_TAILLE_MAILLE:
            self.taille_maille = self.GetFloat(self.ID_TAILLE_MAILLE)
            if self.taille_maille:
                self.maj_taille()


        if id == self.ID_NB_POLYS_LARG:
            self.nb_pts_w = self.GetInt32(self.ID_NB_POLYS_LARG)

            if self.nb_pts_w:
                self.taille_maille = self.width/(self.nb_pts_w-1)
                self.maj_taille()

        if id == self.ID_NB_POLYS_HAUT:
            self.nb_pts_h = self.GetInt32(self.ID_NB_POLYS_HAUT)

            if self.nb_pts_h:
                self.taille_maille = self.height/(self.nb_pts_h-1)
                self.maj_taille()

        if id == self.ID_NB_POLYS:
            """equation selon Tim Donzé le 29 juillet 2020 à 14h00"""
            self.nb_polys = self.GetFloat(self.ID_NB_POLYS)*1000000
            rapport = self.width/self.height
            pts_larg = (self.nb_polys*rapport)**0.5
            self.taille_maille = self.width/(pts_larg-1)
            self.maj_taille()






        # BOUTONS GENERAUX
        if id == self.ID_BTON_TEST_JETON:
            self.test_jeton()

        if id == self.ID_BTON_REQUEST:
            self.requete_MNT()

        if id == self.ID_BTON_IMPORT_GEOTIF:
            self.import_geotif()



        return True

    def InitValues(self):
        self.SetFloat(self.ID_XMIN, 0.0,format = c4d.FORMAT_METER)
        self.SetFloat(self.ID_XMAX, 0.0,format = c4d.FORMAT_METER)
        self.SetFloat(self.ID_YMIN, 0.0,format = c4d.FORMAT_METER)
        self.SetFloat(self.ID_YMAX, 0.0,format = c4d.FORMAT_METER)
        self.taille_maille = 1.0
        self.SetFloat(self.ID_TAILLE_MAILLE, self.taille_maille,format = c4d.FORMAT_METER ,min=TAILE_MAILLE_MIN)
        #.SetMeter(self, id, value, min=sys.float_info.min, max=sys.float_info.max, step=1.0, tristate=False)

        #self.SetInt32(self.ID_NB_POLYS_LARG, 0.0)

        #DESACTIVATION DES CHAMPS TAILLE
        self.disableTailleGadgets()

        return True

    def CreateLayout(self):
        self.SetTitle(self.TXT_TITRE)

        self.GroupBegin(self.ID_GRP_MAIN,flags=c4d.BFH_SCALEFIT, cols=1, rows=4)
        self.GroupBorderSpace(10, 10, 10, 0)

        #self.AddStaticText(self.ID_TXT_REMARQUE,c4d.BFH_LEFT)
        #self.SetString(self.ID_TXT_REMARQUE, self.TXT_REMARQUE)

        # DEBUT GROUPE ETENDUE
        self.GroupBegin(self.ID_GRP_ETENDUE,title = self.TXT_TITRE_GRP_ETENDUE,flags=c4d.BFH_SCALEFIT, cols=1, rows=2)
        self.GroupBorderSpace(10, 10, 10, 0)
        self.GroupBorder(c4d.BORDER_GROUP_IN|c4d.BORDER_WITH_TITLE_BOLD)

        # DEBUT GRPE COORD
        self.GroupBegin(self.ID_GRPE_COORD,flags=c4d.BFH_SCALEFIT, groupflags = c4d.BFV_GRIDGROUP_EQUALCOLS|c4d.BFV_GRIDGROUP_EQUALROWS, cols=4, rows=2)
        self.GroupBorderSpace(10, 10, 10, 0)

        self.AddStaticText(self.ID_TXT_XMIN,c4d.BFH_RIGHT)
        self.SetString(self.ID_TXT_XMIN, 'xmin : ')
        self.AddEditNumberArrows(self.ID_XMIN, flags=c4d.BFH_SCALEFIT)

        self.AddStaticText(self.ID_TXT_XMAX,c4d.BFH_RIGHT)
        self.SetString(self.ID_TXT_XMAX, '      xmax : ')
        self.AddEditNumberArrows(self.ID_XMAX, flags=c4d.BFH_SCALEFIT)

        self.AddStaticText(self.ID_TXT_YMIN,c4d.BFH_RIGHT)
        self.SetString(self.ID_TXT_YMIN, 'ymin : ')
        self.AddEditNumberArrows(self.ID_YMIN, flags=c4d.BFH_SCALEFIT)

        self.AddStaticText(self.ID_TXT_YMAX,c4d.BFH_RIGHT)
        self.SetString(self.ID_TXT_YMAX, '      ymax : ')
        self.AddEditNumberArrows(self.ID_YMAX, flags=c4d.BFH_SCALEFIT)

        self.GroupEnd() #FIN GROUPE COORD

        #DEBUT GROUPE BOUTONS
        self.GroupBegin(self.ID_GRP_ETENDUE_BTONS,flags=c4d.BFH_SCALEFIT, groupflags = c4d.BFV_GRIDGROUP_EQUALCOLS|c4d.BFV_GRIDGROUP_EQUALROWS, cols=1, rows=3)
        self.GroupBorderSpace(10, 10, 10, 10)
        self.AddButton(self.ID_BTON_EMPRISE_VUE_HAUT, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, name=self.TXT_BTON_EMPRISE_VUE_HAUT)
        self.AddButton(self.ID_BTON_EMPRISE_OBJET, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, name=self.TXT_EMPRISE_OBJET)
        self.AddButton(self.ID_BTON_COLLER_COORDONNEES, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, name=self.TXT_COLLER_COORDONNEES)

        self.GroupEnd() #FIN GROUPE BOUTONS

        self.GroupEnd()
        # FIN GROUPE ETENDUE



        # DEBUT GROUPE TAILLE
        self.GroupBegin(self.ID_GRP_TAILLE,title = self.TXT_TITTRE_GRP_TAILLE,flags=c4d.BFH_SCALEFIT, cols=1, rows=2)
        self.GroupBorderSpace(10, 10, 10, 10)
        self.GroupBorder(c4d.BORDER_GROUP_OUT|c4d.BORDER_WITH_TITLE_BOLD)

        # DEBUT GRPE COORD
        self.GroupBegin(self.ID_GRPE_COORD,flags=c4d.BFH_SCALEFIT, groupflags = c4d.BFV_GRIDGROUP_EQUALCOLS|c4d.BFV_GRIDGROUP_EQUALROWS, cols=2, rows=4)
        self.GroupBorderSpace(10, 10, 10, 0)

        self.AddStaticText(self.ID_TXT_TAILLE_MAILLE,c4d.BFH_RIGHT)
        self.SetString(self.ID_TXT_TAILLE_MAILLE, self.TXT_TAILLE_MAILLE)
        self.AddEditNumberArrows(self.ID_TAILLE_MAILLE, flags=c4d.BFH_SCALEFIT)


        #self.SetFloat(self.ID_TAILLE_MAILLE, 1000.0,format = c4d.FORMAT_METER)

        self.gadgets_taille.append(self.AddStaticText(self.ID_TXT_NB_POLYS_LARG,c4d.BFH_RIGHT))
        self.SetString(self.ID_TXT_NB_POLYS_LARG, self.TXT_NB_POLYS_LARG)
        self.gadgets_taille.append(self.AddEditNumberArrows(self.ID_NB_POLYS_LARG, flags=c4d.BFH_SCALEFIT))

        self.gadgets_taille.append(self.AddStaticText(self.ID_TXT_NB_POLYS_HAUT,c4d.BFH_RIGHT))
        self.SetString(self.ID_TXT_NB_POLYS_HAUT, self.TXT_NB_POLYS_HAUT)
        self.gadgets_taille.append(self.AddEditNumberArrows(self.ID_NB_POLYS_HAUT, flags=c4d.BFH_SCALEFIT))

        self.gadgets_taille.append(self.AddStaticText(self.ID_TXT_NB_POLYS,c4d.BFH_RIGHT))
        self.SetString(self.ID_TXT_NB_POLYS, self.TXT_NB_POLYS)
        self.gadgets_taille.append(self.AddEditNumberArrows(self.ID_NB_POLYS, flags=c4d.BFH_SCALEFIT))

        self.GroupEnd()# FIN GRPE COORD

        self.GroupEnd()
        # FIN GROUPE TAILLE

        # DEBUT GROUPE BOUTONS
        self.GroupBegin(self.ID_GRP_TAILLE,title = self.TXT_TITTRE_GRP_TAILLE,flags=c4d.BFH_SCALEFIT, cols=1, rows=3)
        self.GroupBorderSpace(10, 10, 10, 10)

        self.AddButton(self.ID_BTON_TEST_JETON, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, name=self.TXT_BTON_TEST_JETON)
        self.bton_request = self.AddButton(self.ID_BTON_REQUEST, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, name=self.TXT_BTON_REQUEST)
        #self.Enable(self.bton_request,False)

        self.AddButton(self.ID_BTON_IMPORT_GEOTIF, flags=c4d.BFH_SCALEFIT, initw=0, inith=0, name=self.TXT_BTON_IMPORT_GEOTIF)

        self.GroupEnd()
        # FIN GROUPE BOUTONS

        self.GroupEnd() #FIN GROUP MAIN

        return True



# Main function
def main():
    gui.MessageDialog('Hello World!')

# Execute main()
if __name__=='__main__':
    dlg = EsriWorldTerrainDlg(doc)
    dlg.Open(c4d.DLG_TYPE_ASYNC)