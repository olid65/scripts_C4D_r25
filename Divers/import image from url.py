import c4d
import os.path
import urllib.request

CONTAINER_ORIGIN =1026473



NOT_SAVED_TXT = "Le document doit être enregistré pour pouvoir copier les textures dans le dossier tex, vous pourrez le faire à la prochaine étape\nVoulez-vous continuer ?"

DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"

######################################################################################################

def tex_folder(doc, subfolder = None):
    """crée le dossier tex s'il n'existe pas et renvoie le chemin
       si subfolder est renseigné crée également le sous-dossier
       et renvoie le chemin du sous dossier
       Si le doc n'est pas enregistré renvoie None
       """

    path_doc = doc.GetDocumentPath()
    #si le doc n'est pas enregistré renvoie None
    if not path_doc : return None

    path = os.path.join(path_doc,'tex')

    if subfolder:
        path = os.path.join(path,subfolder)

    if not os.path.isdir(path):
        os.makedirs(path)
    return path

# Main function
def main():
    url = 'http://server.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/export?bbox=2481143.4526204173,1108867.338152807,2504619.377993354,1121283.7045966922&format=png&size=1024,542&f=image&bboxSR=2056&imageSR=2056'
    nom_img = 'ESRI_image.png'
    
    #le doc doit être en mètres
    doc = c4d.documents.GetActiveDocument()

    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()
    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata



    #si le document n'est pas enregistré on enregistre
    path_doc = doc.GetDocumentPath()

    while not path_doc:
        rep = c4d.gui.QuestionDialog(NOT_SAVED_TXT)
        if not rep : return
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()
    
    path = tex_folder(doc, subfolder = 'ESRI')
    
    fn_img = os.path.join(path,nom_img)
    
    try:
        x = urllib.request.urlopen(url)
        with open(fn_img,'wb') as saveFile:
            saveFile.write(x.read())
    except:
        print('pas bien !')

# Execute main()
if __name__=='__main__':
    main()