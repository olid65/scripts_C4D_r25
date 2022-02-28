import c4d
import re
import os.path
from os import listdir
from os.path import isfile, join, basename
from pprint import pprint

import sys


sys.path.append(os.path.dirname(__file__))
import png


DIC_TYPES = {'top':['top','haut','plan','carte'],
             'front':['coupe','elevation','face','profil','section','front','avant'],
             'right':['right', 'droite'],
             'left':['left', 'gauche'],
             'back':['back', 'arriere'],
             'bottom':['bottom','dessous'],
             'perspective':['perspective','vue','pers','croquis','dessin'],
             }

EXTENSIONS = ['.jpg','.png','.psd','.tif']

CODE_SCALE = 'ech' #example ech1000 -> 1/1000

CODE_RESOLUTION = 'dpi' #example 300dpi

DEFAULT_PROJECTION = 'top'
DEFAULT_SCALE = 500
DEFAULT_RESOLUTION = 72

#si jamais il y a le module unidecode
#qui fait ça très bien, mais il faut l'installer !
#unidecode.unidecode(texte_unicode)
def suppr_accents(txt):
    dico = { 'éèêẽ' : 'e',
             'ç'    : 'c',
             'àâãä' : 'a',
             'ù'    : 'u',
            }
    res = ''
    for car in txt:
        for k in dico:
            if car in k:
                car = dico[k]
                break
        res += car

    return res

def get_image_files(pth):
    """renvoie une liste des fichiers dont l'extension est
       présente dans la constante EXTENSIONS"""
    res = []

    for f in listdir(pth):
        if isfile(join(pth, f)):
            if f[-4:] in EXTENSIONS:
                res.append(f)

    return res

def get_info_from_fn(fn):
    """renvoie projection,scale,resolution contenu dans le nom,
       si pas trouvé renvoie une valeur None pour chaque paramètre.
       projection -> selon liste de valeurs de DIC_TYPES
       resolution -> integer d'après série de chiffre après CODE_SCALE
       scale -> integer d'après série de chiffre avant CODE_RESOLUTION
       """
    txt = basename(fn)

    #suppression des accents
    txt = suppr_accents(txt)

    #type de projection
    projection = None
    for k,lst in DIC_TYPES.items():
        for name in lst:
            if name in txt :
                projection = k

    #extraction de l'échelle par ex ECH500 ech500 éch500 ...'
    scale = None
    p = re.compile(f'{CODE_SCALE}[0-9,/,]+', re.IGNORECASE)
    req = re.search(p,txt)
    if req:
        try : scale = int(req.group()[len(CODE_SCALE):])
        except:
            print(f"problème avec scale : {txt}")

    #extraction de la résolution par ex 220dpi 300DPI
    p2 = re.compile(f'[0-9]+{CODE_RESOLUTION}', re.IGNORECASE)

    resolution = None
    req = re.search(p2,txt)
    if req:
        try : resolution=int(req.group()[:-len(CODE_RESOLUTION)])
        except:
            print(f"problème avec resolution : {txt}")

    return projection,scale,resolution

def creer_mat(fn, alpha = False):
    nom = basename(fn)
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    mat.SetName(nom)
    shd = c4d.BaseList2D(c4d.Xbitmap)
    shd[c4d.BITMAPSHADER_FILENAME] = fn
    mat[c4d.MATERIAL_COLOR_SHADER] = shd
    mat[c4d.MATERIAL_USE_REFLECTION] = False
    mat[c4d.MATERIAL_COLOR_MODEL] = c4d.MATERIAL_COLOR_MODEL_ORENNAYAR
    mat.InsertShader(shd)
    mat[c4d.MATERIAL_USE_SPECULAR]=False

    #on teste si il y a une couche alpha
    #le jpg ne peut pas contenir d'alpha'
    if fn[:-4] != '.jpg':
        bmp = c4d.bitmaps.BaseBitmap()

        result, isMovie = bmp.InitWith(fn)
        if result == c4d.IMAGERESULT_OK: #int check

            if bmp.GetInternalChannel(): alpha = True
        bmp.FlushAll()

    if alpha :
        mat[c4d.MATERIAL_USE_ALPHA]=True
        shda = c4d.BaseList2D(c4d.Xbitmap)
        shda[c4d.BITMAPSHADER_FILENAME] = fn
        mat[c4d.MATERIAL_ALPHA_SHADER]=shda
        mat.InsertShader(shda)

    mat.Message(c4d.MSG_UPDATE)
    mat.Update(True, True)
    return mat


def creer_plan(nom,mat,width,height, projection):
    plan = c4d.BaseObject(c4d.Oplane)
    plan.SetName(nom)
    plan[c4d.PRIM_PLANE_WIDTH]=width
    plan[c4d.PRIM_PLANE_HEIGHT]=height
    plan[c4d.PRIM_PLANE_SUBW]=1
    plan[c4d.PRIM_PLANE_SUBH]=1

    DIC_TYPES = {'top':['top','haut','plan','carte'],
                 'front':['coupe','elevation','face','profil','section','front','avant'],
                 'right':['right', 'droite'],
                 'left':['left', 'gauche'],
                 'back':['back', 'arriere'],
                 'bottom':['bottom','dessous'],
                 'perspective':['perspective','vue','pers','croquis','dessin'],
                 }
    if projection == 'top':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_YP
    elif projection == 'front':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_ZP
    elif projection == 'right':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_XP
    elif projection == 'left':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_XN
    elif projection == 'back':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_ZN
    elif projection == 'bottom':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_YN
    elif projection == 'perspective':
        plan[c4d.PRIM_AXIS]=c4d.PRIM_AXIS_XN
    tag = c4d.TextureTag()
    tag.SetMaterial(mat)
    tag[c4d.TEXTURETAG_PROJECTION]=c4d.TEXTURETAG_PROJECTION_UVW
    plan.InsertTag(tag)

    return plan #doc.InsertObject(plan)

def png_get_size_in_meter(fn_png):
    """ renvoie la taille en mètres d'un fichier png ou None si pas trouvé
        attention il n'y a pas toujours l'info 'physical' en général si on
        réenregistre l'image sous dans psd cela fonctionne
        attention2 : utilise la lib png (un seul fichier png.py)"""
    with open(fn_png,'rb') as f:
        r=png.Reader(file=f)
        width,height,rows,info = r.read()
        alpha = info.get('alpha',-1)
        resol = info.get('physical',None)
        if resol:
            #print(resol.unit_is_meter)
            if resol.unit_is_meter:
                #dimensions en mètres
                largeur = width/resol.x
                hauteur = height/resol.y
            else:
                # à tester avec un exemple
                # j'ai supposé que cela donne des pouces -> /2.54'
                largeur = width/resol.x/2.54
                hauteur = height/resol.y/2.54
            return largeur,hauteur, alpha
    return None

# Main function
def main():
    fn = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/c4d/tex/Schema_Laurence.png'
    fn = '/Users/olivierdonze/Documents/TEMP/Schema_Laurence.png'
    #fn = '/Users/olivierdonze/Documents/TEMP/jpegrgb_dissected.png'

    pth = '/Users/olivierdonze/switchdrive/Mandats/Versoix chemin Val-de-Travers/tex'
    pth = '/Users/olivierdonze/switchdrive/Mandats/Parc_naturel_regional_vallee_Trient/c4d/tex'
    #pth = '/Volumes/My Passport Pro/PAV_projet_fed_2019/BACHELOR/PLAN_MASSES_GEOREF/PAV_2019_BACHELOR_PLAN_MASSES_GEOREF'


    files_img = get_image_files(pth)
    doc.StartUndo()
    for fn in files_img:
        fn = join(pth,fn)
        largeur,hauteur = 0,0

        alpha = -1

        # si c'est un png on essaie de récupèrer directement la taille via la lib png
        if fn[-4:]=='.png':
            print(os.path.basename(fn))
            largeur,hauteur, alpha = png_get_size_in_meter(fn)
        print(largeur,hauteur)
        #récupération des différentes valeurs depuis le nom
        projection,scale,resolution = get_info_from_fn(fn)
        print(projection,scale,resolution)
        #valeurs par defaut si pas renseigné
        if not projection : projection= DEFAULT_PROJECTION
        if not scale : scale = DEFAULT_SCALE
        if not resolution : resolution = DEFAULT_RESOLUTION
        print(projection,scale,resolution)
        # si on n'a pas réussi à récupérer ces valeurs
        # on utilise BaseBitmap
        if not largeur or not hauteur or alpha==-1:
            bmp = c4d.bitmaps.BaseBitmap()

            result, isMovie = bmp.InitWith(fn)
            if result == c4d.IMAGERESULT_OK: #int check
                width,height = bmp.GetSize()
                #TODO -> voir dans quelles unité on est par rapport au doc !!!
                if not largeur or not hauteur:
                    largeur = width / resolution * scale/2.54
                    hauteur = height/ resolution * scale/2.54
                else:
                    largeur *=scale
                    hauteur *=scale

                #on regarde s'il y a une couche alpha'
                if bmp.GetInternalChannel():
                    alpha = True
                else:
                    alpha = None

            else:
                print(f'problème de lecture de fichier  : {basename(fn)}')


            print('----')
            bmp.FlushAll()

        mat = creer_mat(fn, alpha)
        doc.InsertMaterial(mat)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,mat)

        nom = basename(fn)
        plan = creer_plan(nom,mat,largeur,hauteur,projection)
        doc.InsertObject(plan)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,plan)





    doc.EndUndo()
    c4d.EventAdd()



# Execute main()
if __name__=='__main__':
    main()