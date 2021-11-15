import c4d,os

""" Attention le nom des image doit contenir l'échelle précédée d'un '_' à la fin du nom
    type : nom_image_1000.jpg
    
    Ne pas oublier de régler la résolution des images, qui doivent toutes avoir la même"""

from glob import glob
#from PIL import Image
#########################################################
# A ADAPTER  A ADAPTER  A ADAPTER  A ADAPTER 
RES = 300 #resolution de l'image'

def matFromImg(fn, relatif = False):
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    mat.SetName( os.path.basename(fn))
    shd = c4d.BaseList2D(c4d.Xbitmap)
    if relatif:
        shd[c4d.BITMAPSHADER_FILENAME] = os.path.basename(fn)
    else :
        shd[c4d.BITMAPSHADER_FILENAME] = fn
        
    mat[c4d.MATERIAL_COLOR_SHADER] = shd
    mat.InsertShader(shd)
    mat[c4d.MATERIAL_PREVIEWSIZE] = c4d.MATERIAL_PREVIEWSIZE_NO_SCALE
    mat.Message(c4d.MSG_UPDATE)
    mat.Update(True, True)
    return mat

def tagTex(obj,mat):
    tag = c4d.TextureTag()
    tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW
    tag.SetMaterial(mat)
    obj.InsertTag(tag)
    
def tagDisplay(obj):
    tag = c4d.BaseTag(c4d.Tdisplay)
    tag[c4d.DISPLAYTAG_AFFECT_DISPLAYMODE] = True
    tag[c4d.DISPLAYTAG_SDISPLAYMODE] = c4d.DISPLAYTAG_SDISPLAY_FLAT
    obj.InsertTag(tag)

def main():
    
    path = "/Users/donzeo/Documents/Cours/Cinema4D_niv2_2018/exos/pavillon_barcelone/tex"
    path = '/Users/olivierdonze/switchdrive/Mandats/Versoix chemin Val-de-Travers/tex'
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(os.path.basename(path))
    doc.StartUndo()
    pos = c4d.Vector()
    
    for fn in glob(path+'/*.png'):
        
        #extraction de l'échelle  de ce type ......_1000.jpg'
        scale = None
        try : 
            scale = int(os.path.splitext(fn)[0].split('_')[-1])
        except:
            print ("problème d'extraction d'échelle avec le fichier %s "%os.path.basename(fn))
            
        if not scale:
            continue
        bmp = c4d.bitmaps.BaseBitmap()
        bmp.InitWith(fn)
        width, height = bmp.GetSize()
        larg = width/float(RES) *2.54 * scale /100
        haut = height/float(RES) *2.54 * scale /100
        pos.x+= larg/2.
        plane = c4d.BaseObject(c4d.Oplane)
        plane[c4d.PRIM_PLANE_WIDTH] = larg
        plane[c4d.PRIM_PLANE_HEIGHT] = haut
        plane[c4d.PRIM_PLANE_SUBW] = 1
        plane[c4d.PRIM_PLANE_SUBH] = 1
        
        plane.SetRelPos(pos)
        
        plane.SetName(os.path.basename(fn))
        plane.InsertUnderLast(res)
        pos.x += larg/2.
        
        mat = matFromImg(fn,relatif = True)
        doc.InsertMaterial(mat)
        doc.AddUndo(c4d.UNDOTYPE_NEW,mat)
        
        tagTex(plane,mat)
        tagDisplay(plane)
    doc.InsertObject(res)
    doc.AddUndo(c4d.UNDOTYPE_NEW,res)
    doc.EndUndo()
    c4d.EventAdd()
    
if __name__=='__main__':
    main()
