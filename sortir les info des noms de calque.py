import c4d
import re


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

PREFIXE_HAUTEUR = 'h'
PREFIXE_DIST = 'dist'
PREFIXE_DENSITE = 'dens'
PREFIXE_LARGEUR = 'larg' #(largeur de cordon)

#dans re le ? sert à dire que le caractère qui précède est facultatif
CATEGORIES = [r'emprises?',
              r'arbres?',
              r'arbres?-surfaces?',
              r'arbres?-alignements?',
              r'arbres?-cordons?',
              r'constructions?']


def getInfo(txt,prefixe):
    """renvoie une liste à une ou deux valeurs"""
    p = re.compile(f'{prefixe}[0-9,/,]+', re.IGNORECASE)
    req = re.search(p,txt)
    if req:
        return [abs(float(s)) for s in re.findall(r'-?\d+\.?\d*', txt)]
    return None


# Main function
def main():

    lyr_name = 'arbres-cordon_baliveaux_existants_h12-15'
    #lyr_name = 'arbres_baliveaux_existants_h12-15m'
    #lyr_name = 'ARBRES-surface_baliveaux_existants_h12m-15m_dist5-12'
    #lyr_name = 'arbres_baliveaux_existants_h12m'
    
    #extraction du type
    typ = None
    for cat in CATEGORIES:
        regex = re.compile(cat, re.IGNORECASE)
        if re.match(regex,lyr_name):
            typ = cat.replace('s?','')
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
    print(hauteurs)
    print(distances)
    print(densites)
    print(largeurs)
    return


# Execute main()
if __name__=='__main__':
    main()