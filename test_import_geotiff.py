import c4d,os
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    fn = '/Users/olivierdonze/Documents/TEMP/Saint_cergue/ch.swisstopo.swissalti3d-L1nVhM3j_tif/swissalti3d_2021_2503-1146_2_2056_5728.tif'

    filename,ext = os.path.splitext(os.path.basename(fn))
    produit,annee,coord,val_px,epsg,inconnu = (filename.split('_'))
    x,y =[float(val)*1000 for val in coord.split('-')]
    print (x,'-',y)
    #left=2503000.0, bottom=1146000.0, right=2504000.0, top=1147000.0
    #les dalles font 1000m x 1000m (500 px pour le mnt2m et 2000 px pour le mnt 50cm)
    #ATTENTION pour le mnt le point est au centre du pixel et pas au bord de l'image !
    #donc le mnt fait un pixel de moins en largeur et hauteur
    #il faut trouver un truc pour "couturer" les dalles !
    
    return

    taille_px = 2
    bmp = c4d.bitmaps.BaseBitmap()
    bmp.InitWith(fn)
    width,height = bmp.GetSize()

    nb_pts = width*height
    nb_polys = (width-1)*(height-1)
    res = c4d.PolygonObject(nb_pts,nb_polys)
    phong_tag = c4d.BaseTag(c4d.Tphong)
    phong_tag[c4d.PHONGTAG_PHONG_ANGLELIMIT] = True

    res.InsertTag(phong_tag)


    pos = c4d.Vector(0,0,0)
    pts = []
    id_pt = 0
    id_poly = 0
    for i in range(height):
        for n in range(width):
            #il faut diviser la valeur par 255 pour avoir la vrie valeur d'altitude!!!!
            pos.y = (bmp.GetPixelDirect(n,i)/255.).x
            pts.append(c4d.Vector(pos))
            if i>0 and n>0:
                res.SetPolygon(id_poly,c4d.CPolygon(id_pt,id_pt-1,id_pt-width-1,id_pt-width))
                id_poly+=1
            id_pt+=1
            pos.x+= taille_px
        pos.x = 0
        pos.z-=taille_px

    res.SetAllPoints(pts)
    res.Message(c4d.MSG_UPDATE)

    doc.StartUndo()

    doc.InsertObject(res)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,res)
    c4d.EventAdd()
    doc.EndUndo()



# Execute main()
if __name__=='__main__':
    main()