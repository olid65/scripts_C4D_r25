import c4d
import os, re


#importe un fichier .asc sous forme de points seulement
#les nodata ne sont pas importés
#un tag Vertex color est ajoutés pour fair afficher les points
#et on peut classer selon les valeurs en y de chaque point (à faire avant via gdal)

FORET = 100
FORET_CLAIRSEMEE = 50
FORET_BUISSONNANTE = 10




# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    
    fn = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/test_foret_10m.asc'
    name = os.path.basename(fn).split('.')[0]

    nb = 0
    header = {}
    # lecture de l'entête pour savoir si on a 5 ou 6 lignes ( il y a des fichiers qui n'ont pas la ligne nodata)
    # ou encore 7 lignes commes qgis avec valeurs différentes pour dx, dy
    with open(fn, 'r') as file:
        virgule = False
        while 1:
            s = file.readline()
            split = s.split()
            # si la première partie de split commence par un chiffre ou par le signe moins on break
            if re.match(r'^[0-9]', split[0]) or re.match(r'^-', split[0]): break
            k, v = split
            # si on a une virgule dans v c'est que le fichier est en virgule
            # ça arrive quand les paramètres régionaux de Windows ont , comme cararctère décimal
            if v.find(","):
                virgule = True

            if virgule:
                v = v.replace(",", ".")

            header[k.lower()] = v  # QGIS met le NODATA_value en partie en majuscule !!!
            nb += 1

    ncols = int(header['ncols'])
    nrows = int(header['nrows'])
    xcorner = float(header['xllcorner'].replace(',','.'))
    ycorner = float(header['yllcorner'].replace(',','.'))

    # on teste si on a une valeur cellsize
    if header.get('cellsize', None):
        cellsize = float(header['cellsize'].replace(',','.'))
        dx = cellsize
        dy = cellsize
    # sinon on récupère dx et dy
    else:
        dx = float(header['dx'].replace(',','.'))
        dy = float(header['dy'].replace(',','.'))

    nodata = 0.
    if nb == 6 or nb == 7:
        try:
            nodata = float(header['nodata_value'].replace(',','.'))
        except:
            nodata = 0.
    

    # lecture des altitudes
    with open(fn, 'r') as file:
        # on saute l'entête
        for i in range(nb): file.readline()

        #nb_pts = ncols * nrows
        #nb_poly = (ncols - 1) * (nrows - 1)
        #poly = c4d.PolygonObject(nb_pts, nb_poly)
        #poly.SetName(name)
        origine = c4d.Vector(xcorner, 0, ycorner + nrows * dy)
        pts = []

        pos = c4d.Vector(0)
        i = 0
        for r in range(nrows):
            for val in file.readline().split():
                if virgule:
                    val = val.replace(",", ".")

                y = float(val)
                if y != nodata: 
                    pts.append(c4d.Vector(pos.x,y,pos.z))
                pos.y = y
                #poly.SetPoint(i, pos)
                pos.x += dx
                i += 1
            pos.x = 0
            pos.z -= dy
        
    if pts :
        tag = c4d.VertexColorTag(len(pts))
        tag[c4d.ID_VERTEXCOLOR_DRAWPOINTS] =True
        
        data = tag.GetDataAddressW()
        color = c4d.Vector4d(1.0, 1.0, 1.0, 1.0)

        for idx in range(len(pts)):
            p = pts[idx]
            
            #couleurs des points selon la valeur y
            if p.y ==FORET_BUISSONNANTE:
                color = c4d.Vector4d(1.0, 0, 0, 1.0)
            elif p.y ==FORET_CLAIRSEMEE:
                color = c4d.Vector4d(0, 1.0, 0, 1.0)
            elif p.y ==FORET:
                color = c4d.Vector4d(0, 0, 1.0, 1.0)
        
                
            c4d.VertexColorTag.SetPoint(data, None, None, idx, color)
        
        res = c4d.PolygonObject(len(pts),0)
        res.InsertTag(tag)
        res.SetName(name)
        res.SetAllPoints(pts)
        res.Message(c4d.MSG_UPDATE)
        doc.InsertObject(res)
        c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()