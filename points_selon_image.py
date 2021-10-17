import c4d, os

#ATTENTION FONCTIONNE AVEC LE CANAL ALPHA


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


DISTANCE_PLANTATION = 4


def getCalage(fn):
    f,ext = os.path.splitext(fn)
        
    #fichier .wld
    if os.path.isfile(f+'.wld'):
        return f+'.wld'
    
    #fichier type tfw
    ext_calage = f'.{ext[1]}{ext[-1]}w'
    if os.path.isfile(f+ext_calage):
        return f+ext_calage
    
    return None

# Main function
def main():
    fn ='/Users/olivierdonze/Documents/Mandats/Cite_des_metiers_2021/C4D/Maquette PAV/tex/plantations.png'
    
    dirname = os.path.dirname(fn)
    
    #on regarde s'il y a un fichier de calage
    fn_calage = getCalage(fn)
    val_px = 0
    
    if not fn_calage:
        rep = c4d.gui.QuestionDialog("Il n'y a pas de fichier de calage, voulez-vous continuer ?")
        if not rep : return
        while not val_px:
            rep = c4d.gui.InputDialog("Rentrez la valeur d'un pixel en mètre :", '')
            try :
                val_px = float(rep)
            except: pass
            if not rep : return
    
    else:
        #pour l'instant on prend que la valeur du pixel (1ère ligne)
        with open(fn_calage) as f :
            try :
                val_px = float(f.readline())
                #print(val_px)
            except:
                c4d.gui.MessageDialog("Problème de lecture du fichier de calage")
                return

    
    bmp = c4d.bitmaps.BaseBitmap()
    result, isMovie = bmp.InitWith(fn)
    if result != c4d.IMAGERESULT_OK:
        c4d.gui.MessageDialog("Problème de lecture de l'image")
        return
    
    x, y = bmp.GetSize()
    #print(x,y)
    larg = (x)*val_px
    haut = (y)*val_px
    
    nb_px_x = int(round(larg/DISTANCE_PLANTATION))
    nb_px_y = int(round(haut/DISTANCE_PLANTATION))
    
    val_px_x = larg/(nb_px_x)
    val_px_y = haut/(nb_px_y)
    
    #print(nb_px_x,nb_px_y)
    #print(bmp.GetChannelCount())
    dpth = bmp.GetBt()
    bmp_plant = c4d.bitmaps.BaseBitmap()
    bmp_plant.Init(nb_px_x, nb_px_y, depth=dpth, flags=c4d.INITBITMAPFLAGS_NONE)
    
    bmp.ScaleIt(bmp_plant, 256, sample=False, nprop= True)
    #f,ext = os.path.splitext(fn) 
    #bmp_plant.Save(f+'-test'+ext, format=c4d.FILTER_PNG, data=None, savebits=c4d.SAVEBIT_ALPHA)
    alpha_channel = bmp_plant.GetInternalChannel()
    pos = c4d.Vector(0)
    pts = []
    for i in range(nb_px_y):
        for n in range(nb_px_x):
            if bmp_plant.GetAlphaPixel( alpha_channel, n, i):
                pts.append(c4d.Vector(pos))
            pos.x += val_px_x
        
        pos.x =0
        pos.z -= val_px_y
    res = c4d.PolygonObject(len(pts),0)
    res.SetAllPoints(pts)
    res.Message(c4d.MSG_UPDATE)
    doc.InsertObject(res)
    c4d.EventAdd()
        
    
    

# Execute main()
if __name__=='__main__':
    main()