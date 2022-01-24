
import c4d, os
import urllib.request


CONTAINER_ORIGIN =1026473

O_DEFAUT = c4d.Vector(2500360.00,0.0,1117990.00)

def empriseVueHaut(bd,origine):

    dimension = bd.GetFrame()
    largeur = dimension["cr"]-dimension["cl"]
    hauteur = dimension["cb"]-dimension["ct"]

    mini =  bd.SW(c4d.Vector(0,hauteur,0)) + origine
    maxi = bd.SW(c4d.Vector(largeur,0,0)) + origine

    return  mini,maxi,largeur,hauteur

def get_nonexistant_path(fname_path):
    """
    Get the path to a filename which does not exist by incrementing path.

    Examples
    --------
    >>> get_nonexistant_path('/etc/issue')
    '/etc/issue-1'
    >>> get_nonexistant_path('whatever/1337bla.py')
    'whatever/1337bla.py'
    """
    if not os.path.exists(fname_path):
        return fname_path
    filename, file_extension = os.path.splitext(fname_path)
    i = 1
    new_fname = "{}-{}{}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        i += 1
        new_fname = "{}-{}{}".format(filename, i, file_extension)
    return new_fname

def main():
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        doc[CONTAINER_ORIGIN] = O_DEFAUT
        origine = doc[CONTAINER_ORIGIN]
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)
    if not camera[c4d.CAMERA_PROJECTION]== c4d.Ptop:
        c4d.gui.MessageDialog("""Ne fonctionne qu'avec une caméra en projection "haut" """)
        return

    mini,maxi,larg,haut = empriseVueHaut(bd,origine)
    #larg = 3840/2
    #haut = 2160/2
    #print mini.x,mini.z,maxi.x,maxi.z
    bbox = '{0}%2C{1}%2C{2}%2C{3}'.format(mini.x,mini.z,maxi.x,maxi.z) # 2499639.5233%2C1117120.08436258%2C2500839.57718198%2C1118560.1287&
    size = '{0},{1}'.format(larg,haut)
    bboxSR = '2056'
    imageSR = '2056'
    url = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox={0}&format=jpg&size={1}&f=image&bboxSR={2}&imageSR={3}'.format(bbox,size,bboxSR,imageSR)

    with urllib.request.urlopen(url) as site:
        img = site.read()

    fn =  get_nonexistant_path('/Users/olivierdonze/Documents/TEMP/ESRI_world_imagery.jpg')
    out = open(fn, 'wb')
    out.write(img)
    out.close()
    bd[c4d.BASEDRAW_DATA_PICTURE] = fn
    bd[c4d.BASEDRAW_DATA_SIZEX] = maxi.x-mini.x
    bd[c4d.BASEDRAW_DATA_SIZEY] = maxi.z-mini.z


    bd[c4d.BASEDRAW_DATA_OFFSETX] = (maxi.x+mini.x)/2 -origine.x
    bd[c4d.BASEDRAW_DATA_OFFSETY] = (maxi.z+mini.z)/2-origine.z

    c4d.EventAdd()

if __name__=='__main__':
    main()