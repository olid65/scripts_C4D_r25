
import c4d
import shapefile
import os, json, sys
import socket
import json
import urllib
from zipfile import ZipFile
import subprocess

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
# def state():
#    return True

sys.path.append(os.path.dirname(__file__))
from thread_download import ThreadDownload

CONTAINER_ORIGIN = 1026473


URL_STAC_SWISSTOPO_BASE = 'https://data.geo.admin.ch/api/stac/v0.9/collections/'

DIC_LAYERS = {'ortho':'ch.swisstopo.swissimage-dop10',
              'mnt':'ch.swisstopo.swissalti3d',
              'bati3D':'ch.swisstopo.swissbuildings3d_2',
              }

#Fichier pour le noms de lieu au m^ême emplacement que ce fichier
LOCATIONS_FILE = os.path.join(os.path.dirname(__file__),'noms_lieux.json')

def dirImgToTextFile(path_dir, ext = '.tif'):
    """crée un fichier texte avec le chemin de l'image pour chaque ligne"""
    fn_txt = path_dir+'.txt'
    len_ext = len(ext)
    lst_img = [os.path.join(path_dir,fn) for fn in os.listdir(path_dir) if fn[-len_ext:] == ext]

    if lst_img :
        with open(fn_txt,'w') as f:
            for fn in lst_img:
                f.write(fn+'\n')
        return fn_txt
    return False

##################################################################################################
#GDAL
##################################################################################################

def getPathToQGISbin(path_to_QGIS = None):
    #Si le path_to_QGIS n'est pas renseigné on prend le chemin par défaut selon la plateforme
    win = sys.platform == 'win32'
    if not path_to_QGIS:
        if sys.platform == 'win32':
            path_to_QGIS = 'C:\\Program Files'
        else:
            path_to_QGIS = '/Applications'
    for folder_name in os.listdir(path_to_QGIS):
        if 'QGIS'  in folder_name:
            if win :
                path = os.path.join(path_to_QGIS,folder_name,'bin')
            else:

                path = os.path.join(path_to_QGIS,folder_name,'Contents/MacOS/bin')

            if os.path.isdir(path):
                return path
    return None

def gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate'):
    if sys.platform == 'win32':
        exe+='.exe'
    path = os.path.join(path_to_QGIS_bin,exe)
    if os.path.isfile(path):
        return path
    else:
        return False

def createVRTfromDir(path_tifs, path_to_gdalbuildvrt = None):
    if not path_to_gdalbuildvrt:
        path_to_QGIS_bin = getPathToQGISbin()
        if path_to_QGIS_bin:
            path_to_gdalbuildvrt = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdalbuildvrt')

    if not path_to_gdalbuildvrt:
        c4d.gui.MessageDialog("La génération du raster virtuel (.vrt) est impossible")
        return False
    fn_vrt = path_tifs+'.vrt'
    #fichier texte avec listes images tif
    lst_img_txt = dirImgToTextFile(path_tifs, ext = '.tif')
    if lst_img_txt:
        req = f'"{path_to_gdalbuildvrt}" -input_file_list "{lst_img_txt}" "{fn_vrt}"'
        output = subprocess.check_output(req,shell=True)
        #on supprime le fichier txt
        os.remove(lst_img_txt)
        if os.path.isfile(fn_vrt):

            return fn_vrt

    return False

def extractFromBbox(raster_srce, raster_dst,xmin,ymin,xmax,ymax,path_to_gdal_translate = None):
    """normalement l'extension du fichier de destination permet le choix du format (à vérifier)
       si on a du .png ou du .jpg un fichier wld est généré"""

    name,ext = os.path.splitext(raster_dst)
    if ext in ['.jpg','.png']:
        wld = '-co worldfile=yes'
    else:
        wld = ''
    if not path_to_gdal_translate:
        path_to_QGIS_bin = getPathToQGISbin()
        if path_to_QGIS_bin:
            path_to_gdal_translate = gdalBIN_OK(path_to_QGIS_bin, exe = 'gdal_translate')

    if not path_to_gdal_translate:
        c4d.gui.MessageDialog("L'extraction est impossible, gdal_translate non trouvé")
        return False
    req = f'"{path_to_gdal_translate}" {wld} -projwin {xmin} {ymax} {xmax} {ymin} "{raster_srce}" "{raster_dst}"'
    output = subprocess.check_output(req,shell=True)
    if os.path.isfile(raster_dst):
        return raster_dst

    return False

######################################################################################################

def verify_web_connexion(hostname = "www.google.com"):
  """pour vérifier s'il y a une connexion internet"""
  # from : https://askcodez.com/tester-si-une-connexion-internet-est-presente-en-python.html
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi, largeur, hauteur


def empriseObject(obj, origine):
    mg = obj.GetMg()

    rad = obj.GetRad()
    centre = obj.GetMp()

    # 4 points de la bbox selon orientation de l'objet
    pts = [c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z + rad.z) * mg]

    mini = c4d.Vector(min([p.x for p in pts]), min([p.y for p in pts]), min([p.z for p in pts])) + origine
    maxi = c4d.Vector(max([p.x for p in pts]), max([p.y for p in pts]), max([p.z for p in pts])) + origine

    return mini, maxi


def fichierPRJ(fn):
    fn = os.path.splitext(fn)[0] + '.prj'
    f = open(fn, 'w')
    f.write(
        """PROJCS["CH1903+_LV95",GEOGCS["GCS_CH1903+",DATUM["D_CH1903+",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["latitude_of_center",46.95240555555556],PARAMETER["longitude_of_center",7.439583333333333],PARAMETER["azimuth",90],PARAMETER["scale_factor",1],PARAMETER["false_easting",2600000],PARAMETER["false_northing",1200000],UNIT["Meter",1]]""")
    f.close()


def bbox2shapefile(mini, maxi):
    poly = [[[mini.x, mini.z], [mini.x, maxi.z], [maxi.x, maxi.z], [maxi.x, mini.z]]]

    fn = c4d.storage.LoadDialog(flags=c4d.FILESELECT_SAVE)

    if not fn: return
    with shapefile.Writer(fn, shapefile.POLYGON) as w:
        w.field('id', 'I')
        w.record(1)
        w.poly(poly)

        fichierPRJ(fn)

def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])


def get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax):
    #pour les bati3D il y a chaque fois toute la Suisse dans 2 gdb
    #pour les mnt on aussi du xyz
    # attention bien prendre les 8 derniers caractères
    lst_indesirables = ['.xyz.zip','.gdb.zip']
    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"


    url += sufixe_url
    f = urllib.request.urlopen(url)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    res = []

    for item in json_res['features']:
        for k,dic in item['assets'].items():
            href = dic['href']

            if href[-8:] not in lst_indesirables:
                res.append(dic['href'])
    return res

class DlgBbox(c4d.gui.GeDialog):
    N_MIN = 1015
    N_MAX = 1016
    E_MIN = 1017
    E_MAX = 1018

    COMBO_LOCALISATION =1039
    BTON_ORTHO = 1040
    BTON_CN = 1041

    BTON_FROM_OBJECT = 1050
    BTON_FROM_VIEW = 1051
    BTON_COPY_ALL = 1052
    BTON_PLANE = 1053
    BTON_EXPORT_SHP = 1054

    BTON_N_MIN = 1055
    BTON_N_MAX = 1056
    BTON_E_MIN = 1057
    BTON_E_MAX = 1058

    CHECKBOX_MNT2M = 1500
    CHECKBOX_MNT50CM = 1501
    CHECKBOX_BATI3D = 1502
    CHECKBOX_ORTHO2M = 1503
    CHECKBOX_ORTHO10CM = 1504

    BTON_GET_URLS_DOWNLOAD = 1600

    ID_TXT_DOWNLOAD_STATUS = 1700


    LABEL_MNT2M = "MNT 2m"
    LABEL_MNT50CM = "MNT 50cm"
    LABEL_BATI3D = "Bâtiments 3D"
    LABEL_ORTHO2M = "Orthophoto 2m"
    LABEL_ORTHO10CM = "Orthophoto 10cm"


    TXT_NO_ORIGIN = "Le document n'est pas géoréférencé !"
    TXT_NOT_VIEW_TOP = "Vous devez activer une vue de haut !"
    TXT_NO_SELECTION = "Vous devez sélectionner un objet !"
    TXT_MULTI_SELECTION = "Vous devez sélectionner un seul objet !"

    TITLE_GEOLOC = "1. Géolocalisation et affichage d'arrière plan"
    TITLE_EMPRISE = "2. Définissez l'emprise de l'extraction"
    TITLE_LAYER_CHOICE = "3. Choisissez les couches"
    TITLE_LIST_TO_DOWNLOAD = "4. Liste des fichiers à télécharger"

    MARGIN = 10
    LARG_COORD = 130

    dico_lieux = None
    lst_lieux = None

    def CreateLayout(self):
        #lecture du fichier des lieux
        if os.path.isfile(LOCATIONS_FILE):
            with open(LOCATIONS_FILE, encoding = 'utf-8') as f:
                self.dico_lieux = json.load(f)
            if self.dico_lieux:
                self. lst_lieux =[k for k in self.dico_lieux.keys()]


        self.SetTitle("swisstopo extractor")
        # MAIN GROUP
        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=1, rows=6)
        self.GroupBorderSpace(self.MARGIN*2, self.MARGIN*2, self.MARGIN*2, self.MARGIN*2)

        # GEOLOCALISATION
        self.AddStaticText(400, flags=c4d.BFH_LEFT, initw=0, inith=0, name=self.TITLE_GEOLOC, borderstyle=c4d.BORDER_WITH_TITLE_BOLD)

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)

        self.AddComboBox(self.COMBO_LOCALISATION, flags=c4d.BFH_LEFT, initw=200, inith=0, specialalign=False, allowfiltering=True)
        #
        self.AddChild(self.COMBO_LOCALISATION,0,'--choisissez un lieu--')
        if self.dico_lieux:
            for i,k in enumerate(self.dico_lieux.keys()):
                self.AddChild(self.COMBO_LOCALISATION,i+1,k)

        self.AddButton(self.BTON_ORTHO, flags=c4d.BFH_MASK, initw=0, inith=0, name="orthophoto")
        self.AddButton(self.BTON_CN, flags=c4d.BFH_MASK, initw=0, inith=0, name="carte nationale")
        self.GroupEnd()
        self.AddSeparatorH( initw=150, flags=c4d.BFH_FIT)

        # EMPRISE
        self.AddStaticText(400, flags=c4d.BFH_LEFT, initw=0, inith=0, name=self.TITLE_EMPRISE, borderstyle=c4d.BORDER_WITH_TITLE_BOLD)

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.AddStaticText(1001, name="Nord :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.N_MAX, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_N_MAX, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=7, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.AddStaticText(1003, name="Est :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.E_MIN, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_E_MIN, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.AddStaticText(1005, name="", flags=c4d.BFH_MASK, initw=200)
        self.AddStaticText(1004, name="Ouest :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.E_MAX, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_E_MAX, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.AddStaticText(1002, name="Sud :", flags=c4d.BFH_MASK, initw=50)
        self.AddEditNumber(self.N_MIN, flags=c4d.BFH_MASK, initw=self.LARG_COORD, inith=0)
        self.AddButton(self.BTON_N_MIN, flags=c4d.BFH_MASK, initw=0, inith=0, name="copier")
        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=2, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, 0)

        self.AddButton(self.BTON_FROM_OBJECT, flags=c4d.BFH_MASK, initw=150, inith=20, name="depuis la sélection")
        self.AddButton(self.BTON_FROM_VIEW, flags=c4d.BFH_MASK, initw=150, inith=20, name="depuis la vue")

        self.GroupEnd()

        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=3, rows=1)
        self.GroupBorderSpace(self.MARGIN, 0, self.MARGIN, self.MARGIN)

        self.AddButton(self.BTON_COPY_ALL, flags=c4d.BFH_MASK, initw=150, inith=20, name="copier toutes les valeurs")
        self.AddButton(self.BTON_PLANE, flags=c4d.BFH_MASK, initw=150, inith=20, name="créer un plan")
        self.AddButton(self.BTON_EXPORT_SHP, flags=c4d.BFH_MASK, initw=150, inith=20, name="créer un shapefile")

        self.GroupEnd()

        self.AddSeparatorH( initw=150, flags=c4d.BFH_FIT)

        #CHOIX COUCHES
        self.AddStaticText(401, flags=c4d.BFH_LEFT, initw=0, inith=0, name=self.TITLE_LAYER_CHOICE, borderstyle=c4d.BORDER_WITH_TITLE_BOLD)

        self.GroupBegin(600, flags=c4d.BFH_CENTER, cols=1, rows=3)
        self.GroupBegin(600, flags=c4d.BFH_CENTER, cols=2, rows=1)
        self.AddCheckbox(self.CHECKBOX_MNT2M, flags=c4d.BFH_MASK, initw=150, inith=20, name=self.LABEL_MNT2M)
        self.AddCheckbox(self.CHECKBOX_MNT50CM, flags=c4d.BFH_MASK, initw=150, inith=20, name=self.LABEL_MNT50CM)
        self.GroupEnd()

        self.AddCheckbox(self.CHECKBOX_BATI3D, flags=c4d.BFH_MASK, initw=150, inith=20, name=self.LABEL_BATI3D)

        self.GroupBegin(600, flags=c4d.BFH_CENTER, cols=2, rows=1)
        self.AddCheckbox(self.CHECKBOX_ORTHO2M, flags=c4d.BFH_MASK, initw=150, inith=20, name=self.LABEL_ORTHO2M)
        self.AddCheckbox(self.CHECKBOX_ORTHO10CM, flags=c4d.BFH_MASK, initw=150, inith=20, name=self.LABEL_ORTHO10CM)
        self.GroupEnd()

        self.GroupEnd()

        # LISTE DES TELECHARGEMNT
        self.AddStaticText(701, flags=c4d.BFH_LEFT, initw=0, inith=0, name=self.TITLE_LIST_TO_DOWNLOAD, borderstyle=c4d.BORDER_WITH_TITLE_BOLD)

        self.GroupBegin(700, flags=c4d.BFH_CENTER, cols=1, rows=1)
        self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)

        self.AddButton(self.BTON_GET_URLS_DOWNLOAD, flags=c4d.BFH_MASK, initw=250, inith=20, name="Téléchargement")

        self.GroupEnd()

        #ETAT DU TELECHARGEMENT
        #self.GroupBegin(700, flags=c4d.BFH_SCALEFIT, cols=1, rows=1)
        #self.GroupBorderSpace(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)

        self.AddStaticText(self.ID_TXT_DOWNLOAD_STATUS, flags=c4d.BFH_RIGHT, initw=500, inith=0, name="Pas de téléchargement en cours", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)

        #self.GroupEnd()
        self.GroupEnd()
        return True

    def InitValues(self):
        self.SetMeter(self.N_MAX, 0.0)
        self.SetMeter(self.N_MIN, 0.0)
        self.SetMeter(self.E_MIN, 0.0)
        self.SetMeter(self.E_MAX, 0.0)
        return True

    def getBbox(self):
        mini = c4d.Vector()
        maxi = c4d.Vector()
        maxi.z = self.GetFloat(self.N_MAX)
        mini.z = self.GetFloat(self.N_MIN)
        maxi.x = self.GetFloat(self.E_MAX)
        mini.x = self.GetFloat(self.E_MIN)
        return mini, maxi

    def planeFromBbox(self, mini, maxi, origine):
        plane = c4d.BaseObject(c4d.Oplane)
        plane[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_YP
        plane[c4d.PRIM_PLANE_SUBW] = 1
        plane[c4d.PRIM_PLANE_SUBH] = 1

        plane[c4d.PRIM_PLANE_WIDTH] = maxi.x - mini.x
        plane[c4d.PRIM_PLANE_HEIGHT] = maxi.z - mini.z

        pos = (mini + maxi) / 2 - origine

        plane.SetAbsPos(pos)
        return plane

    def Command(self, id, msg):
        #########
        # 1 : GEOLOCALISATION
        #########

        # Choix du lieu
        if id == self.COMBO_LOCALISATION:
            id_lieu = self.GetInt32(self.COMBO_LOCALISATION)
            if id_lieu>0:
                id_lieu-=1
                nom_lieu = self.lst_lieux[id_lieu]
                x,z = self.dico_lieux[nom_lieu]
                pos = c4d.Vector(float(x),0,float(z))

                rep = True
                doc = c4d.documents.GetActiveDocument()
                if doc[CONTAINER_ORIGIN]:
                    rep  = c4d.gui.QuestionDialog("Le document est déjà géoréférencé voulez-vous modifier l'origine")

                if rep :
                    doc[CONTAINER_ORIGIN] = pos

                    #TODO remettre la camera au centre
                    c4d.EventAdd()

        #Affichage OrthoPhoto
        if id ==self.BTON_ORTHO:
            c4d.CallCommand(1058393) # #$00orthophoto


        #Affichage CarteNationale
        if id ==self.BTON_CN:
            c4d.CallCommand(1058394) # #$01carte nationale 10'000


        # DEPUIS L'OBJET ACTIF
        # TODO : sélection multiple
        if id == self.BTON_FROM_OBJECT:
            doc = c4d.documents.GetActiveDocument()
            origine = doc[CONTAINER_ORIGIN]
            if not origine:
                c4d.gui.MessageDialog(self.TXT_NO_ORIGIN)
                return True
            op = doc.GetActiveObjects(0)
            if not op:
                c4d.gui.MessageDialog(self.TXT_NO_SELECTION)
                return True
            if len(op) > 1:
                c4d.gui.MessageDialog(self.TXT_MULTI_SELECTION)
                return True
            obj = op[0]

            mini, maxi = empriseObject(obj, origine)
            self.SetMeter(self.N_MAX, maxi.z)
            self.SetMeter(self.N_MIN, mini.z)
            self.SetMeter(self.E_MIN, mini.x)
            self.SetMeter(self.E_MAX, maxi.x)

        # DEPUIS LA VUE DE HAUT
        if id == self.BTON_FROM_VIEW:
            doc = c4d.documents.GetActiveDocument()
            origine = doc[CONTAINER_ORIGIN]
            if not origine:
                c4d.gui.MessageDialog(self.TXT_NO_ORIGIN)
                return True

            bd = doc.GetActiveBaseDraw()
            camera = bd.GetSceneCamera(doc)
            if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
                c4d.gui.MessageDialog(self.TXT_NOT_VIEW_TOP)
                return True

            mini, maxi, larg, haut = empriseVueHaut(bd, origine)
            self.SetMeter(self.N_MAX, maxi.z)
            self.SetMeter(self.N_MIN, mini.z)
            self.SetMeter(self.E_MIN, mini.x)
            self.SetMeter(self.E_MAX, maxi.x)

        # COPIER LES VALEURS (et print)
        if id == self.BTON_COPY_ALL:
            n_max = self.GetFloat(self.N_MAX)
            n_min = self.GetFloat(self.N_MIN)
            e_max = self.GetFloat(self.E_MAX)
            e_min = self.GetFloat(self.E_MIN)
            txt = "{0},{1},{2},{3}".format(e_min,n_min,e_max,n_max)
            print(txt)
            c4d.CopyStringToClipboard(txt)

        # CREER UN PLAN
        if id == self.BTON_PLANE:

            mini, maxi = self.getBbox()

            if mini == c4d.Vector(0) or maxi == c4d.Vector(0):
                return True
            doc = c4d.documents.GetActiveDocument()
            doc.StartUndo()
            origine = doc[CONTAINER_ORIGIN]
            if not origine:
                origine = (mini + maxi) / 2
                # pas réussi à faire un undo pour le doc !
                doc[CONTAINER_ORIGIN] = origine

            plane = self.planeFromBbox(mini, maxi, origine)
            doc.AddUndo(c4d.UNDOTYPE_NEW, plane)
            doc.InsertObject(plane)
            doc.EndUndo()
            c4d.EventAdd()

        # EXPORT SHAPEFILE
        if id == self.BTON_EXPORT_SHP:
            mini, maxi = self.getBbox()
            if mini == c4d.Vector(0) or maxi == c4d.Vector(0):
                return True

            bbox2shapefile(mini, maxi)

        # BOUTONS COPIE COORDONNöE
        if id == self.BTON_N_MIN:
            c4d.CopyStringToClipboard(str(self.GetFloat(self.N_MIN)))

        if id == self.BTON_N_MAX:
            c4d.CopyStringToClipboard(self.GetFloat(self.N_MAX))

        if id == self.BTON_E_MIN:
            c4d.CopyStringToClipboard(str(self.GetFloat(self.E_MIN)))

        if id == self.BTON_E_MAX:
            c4d.CopyStringToClipboard(str(self.GetFloat(self.E_MAX)))


        #############################################################
        # 3 CHOIX DES COUCHES
        if id == self.CHECKBOX_MNT2M:
            # si le 50 cm est actif on le désactive
            if self.GetBool(self.CHECKBOX_MNT50CM):
                self.SetBool(self.CHECKBOX_MNT50CM,False)

        if id == self.CHECKBOX_MNT50CM:
            # si le 50 cm est actif on le désactive
            if self.GetBool(self.CHECKBOX_MNT2M):
                self.SetBool(self.CHECKBOX_MNT2M,False)


        if id == self.CHECKBOX_BATI3D:
            pass

        if id == self.CHECKBOX_ORTHO2M:
            # si le 50 cm est actif on le désactive
            if self.GetBool(self.CHECKBOX_ORTHO10CM):
                self.SetBool(self.CHECKBOX_ORTHO10CM,False)

        if id == self.CHECKBOX_ORTHO10CM:
            # si le 50 cm est actif on le désactive
            if self.GetBool(self.CHECKBOX_ORTHO2M):
                self.SetBool(self.CHECKBOX_ORTHO2M,False)


        #############################################################
        # 4 LISTE DES TELECHARGEMENTs

        #TODO : désactiver le bouton si les coordonnées ne sont pas bonnes !

        if id == self.BTON_GET_URLS_DOWNLOAD:
            bbox = self.getDialogBbox()

            if not bbox :
                c4d.gui.MessageDialog("Coordonnées non valides")
                return True

            if bbox:
                xmin,ymin,xmax,ymax = bbox
                #self.dic_downloads = {}
                urls =[]

                #MNT
                if self.GetBool(self.CHECKBOX_MNT2M) or self.GetBool(self.CHECKBOX_MNT50CM):
                    #on
                    tri = '_2_'
                    if self.GetBool(self.CHECKBOX_MNT50CM): tri = '_0.5_'

                    url = URL_STAC_SWISSTOPO_BASE+DIC_LAYERS['mnt']
                    lst = [v for v in get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax) if tri in v]
                    urls+= lst
                    #for v in lst : print(v)
                    #print('---------')

                #BATI3D
                if self.GetBool(self.CHECKBOX_BATI3D):
                    url = URL_STAC_SWISSTOPO_BASE+DIC_LAYERS['bati3D']
                    lst = get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax)
                    urls+= lst
                    #for v in lst : print(v)
                    #print('---------')

                #ORTHO
                if self.GetBool(self.CHECKBOX_ORTHO2M) or self.GetBool(self.CHECKBOX_ORTHO10CM):
                    tri = '_2_'
                    if self.GetBool(self.CHECKBOX_ORTHO10CM):
                        tri = '_0.1_'


                    url = URL_STAC_SWISSTOPO_BASE+DIC_LAYERS['ortho']
                    lst = [v for v in get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax) if tri in v]

                    urls+= lst
                    #for v in lst : print(v)
                    #print('---------')

                #TELECHARGEMENT
                doc = c4d.documents.GetActiveDocument()

                pth = c4d.storage.LoadDialog(title = 'Dossier pour les fichiers à télécharger',def_path = doc.GetDocumentPath(),flags = c4d.FILESELECT_DIRECTORY)
                if not pth:
                    return True
                #pth = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo'

                self.dirs = []

                #list de tuple url,fn_dest pour envoyer dans le Thread
                self.dwload_lst = []

                for url in urls:
                    name_file = url.split('/')[-1]
                    name_dir = name_file.split('_')[0]
                    path_dir = os.path.join(pth,name_dir)
                    if '_0.1_'in name_file:
                        path_dir+='_10cm'
                    elif '_0.5_'in name_file:
                        path_dir+='_50cm'
                    elif '_2_'in name_file and not 'swissbuildings3d' in name_file :
                        path_dir+='_2m'

                    if not os.path.isdir(path_dir):
                        os.mkdir(path_dir)

                    fn = os.path.join(path_dir,name_file)
                    name,ext = os.path.splitext(fn)

                    self.dirs.append(path_dir)

                    self.dwload_lst.append((url,fn))


                #LANCEMENT DU THREAD
                self.thread = ThreadDownload(self.dwload_lst)
                self.thread.Start()

                #lancement du timer pour voir l'avancement du téléchargement
                self.SetTimer(500)
                return True

                #création des fichiers vrt pour les rasters
                for directory in self.dirs:
                    name = os.path.basename(directory)
                    if 'swissalti3d' in name or 'swissimage' in name:
                        vrt_file = createVRTfromDir(directory, path_to_gdalbuildvrt = None)

                        #+ extraction de l'image'
                        raster_dst = vrt_file.replace('.vrt','.png')

                        if 'swissalti3d' in name:
                            raster_dst = vrt_file.replace('.vrt','.asc')
                        extractFromBbox(vrt_file, raster_dst,xmin,ymin,xmax,ymax,path_to_gdal_translate = None)



        return True

    def Timer(self,msg):
        nb = 0
        for url,fn in self.dwload_lst:
            if os.path.isfile(fn):
                nb+=1

        self.SetString(self.ID_TXT_DOWNLOAD_STATUS,f'nombre de fichiers téléchargés : {nb}/{len(self.dwload_lst)}')

        #si le thread est terminé on arr^ête le Timer et on lance la création des vrt
        if not self.thread.IsRunning():
            self.SetTimer(0)
            self.SetString(self.ID_TXT_DOWNLOAD_STATUS,f'Téléchargement terminé')



    def getDialogBbox(self):

        xmin,ymin,xmax,ymax = self.GetFloat(self.E_MIN),self.GetFloat(self.N_MIN),self.GetFloat(self.E_MAX),self.GetFloat(self.N_MAX)

        if not xmin or not xmax or not ymin or not ymax:
            return False

        if xmax<xmin : return False
        if ymax<ymin : return False

        return xmin,ymin,xmax,ymax



URL_STAC_SWISSTOPO_BASE = 'https://data.geo.admin.ch/api/stac/v0.9/collections/'

DIC_LAYERS = {'ortho':'ch.swisstopo.swissimage-dop10',
              'mnt':'ch.swisstopo.swissalti3d',
              'bati3D':'ch.swisstopo.swissbuildings3d_2',
              }
def main():
    dlg = DlgBbox()
    dlg.Open(c4d.DLG_TYPE_ASYNC)


# Execute main()
if __name__ == '__main__':

    #main()
    dlg = DlgBbox()
    dlg.Open(c4d.DLG_TYPE_ASYNC)