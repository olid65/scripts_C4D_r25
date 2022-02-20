import c4d
import os
from glob import glob

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def get_name_tilenumber_year_from_fn(fn):    
    try :
        name,year,tilenumber,*other = os.path.basename(fn)[:-4].split('_')
    except:
        return None
    return name,year,tilenumber

# Main function
def main():
    pth = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Vernayaz_decoup_commune/swisstopo/swissimage-dop10_2m'
    pth = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Vernayaz_decoup_commune/swisstopo/swissalti3d_2m'
    dico = {}
    for fn in glob(os.path.join(pth,'*.tif')):
        #nom,an,no_flle,resol,epsg = os.path.basename(fn)[:-4].split('_')
        print(get_name_tilenumber_year_from_fn(fn))
        #dico.setdefault(no_flle,[]).append((an,fn))
    return    
    for no_flle,lst in dico.items():
        #si on en a plus qu'un il y a doublon
        if len(lst)>1:
            #sur la liste triée on supprime tous sauf le dernier qui est le plus récent
            for an,fn in sorted(lst)[:-1]:
                os.remove(fn)

        
        
        
    

# Execute main()
if __name__=='__main__':
    main()