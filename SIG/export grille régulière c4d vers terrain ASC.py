import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# ATTENTION la grille doit être régulière (TODO vérifier que c'est le cas)
# toutes les case doivent avoir la même taille en x et/ou z
# on peut différencier la taille x et z

CONTAINER_ORIGIN = 1026473

# Main function
def main():
    origine = doc[CONTAINER_ORIGIN]
    if not origine:
        origine = c4d.Vector(0)

    fn = '/Users/olivierdonze/Documents/TEMP/test_export.asc'
    #On met les points dans l'ordre du MNT ASCCI
    #le point le plus en haut à gauche en premier
    #puis on avance de la taille de cellule en x

    #on récupère les points sous forme de tuple et
    #on inverse le sens : -z,x,p pour le tri ensuite
    # - z pour que cela aille du nord vers le sud
    mg = op.GetMg()
    p_global = lambda v : v*mg+ origine
    pts = map(p_global,op.GetAllPoints())
    pts = [(-p.z,p.x,p.y) for p in pts]
    pts.sort()
    #on remet dans le bon sens les vecteurs
    new_pts = [c4d.Vector(x,y,-z) for z,x,y in pts]

    #new = c4d.PolygonObject(len(new_pts),0)
    #new.SetAllPoints(new_pts)
    #new.Message(c4d.MSG_UPDATE)
    #doc.InsertObject(new)
    #pos = new.GetAbsPos()
    #pos-= origine
    #new.SetAbsPos(pos)
    #c4d.EventAdd()


    #la taille de la maille en x correspond à la différence en x
    #entre les deux premiers points
    cellsize_x = new_pts[1].x-new_pts[0].x
    cellsize_z = 0
    ncols = 0

    p_pred = new_pts[0]

    #pour le nombre de colonne quand les points
    #n'ont plus le m^ême x on peut reprendre le nombre
    #et le delta z
    for i,p in enumerate(new_pts[1:]):
        if p.x - p_pred.x != cellsize_x:
            ncols = i+1
            cellsize_z = p.z-p_pred.z
            break
        p_pred = p

    #pour le nombre de ligne on divise le nombre de points
    #par le nombre de colonnes
    nrows = int(len(new_pts)/ncols)
    ncols = int(ncols)

    #le premier point est en haut à droite
    # et la ref en bas à gauche
    corner = new_pts[0]
    xllcorner = corner.x - cellsize_x/2
    corner = new_pts[-1]
    yllcorner = corner.z + cellsize_z/2

    #TODO : vérifier que la grille soit bien régulière

    nodata = -9999
    #écriture du fichier ascii
    lines = [
                f'ncols        {ncols}\n',
                f'nrows        {nrows}\n',
                f'xllcorner    {xllcorner}\n',
                f'yllcorner    {yllcorner}\n']

    if cellsize_x == abs(cellsize_z):
        lines.append(f'cellsize     {cellsize_x}\n')
    else:
        lines.append(f'dx           {cellsize_x}\n')
        lines.append(f'dy           {cellsize_z}\n')
    lines.append(f'NODATA_value {nodata}\n')


    for i,p in enumerate(new_pts):
        lines.append(f'{p.y} ')
        if not (i+1) % ncols:
            lines.append(f'\n')

    with open(fn,'w') as f:
        f.writelines(lines)




    return
    emprise = op.GetRad()*2
    largeur = emprise.x
    hauteur = emprise.z

    taille_maille = op.GetPoint(1)-op.GetPoint(0)
    if taille_maille.x :
        taille_maille = taille_maille.x
    else:
        taille_maille = taille_maille.z

    nb_cols = 0






# Execute main()
if __name__=='__main__':
    main()