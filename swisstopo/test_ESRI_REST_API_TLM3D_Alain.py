import c4d
import json
import urllib.request, urllib.error, urllib.parse


CONTAINER_ORIGIN = 1026473

ID_LYR_ARBRES_ISOLES = 0
ID_LYR_COUV_SOL = 1



# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True



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

def createSpline(pts,segments, name):
    pcnt = len(pts)
    sp = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
    sp[c4d.SPLINEOBJECT_CLOSED] = True
    sp.SetAllPoints(pts)
    sp.SetName(name)
    
    #ajout des segments s'il y en a plus que 1
    if len(segments)>1:
        sp.ResizeObject(pcnt, len(segments))
        for i,cnt in enumerate(segments):
            sp.SetSegment(i,cnt,closed = True)
    sp.Message(c4d.MSG_UPDATE)
    return sp


# Main function
def main():

    origine = doc[CONTAINER_ORIGIN]
    xmin,ymin,xmax,ymax = 2567370.0,1107818.0,2571388.0,1109930.0

    url_base = 'https://hepiadata.hesge.ch/arcgis/rest/services/suisse/TLM_C4D_couverture_sol/FeatureServer'
    
    #arbres isoles
    lyr_arbres_isoles = f'/{ID_LYR_ARBRES_ISOLES}/'
    query = f'query?geometry={xmin},{ymin},{xmax},{ymax}&returnZ=true&geometryType=esriGeometryEnvelope&f=json'

    url_arbres_isoles = url_base+lyr_arbres_isoles+query

    data = get_json_from_url(url_arbres_isoles)

    pts = []
    for feat in data['features']:
        geom = feat['geometry']

        pts.append(c4d.Vector(geom['x'],geom['z'],geom['y'])-origine)

    polyo = c4d.PolygonObject(len(pts),0)
    polyo.SetName('arbres_isoles_swisstopo')
    polyo.SetAllPoints(pts)
    polyo.Message(c4d.MSG_UPDATE)
    doc.InsertObject(polyo)
    

    #couverture du sol
    
    #catégories dans le champ OBJEKTART que l'on récupère'
    categories ={'Gebueschwald':'Forêt buissonnante',
                 'Wald':'Forêt',
                 'Wald%20offen': 'Forêt claisemée',
                 'Gehoelzflaeche':'Zone boisée',
                 }
                 
    #categories ={'Wald':'Forêt',
                 #'Wald offen': 'Forêt claisemée',}
                 
    lyr_couv_sol = f'/{ID_LYR_COUV_SOL}/'
    
    res = c4d.BaseObject(c4d.Onull)
    res.SetName('couverture_sol')
    
    sql = ''
    
    for i,cat in enumerate(categories.keys()):
        
        if i>0 :
            sql+=' OR '
        
        sql+=f"OBJEKTART='{cat}'"
        
    #urllib.parse.quote sert à remplacer les caractère spéciaux par le code ascii
    #on doit passer par ça notamment pour les espaces !
    print(sql)
    sql= urllib.parse.quote(sql)
    
    
    query = f"query?geometry={xmin},{ymin},{xmax},{ymax}&returnZ=true&outFields=OBJEKTART&orderByFields=OBJEKTART&where={sql}&geometryType=esriGeometryEnvelope&f=json"
    
    url_couv_sol = url_base+lyr_couv_sol+query
    
    #url_couv_sol = urllib.parse.urlencode(url_couv_sol, quote_via=urllib.parse.quote)

    print(url_couv_sol)


    data = get_json_from_url(url_couv_sol)
    if not data:
        print('pas de data')
        return
    
    #stockage du nombre de points par segement
    segments = []
    pts = []
    cat = None
    
    for feat in data['features']:
        if not cat :
            cat = feat['attributes']['objektart']
            
        #vu que lq requête trie par OBJEKTART
        #si la catégorie change on crée la spline
        #et on efface les listes
        if cat!= feat['attributes']['objektart']:
            sp = createSpline(pts,segments, name = categories[cat])
            sp.InsertUnderLast(res)
            
            #on vide les listes
            pts.clear()
            segments.clear()           
            cat = feat['attributes']['objektart']
   
        geom = feat['geometry']
        for ring in geom['rings']:
            for i,(x,y,z) in enumerate(ring):
                #ATTENTION JE N'AI PAS UTILISE LE Z POUR POUVOIR DECOUPER LES SPLINES ENSUITE
                pts.append(c4d.Vector(x,0,y)-origine)
            segments.append(i+1)
    
    sp = createSpline(pts,segments,name = categories[cat])
    sp.InsertUnderLast(res)
    
    doc.InsertObject(res)
    c4d.EventAdd()
    return
            
    pcnt = len(pts)
    if pcnt:
        sp = c4d.SplineObject(pcnt,c4d.SPLINETYPE_LINEAR)
        sp[c4d.SPLINEOBJECT_CLOSED] = True
        sp.SetAllPoints(pts)
        sp.SetName(categories[cat])
        
        #ajout des segements s'il y en a plus que 1
        if len(segments)>1:
            sp.ResizeObject(pcnt, len(segments))
            for i,cnt in enumerate(segments):
                sp.SetSegment(i,cnt,closed = True)
        sp.Message(c4d.MSG_UPDATE)
        sp.InsertUnderLast(res)
    doc.InsertObject(res)
    c4d.EventAdd()

    return



# Execute main()
if __name__=='__main__':
    main()