import c4d
import re


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
    
    
    #calcul des altitudes
    
    
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
    
    arbres_isoles(op,mnt)
    
    
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
            
            
            


# Execute main()
if __name__=='__main__':
    main()