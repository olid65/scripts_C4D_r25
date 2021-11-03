import c4d, os
from glob import glob
from shutil import copyfile

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True
CONTAINER_ORIGIN =1026473

NOT_SAVED_TXT = "Le document doit être enregistré vous pourrez le faire à la prochaine étape\nVoulez-vous continuer ?"
DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"

def importObj(fn_obj,doc,origin_obj):
    
    #mise en cm des option d'importation 3DS
    plug = c4d.plugins.FindPlugin(c4d.FORMAT_OBJ2IMPORT, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        print ("pas de module d'import obj")
        return 
    op = {}
   
    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):
        
        import_data = op.get("imexporter",None)
        if not import_data:
            print ("pas de data pour l'import obj")
            return
        
        import_data[c4d.OBJIMPORTOPTIONS_POINTTRANSFORM_SWAPYZ] = True
        
        # Change 3DS import settings
        scale = import_data[c4d.OBJIMPORTOPTIONS_SCALE]
        print(scale)
        scale.SetUnitScale(1,c4d.DOCUMENT_UNIT_M)
        import_data[c4d.OBJIMPORTOPTIONS_SCALE] = scale
    
    if c4d.documents.MergeDocument(doc, fn_obj, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MATERIALS):
        obj = doc.GetFirstObject()
        obj.SetName(os.path.basename(fn_obj))
        pts = obj.GetAllPoints()
        pts = [(p-origin_obj) for p in pts]
        obj.SetAllPoints(pts)              
        
        obj.SetAbsPos(origin_obj-doc[CONTAINER_ORIGIN])
        obj.Message(c4d.MSG_UPDATE)  
        
    
        


# Main function
def main():
    
    #si le document n'est pas enregistré on enregistre
    path_doc = doc.GetDocumentPath()
    while not path_doc:
        rep = c4d.gui.QuestionDialog(NOT_SAVED_TXT)
        if not rep : return
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()
        
    path = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY,title="Dossier contenant les dossiers de photomaillage 3D")
    #path = '/Users/olivierdonze/Documents/TEMP/SITG_tuile_3D'
    if not path : return
        
    #Document en mètre
    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()
    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata

    
        
    dirs = [f.path for f in os.scandir(path) if f.is_dir()]
    
        
    dir_tex = os.path.join(path_doc,'tex')
    
    if not os.path.isdir(dir_tex):
        os.mkdir(dir_tex)
    
    for d in dirs:
        #on récupère les coordonnées depuis le nom du dossier
        name_dir = os.path.basename(d)
        try :
            x,z = [float(v) for v in name_dir.split('_')]
            #test pour coordonnées GE
            if x< 2000000 or z< 1000000: continue
            print(x,z)
        except:
            continue
        
        #il doit y avoir un sous-dossier qui a le même nom   
        #que le dossier et qui continet les images
        dir_jpegs = os.path.join(d,name_dir)

        #si c'est le cas
        if os.path.isdir(dir_jpegs) : 
            #on crée un sous-dossier dans tex
            ss_dir = os.path.join(dir_tex,name_dir)
            if not os.path.isdir(ss_dir):
                os.mkdir(ss_dir)
                
            #et on copie les fichiers jpeg en rajoutant les coordonnées
            #comme suffixe pour éviter les doublons de nom
            for fn_src_jpg in glob(os.path.join(dir_jpegs,'*.jpg')):
                name = name_dir+'_'+os.path.basename(fn_src_jpg)
                fn_dst_jpg = os.path.join(ss_dir,name)
                copyfile(fn_src_jpg,fn_dst_jpg)
                
        #IMPORT FICHIER OBJ
        fn_obj = os.path.join(d,name_dir+'.obj')
        if os.path.isfile(fn_obj):
            origin_obj = c4d.Vector(x,0,z)
            origin = doc[CONTAINER_ORIGIN]  
            if not origin:
                 doc[CONTAINER_ORIGIN] = origin_obj
            
            importObj(fn_obj,doc,origin_obj)

    #TRAITEMENT DES MATERIAUX
    mat = doc.GetFirstMaterial()
    while mat:
        shd = mat.GetFirstShader()
        if shd.GetType()==c4d.Xbitmap:
            name = shd[c4d.BITMAPSHADER_FILENAME].replace('\\','_')
            shd[c4d.BITMAPSHADER_FILENAME] = name               
            shd.Message(c4d.MSG_UPDATE)
            
            mat.SetName(name)
            mat.Message(c4d.MSG_UPDATE)
        mat = mat.GetNext()
    c4d.EventAdd()
    

# Execute main()
if __name__=='__main__':
    main()