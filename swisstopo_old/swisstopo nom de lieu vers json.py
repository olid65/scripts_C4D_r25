import c4d
import csv, json
from collections import OrderedDict

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


#le fichier csv  de base a été téléchargé sous :
#https://data.geo.admin.ch/ch.swisstopo-vd.ortschaftenverzeichnis_plz/PLZO_CSV_LV95.zip



def list_duplicates(listNums):
  once = set()
  seenOnce = once.add
  twice = set( num for num in listNums if num in once or seenOnce(num) )
  return list( twice )


# noms de colonnes : ['Ortschaftsname', 'PLZ', 'Zusatzziffer', 'Gemeindename', 'BFS-Nr', 'Kantonskürzel', 'E', 'N', 'Sprache']
# Main function
def main():
    fn_csv = '/Users/olivierdonze/Downloads/PLZO_CSV_LV95 2/PLZO_CSV_LV95.csv'
    
    lst = []
    
    #ATTENTION dans le fichier d'origine il y avait des doublons Nom,PLZ mais avec des 
    #coordonées différentes, j'en ai gardé qu'une seule (la dernière qui écrase la précédente dans le dico)
    with open(fn_csv, encoding = 'utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile,delimiter=';',dialect='excel')
        #print(reader.fieldnames)
        
        #lst = [(row['Ortschaftsname'],row['PLZ']) for row in reader]
        
        #print(sorted(list_duplicates(lst)))

        dico = {}

        for row in reader:
            name,plz, est,nord = row['Ortschaftsname'],row['PLZ'], float(row['E']),float(row['N'])
            print(name)
            #pos = c4d.Vector(est,0,nord)
            #J'ai splité les nom qui était double allemand/français'
            if '/' in name:
                nom1,nom2 = name.split('/')
                dico[f'{nom1} ({plz})'] = (est,nord)
                dico[f'{nom2} ({plz})'] = (est,nord)
                
            else:
                dico[f'{name} ({plz})'] = (est,nord)
                
        
        dico_sorted = {k:dico[k] for k in sorted(dico.keys())}
        #print(dico_sorted)
        
        fn_json = '/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/library/scripts/swisstopo/noms_lieux.json'
        
        with open(fn_json,'w', encoding = 'utf-8') as fjson:
            fjson.write(json.dumps(dico_sorted, indent=4,ensure_ascii=False))
        
        
    
# Execute main()
if __name__=='__main__':
    main()