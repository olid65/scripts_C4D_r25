import c4d
import os

TIFF  = 1100
TGA   = 1101
JPEG  = 1104
PSD   = 1106

dic_format = { TIFF: '.tif',
               TGA : '.tga',
               JPEG: '.jpg',
               PSD : '.psd'}

CONTAINER_ORIGIN =1026473 

def nomFichierCalage(fn_img):
    return fn_img[:-2]+fn_img[-1]+'w'

def writeWorldFile(val_px,coord_x,coord_y,img_name):
    """cree un fichier de calage pour une image et renvoie le nom complet du fichier cree"""
    fn = nomFichierCalage(img_name)
    with open(fn,'w') as file :
        file.write(str(val_px)+'\n')
        file.write('0.0000000000\n') #rotation sur les lignes : a voir si possible/besoin implementer
        file.write('0.0000000000\n') #rotation sur les colonnes idem
        file.write(str(-val_px)+'\n')
        file.write(str(coord_x)+'\n')
        file.write(str(coord_y)+'\n')
    file.closed
    
    return fn

def main():
    #renvoie la vue du rendu
    bd = doc.GetRenderBaseDraw()
    
    #parametres de la vue
    param = bd.GetViewParameter()

    #calcul du centre de l'image
    centre = bd.SW(param['offset']) #conversion ecran->monde
    scale = param['scale']
    
    #renvoie la partie de la vue qui sera rendue
    position = bd.GetSafeFrame()
    #print position["cl"], position["ct"], position["cr"], position["cb"]
    
    #calcul de la largeur et de la hauteur
    largeur = (position["cr"] - position["cl"])/scale.x
    hauteur = (position["cb"] - position["ct"])/-(scale.y)
    
    #recuperation de la taille en pixels de l'image rendue
    rd = doc.GetActiveRenderData()
    larg_px = rd[c4d.RDATA_XRES_VIRTUAL]
    haut_px = rd[c4d.RDATA_YRES_VIRTUAL]
    resol = rd[c4d.RDATA_PIXELRESOLUTION_VIRTUAL]
    
    #calcul de la valeur du pixel
    val_px = float(largeur)/larg_px
    
    #calcul du point haut gauche
    origine = doc[CONTAINER_ORIGIN]
    if not origine : 
        c4d.gui.MessageDialog("Ce document n'est pas géoréférencé le calge de l'image n'est pas possible")
        return
    coord_x = centre.x-largeur/2+origine.x
    coord_y = centre.z+hauteur/2+origine.z
    
    #chemin de l'image rendue ou a rendre
    if not rd[c4d.RDATA_PATH] : 
        c4d.gui.MessageDialog("Vous devez indiquer un nom d'image et chemin d'accès dans les préférences de rendu")
        return

    fn_img = rd[c4d.RDATA_PATH] + dic_format[rd[c4d.RDATA_FORMAT]]
    
    #ecriture du fichier de calage
    writeWorldFile(val_px,coord_x,coord_y,fn_img)
    
    #conversion en cm
    larg_cm = larg_px/resol *2.54
    haut_cm = haut_px/resol *2.54
    

    
    #calcul de l'echelle de l'image
    data = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = data.GetUnitScale()
    echelle = None
    
    if unit == c4d.DOCUMENT_UNIT_M:
        echelle = larg_cm/100 * largeur
    if unit == c4d.DOCUMENT_UNIT_CM:
        echelle = larg_cm* largeur
    print ('echelle 1:',echelle)
    
    
    
    
    
if __name__=='__main__':
    main()
