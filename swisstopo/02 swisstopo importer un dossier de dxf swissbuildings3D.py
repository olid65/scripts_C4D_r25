import c4d,os
from c4d import gui
from zipfile import ZipFile
from glob import glob

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"
CONTAINER_ORIGIN =1026473


# Main function
def main():
    #path = '/Users/donzeo/Documents/TEMP/swisstopo/dxf_tests'
    path = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY,title="Dossier contenant les .dxf de swisstopo")

    if not path : return

    doc = c4d.documents.GetActiveDocument()

    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()
    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata

    #mise en cm des options d'importation DXF
    plug = c4d.plugins.FindPlugin(1001035, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        print ("pas de module d'import 3DS")
        return
    op = {}

    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):

        import_data = op.get("imexporter",None)

        if not import_data:
            print ("pas de data pour l'import 3Ds")
            return

        scale = import_data[c4d.DXFIMPORTFILTER_SCALE]
        scale.SetUnitScale(1,c4d.DOCUMENT_UNIT_M)

        import_data[c4d.DXFIMPORTFILTER_SCALE] = scale

        import_data[c4d.DXFIMPORTFILTER_LAYER] = c4d.DXFIMPORTFILTER_LAYER_NONE

    origin = doc[CONTAINER_ORIGIN]


    i = 0
    first_obj = doc.GetFirstObject()
    for fn in glob(os.path.join(path,'*.dxf')):
        c4d.documents.MergeDocument(doc, fn, c4d.SCENEFILTER_OBJECTS,None)
        obj = doc.GetFirstObject()
        if not obj : continue
        mg = obj.GetMg()
        if not origin :
            doc[CONTAINER_ORIGIN] =mg.off
            origin = doc[CONTAINER_ORIGIN]
        mg.off-=origin
        obj.SetMg(mg)

    c4d.EventAdd()


# Execute main()
if __name__=='__main__':
    main()