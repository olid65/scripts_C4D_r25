import c4d,os
import urllib.request
#import requests
from zipfile import ZipFile
import csv


LOAD_DLG_CSV_TXT = "Fichier .csv de swisstopo :"
NB_MAX_ALERT = 20
TXT_ALERT_MAX = f"Il y a plus de {NB_MAX_ALERT} à télécharger, voulez-vous continuer ?"

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():

    #fn_csv = '/Users/donzeo/Downloads/ch.swisstopo.swissbuildings3d_2-BikSA5fs.csv'
    fn_csv = c4d.storage.LoadDialog(type = c4d.FILESELECTTYPE_SCENES, title= LOAD_DLG_CSV_TXT)
    if not fn_csv : return

    pth = os.path.dirname(fn_csv)
    name_dir = os.path.basename(fn_csv)[:-4]
    pth = os.path.join(pth,name_dir)

    if not os.path.isdir(pth) :
        os.mkdir(pth)

    urls = []

    with open(fn_csv) as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            urls.append(row[0])

    if len(urls) > NB_MAX_ALERT:
        rep = c4d.gui.QuestionDialog(f"Il y a {len(urls)} fichiers à télécharger, voulez-vous continuer ?")
        if not rep : return

    #TODO : inclure ce code dans un thread
    for url in urls:
        fn_dst = os.path.join(pth,url.split('/')[-1])
        #r = requests.get(url)
        try:
            x = urllib.request.urlopen(url)
            
            #print(x.read())
        
            with open(fn_dst,'wb') as saveFile:
                saveFile.write(x.read())

            #si on a un fichier zippé on décompresse    
            if fn_dst[-4:] =='.zip':
                zfobj = ZipFile(fn_dst)
                for name in zfobj.namelist():
                    uncompressed = zfobj.read(name)
                    # save uncompressed data to disk
                    outputFilename = os.path.join(pth,name)
                    with open(outputFilename,'wb') as output:
                        output.write(uncompressed)
                os.remove(fn_dst)
                
        except Exception as e:
            print(str(e))
            
    c4d.gui.MessageDialog(f"""Les fichiers ont été téléchargés dans le dossier :\n {pth}""")

# Execute main()
if __name__=='__main__':
    main()