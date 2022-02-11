import c4d
import json
import os.path
import urllib.request, urllib.error, urllib.parse
from math import ceil


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473

ALERT_NB_PTS = 2000000 #nombre de points à partir duquel on alerte

SR = 2056

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    #return mini, maxi, largeur, hauteur
    return mini.x,mini.z,maxi.x,maxi.z


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

    return mini.x,mini.z,maxi.x,maxi.z

def get_json_from_url(url):
    req = urllib.request.Request(url=url)
    try :
        resp = urllib.request.urlopen(req)

    except urllib.error.HTTPError as e:
        print(f'HTTPError: {e.code}')
        return None

    except urllib.error.URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        # ...
        print(f'URLError: {e.reason}')
        return None

    else:
        # 200
        data = json.loads(resp.read().decode("utf-8"))
        return data

    return None

# Main function
def main():

    origine = doc[CONTAINER_ORIGIN]

    if not origine:
        print("pas d'origine")
        return

    xmin,ymin,xmax,ymax = 0,0,0,0

    if op:
        if op.CheckType(c4d.Opoint):
            xmin,ymin,xmax,ymax = empriseObject(op, origine)
        else:
            xmin,ymin,xmax,ymax = empriseObject(op.GetCache(), origine)

    if not xmin:
        print("pas d'objet sélectionné")
        return

    url_base = 'https://hepiageo2.hesge.ch/server/rest/services/geneve/MNA_SURFACE_AGGLO_2014/ImageServer'

    ################################################
    #recuperation des infos sur la couche
    ################################################
    url = url_base + '?f=json'

    data = get_json_from_url(url)
    size_px = data['pixelSizeX']
    height_max = data['maxImageHeight']
    width_max = data['maxImageWidth']

    #calcul de la taille de l'image en px
    width = xmax-xmin
    height = ymax-ymin


    #si on dépasse la taille max (height_max,width_max)
    #ou si on dépasse la taille d'alerte  on adapte la taille du pixel

    alert = ""
    new_size_px = size_px
    size_x = int(round(width / size_px))
    size_y = int(round(height / size_px))
    
    if size_x> width_max or size_y > height_max:
        new_size_px = max([width_max/width, height_max/height])
        
        # on arrondi au 10ème supérieur
        new_size_px = ceil(new_size_px*10)/10

        size_x = int(round(width / new_size_px))
        size_y = int(round(height / new_size_px))


        alert = (f"""La taille maximale d'extraction du serveur ({width_max} x {height_max}px) a été dépassée.
                     La taille du pixel a été modifiée à {round(new_size_px,1)}m au lieu de {size_px}m
                     Voulez-vous coninuer ?"""  )
    
    size_x = int(round(width / new_size_px))
    size_y = int(round(height / new_size_px))

    nb_pts = size_x * size_y
    
    if nb_pts>ALERT_NB_PTS:

        #nombre de points en millions
        mio = round(nb_pts/1000000,1)
        
        new_size_px = 1/(ALERT_NB_PTS/(height*width))**0.5
        
        # on arrondi au 10ème supérieur
        new_size_px = ceil(new_size_px*10)/10

        alert = (f"Il y a {mio} millions de points,"
                 f"La taille du pixel a été modifiée à {round(new_size_px,1)}m au lieu de {size_px}m"
                 f"Voulez-vous coninuer ?")
    size_px = new_size_px   
    size_x = int(round(width / size_px))
    size_y = int(round(height / size_px))

    nb_pts = size_x * size_y 
    
    if alert :
        rep = c4d.gui.QuestionDialog(alert)
        if not rep : return

    #'https://hepiageo2.hesge.ch/server/rest/services/geneve/MNA_SURFACE_AGGLO_2014/ImageServer/exportImage?bbox=2463049.5889282227%2C1086111.0001220703%2C2532057.0889282227%2C1156000.0001220703&bboxSR=&size=&imageSR=&time=&format=tiff&pixelType=F32&noData=&noDataInterpretation=esriNoDataMatchAny&interpolation=+RSP_BilinearInterpolation&compression=&compressionQuality=&bandIds=&sliceId=&mosaicRule=&renderingRule=&adjustAspectRatio=true&lercVersion=1&compressionTolerance=&f=pjson'

    #https://hepiageo2.hesge.ch/server/rest/services/geneve/MNA_SURFACE_AGGLO_2014/ImageServer?f=pjson
    
    params = {
                'bbox' :f'{xmin},{ymin},{xmax},{ymax}',
                'size': f'{size_x},{size_y}',
                'adjustAspectRatio' :'true',
                'imageSR':f'{SR}',
                'bboxSR':f'{SR}',
                'format':'tiff',
                'pixelType' : 'F32',
                'noData':'0',
                'f': 'json',
             }

    query_string = urllib.parse.urlencode( params )

    url = url_base + '/exportImage?'+query_string
    print(url)
    data = get_json_from_url(url)
    
    try :

        url_tif = data["href"]
        width = data["width"]
        height = data["height"]
        
        xmin = data['extent']['xmin']
        ymin = data['extent']['ymin']
        xmax = data['extent']['xmax']
        ymax = data['extent']['ymax']
    
    except:
        print(f'problème : {url_tif}')
        return
    
    
    #téléchargement de l'image
    
    ext = url_tif[-4:]
    pth = '/Users/olivierdonze/Documents/TEMP/test_ESRI_API_REST'
    name = f'{round(xmin)}_{round(ymin)}_{round(xmax)}_{round(ymax)}'
    image_name = f'{name}{ext}'
    calage_name = f'{name}.json'
    
    #fichier calage
    fn_calage = os.path.join(pth,calage_name)
    with open(fn_calage,'w') as calage_file:
        json.dump(data, calage_file, indent=4)
        
    
    #fichier image    
    fn_img = os.path.join(pth,image_name)
    
    urllib.request.urlretrieve(url_tif, fn_img)
    
    
    

# Execute main()
if __name__=='__main__':
    main()