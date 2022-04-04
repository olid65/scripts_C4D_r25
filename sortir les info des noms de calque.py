import c4d
import re
import os

# localimport-v1.7.3-blob-mcw79
import base64 as b, types as t, zlib as z; m=t.ModuleType('localimport');
m.__file__ = __file__; blob=b'\
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\
XVw='
exec(z.decompress(b.b64decode(blob)), vars(m)); _localimport=m;localimport=getattr(m,"localimport")
del blob, b, t, z, m;


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

NAMES_MNT = ['mnt','swissalti3d', 'terrain']

PREFIXE_HAUTEUR = 'h'
PREFIXE_DIST = 'dist'
PREFIXE_DENSITE = 'dens'
PREFIXE_LARGEUR = 'larg' #(largeur de cordon)

#dans re le ? sert à dire que le caractère qui précède est facultatif
CATEGORIES = [r'arbres?',
              r'arbres?-surfaces?',
              r'arbres?-alignements?',
              r'arbres?-cordons?',
              r'constructions?']

DELTA_ALT = 100

def getMinMaxY(obj):
    """renvoie le minY et le maxY en valeur du monde d'un objet"""
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT

def pointsOnSurface(op,mnt):
    grc = c4d.utils.GeRayCollider()
    grc.Init(mnt)

    mg_op = op.GetMg()
    mg_mnt = mnt.GetMg()
    invmg_mnt = ~mg_mnt
    invmg_op = ~op.GetMg()

    minY,maxY = getMinMaxY(mnt)

    ray_dir = ((c4d.Vector(0,0,0)*invmg_mnt) - (c4d.Vector(0,1,0)*invmg_mnt)).GetNormalized()
    length = maxY-minY
    for i,p in enumerate(op.GetAllPoints()):
        p = p*mg_op
        dprt = c4d.Vector(p.x,maxY,p.z)*invmg_mnt
        intersect = grc.Intersect(dprt,ray_dir,length)
        if intersect :
            pos = grc.GetNearestIntersection()['hitpos']
            op.SetPoint(i,pos*mg_mnt*invmg_op)

    op.Message(c4d.MSG_UPDATE)

def isCircle(obj, nb_pts_min = 5, tolerance = 0.001):

    #objet point
    if not obj.CheckType(c4d.Opoint) : return False

    #points minimum
    if obj.GetPointCount()<nb_pts_min : return False

    #distances au carré (plus rapide à calculer)
    squared_lengthes = [p.GetLengthSquared() for p in obj.GetAllPoints()]
    #différence entre le maxi et le mini
    dif = max(squared_lengthes)-min(squared_lengthes)

    if dif>tolerance : return False

    return True

def getInfo(txt,prefixe):
    """renvoie une liste à une ou deux valeurs"""
    p = re.compile(f'{prefixe}[0-9,/,]+', re.IGNORECASE)
    req = re.search(p,txt)
    if req:
        return [abs(float(s)) for s in re.findall(r'-?\d+\.?\d*', txt)]
    return None

def arbres_isoles(parent,mnt):
    #liste des cercles tuples (position,rayon)
    lst = [(o.GetMg().off,round(o.GetRad().x,2)) for o in parent.GetChildren() if isCircle(o)]
    pts = [p for p,rad in lst]
    polyo = c4d.PolygonObject(len(pts),0)
    polyo.SetAllPoints(pts)
    polyo.Message(c4d.MSG_UPDATE)
    #calcul des altitudes
    pointsOnSurface(polyo,mnt)

    res = c4d.BaseObject(c4d.Onull)
    polyo.InsertUnder(res)
    return res


#ATTENTION avec l'extraction des arbres on a des swissalti3D_extrait pour les arbres'
def getMNT(doc, obj = doc.GetFirstObject()):
    while obj :
        #print(obj.GetName().lower())
        for txt in NAMES_MNT:
            if txt in obj.GetName().lower() and obj.CheckType(c4d.Opolygon) and not '_extrait' in obj.GetName().lower():
                return obj
        res = getMNT(doc, obj.GetDown())
        if res : return res
        obj = obj.GetNext()
    return None



# Main function
def main():
    
    mnt = getMNT(doc,obj = doc.GetFirstObject())
    if not mnt:
        print('Pas de MNT')
        return

    trees = arbres_isoles(op,mnt)
    doc.InsertObject(trees)
    c4d.EventAdd()


    return

    #lyr_name = 'arbres-cordon_baliveaux_existants_h12-15'
    #lyr_name = 'arbres_baliveaux_existants_h12-15m'
    #lyr_name = 'ARBRES-surface_baliveaux_existants_h12m-15m_dist5-12'
    #lyr_name = 'arbres_baliveaux_existants_h12m'

    for o in op.GetChildren():
        lyr_name = o.GetName()

        #extraction du type
        typ = None
        for cat in CATEGORIES:
            regex = re.compile(cat, re.IGNORECASE)
            if re.match(regex,lyr_name):
                typ = cat.replace('s?','')

        #si on a un des types on extrait les données éventuelles
        if typ:
            hauteurs = None
            distances = None
            densites = None
            largeurs = None

            for txt in  lyr_name.split('_')[1:]:
                r = getInfo(txt,PREFIXE_HAUTEUR)
                if r :
                    hauteurs = r
                r = getInfo(txt,PREFIXE_DIST)
                if r :
                    distances = r
                r = getInfo(txt,PREFIXE_DENSITE)
                if r :
                    densites = r
                r = getInfo(txt,PREFIXE_LARGEUR)
                if r :
                    largeurs = r
    
    with localimport('/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/plugins/SITG_C4D/libs') as importer:
        importer.disable(['importArbresShapePoint'])
        import importArbresShapePoint as arbres
        
        print(arbres.create_mograph_cloner)
      
      
    return





# Execute main()
if __name__=='__main__':
    main()