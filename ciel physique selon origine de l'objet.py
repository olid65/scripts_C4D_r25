import c4d
import urllib, json
from datetime import datetime


"""Crée un physical sky et le règle selon la latitude longitude de l'origine du doc,
   Active la GI et la règle sur extérieur aperçu
   J'ai passé par CallCommand car si je passe par BaseObject le ciel n'éclaire pas la m^ême chose
   malgré tous les paramètres identiques ! """

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN =1026473

def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])

# Main function
def main():
    rd = doc.GetActiveRenderData()
    
    #on vérifie si il y a déjà la GI
    vp = rd.GetFirstVideoPost()
    while vp:
        if vp.GetType() == c4d.VPglobalillumination:
            break
        vp = vp.GetNext()
    if not vp :
        vp = c4d.documents.BaseVideoPost(c4d.VPglobalillumination)
        rd.InsertVideoPostLast(vp)
    else:
        #si la gi est présente on l'active'
        vp.SetAllBits(c4d.BIT_ACTIVE)
    
    vp[c4d.GI_SETUP_DATA_PRESETS] = 6220 #Preset Exterior Preview
    
    c4d.CallCommand(1011145) # Physical Sky
    sky = doc.GetFirstObject()
    #Ophysicalsky = 1011146
    
    
    # Parse the time string
    dt = datetime.strptime('21.06.2022 09:00:00',"%d.%m.%Y %H:%M:%S")
    dtd = sky[c4d.SKY_DATE_TIME]

    # Fills the Data object with the DateTime object
    dtd.SetDateTime(dt)
    sky[c4d.SKY_DATE_TIME] = dtd
    
    #sky = c4d.BaseObject(Ophysicalsky)
    sky[c4d.SKY_MATERIAL_GLOBALILLUM_GENERATE] = True
    
    origin = doc[CONTAINER_ORIGIN]
    
    lon,lat = lv95towgs84(origin.x,origin.z)
    
    sky[c4d.SKY_POS_LATITUDE] = c4d.utils.Rad(lat)
    sky[c4d.SKY_POS_LONGITUDE] = c4d.utils.Rad(lon)
    c4d.EventAdd()
    
    return
    origin = doc[CONTAINER_ORIGIN]
    
    lon,lat = lv95towgs84(origin.x,origin.z)
    
    
    print(c4d.utils.Rad(lat),c4d.utils.Rad(lon))

    sky = op
    
    print(sky[c4d.SKY_POS_LATITUDE],sky[c4d.SKY_POS_LONGITUDE])
    
    sky[c4d.SKY_POS_LATITUDE] = c4d.utils.Rad(lat)
    sky[c4d.SKY_POS_LONGITUDE] = c4d.utils.Rad(lon)
    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()