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

CATEGORIES = ['emprise',
              'arbres',
              'arbres-surface',
              'arbres-alignement',
              'arbres-cordon',
              'construction']




# Main function
def main():
    
    lyr_name = 'arbres_baliveaux_existants_h12-15'
    #lyr_name = 'arbres_baliveaux_existants_h12-15m'
    lyr_name = 'arbres-surface_baliveaux_existants_h12m-15m_dist5-12'
    #lyr_name = 'arbres_baliveaux_existants_h12m'
    
    hauteurs = None
    distances = None
    for txt in  lyr_name.split('_'):
        
        #HAUTEURS
        #on recherche si le texte commence par CODE_HAUTEUR suivi de nombre
        p = re.compile(f'{PREFIXE_HAUTEUR}[0-9,/,]+', re.IGNORECASE)
        req = re.search(p,txt)
        #si c'est le cas on extrait le ou les hauteurs en float
        if req:
            hauteurs = [abs(float(s)) for s in re.findall(r'-?\d+\.?\d*', txt)]
            
        #DISTANCES
        p = re.compile(f'{PREFIXE_DIST}[0-9,/,]+', re.IGNORECASE)
        req = re.search(p,txt)
        if req:
            distances = [abs(float(s)) for s in re.findall(r'-?\d+\.?\d*', txt)]
    print(hauteurs, distances)     


# Execute main()
if __name__=='__main__':
    main()