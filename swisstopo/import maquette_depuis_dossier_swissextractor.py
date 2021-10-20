import c4d, os
from libs import importMNT
from glob import glob

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


DOC_NOT_IN_METERS_TXT = "Les unités du document ne sont pas en mètres, si vous continuez les unités seront modifiées.\nVoulez-vous continuer ?"
CONTAINER_ORIGIN =1026473

EPAISSEUR = 10 #épaisseur du socle depuis le points minimum

def selectEdgesContour(op):

    nb = c4d.utils.Neighbor(op)
    nb.Init(op)
    bs = op.GetSelectedEdges(nb,c4d.EDGESELECTIONTYPE_SELECTION)
    bs.DeselectAll()
    for i,poly in enumerate(op.GetAllPolygons()):
        inf = nb.GetPolyInfo(i)
        if nb.GetNeighbor(poly.a, poly.b, i)==-1:
            bs.Select(inf['edge'][0])

        if nb.GetNeighbor(poly.b, poly.c, i)==-1: 
            bs.Select(inf['edge'][1])
            
        
        #si pas triangle
        if not poly.c == poly.d :
            if nb.GetNeighbor(poly.c, poly.d, i)==-1: 
                bs.Select(inf['edge'][2])
                
        if nb.GetNeighbor(poly.d, poly.a, i)==-1: 
            bs.Select(inf['edge'][3])        
        
    op.SetSelectedEdges(nb,bs,c4d.EDGESELECTIONTYPE_SELECTION)


def socle(mnt,doc):
    mg = mnt.GetMg()
    alts = [(p*mg).y for p in mnt.GetAllPoints()]
    alt_min = min(alts) - EPAISSEUR
    
    #tag de selelction de polygone
    tag_sel_terrain = c4d.SelectionTag(c4d.Tpolygonselection)
    bs = tag_sel_terrain.GetBaseSelect()
    bs.SelectAll(mnt.GetPolygonCount())
    tag_sel_terrain[c4d.ID_BASELIST_NAME] = 'mnt'
    
    mnt.InsertTag(tag_sel_terrain)

    #Sélection des arrêtes du contour
    selectEdgesContour(mnt)
    #Extrusion à zéro
    settings = c4d.BaseContainer()                 # Settings
    settings[c4d.MDATA_EXTRUDE_OFFSET] = 0      # Length of the extrusion
    
    res = c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_EXTRUDE_TOOL,
                                    list = [mnt],
                                    mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                    bc = settings,
                                    doc = doc)
                                    
                                    
    #Valeurs commune des points                                
    
    settings = c4d.BaseContainer()                 # Settings
    settings[c4d.MDATA_SETVALUE_SETY] = c4d.MDATA_SETVALUE_SET_SET  
    settings[c4d.MDATA_SETVALUE_VAL] = c4d.Vector(0,alt_min,0)
    #settings[c4d.TEMP_MDATA_SETVALUE_VAL_Y] = -2000
    settings[c4d.MDATA_SETVALUE_SYSTEM] = c4d.MDATA_SETVALUE_SYSTEM_WORLD
    
    res = c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_SETVALUE_TOOL,
                                    list = [mnt],
                                    mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION,
                                    bc = settings,
                                    doc = doc)
    doc.EndUndo()
    c4d.EventAdd()

def get_imgs_georef(path, ext = '.png'):
    res = []
    for fn in glob(os.path.join(path,'*'+ext)):
        fn_wld = fn.replace(ext,'.wld')
        if os.path.isfile(fn_wld):
            res.append(fn)
    return res

def get_swissbuildings3D_dxfs(path):
    """renvoie une liste de fichier dxf contenus dans
       un sous-dossier qui contient le mot swissbuildings3d"""
    lst_dxf = None
    
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            if 'swissbuildings3d' in name:
                lst_dxf = [fn_dxf for fn_dxf in glob(os.path.join(root, name,'*.dxf'))]
    return lst_dxf


def get_cube_from_obj(obj, haut_sup = 100):
    """Lae paramètre haut_sup sert à avoirun peu de marge en haut et en bas lorsque l'on découpe les bâtiment"""
    mg = obj.GetMg()
    rad = obj.GetRad()
    centre = obj.GetMp()
    
    #4 points de la bbox selon orientation de l'objet
    pts = [ c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
            c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
            c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z+rad.z) * mg,
            c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
            c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
            c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
            c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
            c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z+rad.z) * mg]

    mini = c4d.Vector(min([p.x for p in pts]),min([p.y for p in pts]),min([p.z for p in pts]))
    maxi = c4d.Vector(max([p.x for p in pts]),max([p.y for p in pts]),max([p.z for p in pts]))
    
    cube = c4d.BaseObject(c4d.Ocube)
    centre = (mini+maxi)/2
    
    cube.SetAbsPos(centre)
    cube[c4d.PRIM_CUBE_LEN] = maxi-mini + c4d.Vector(0,haut_sup,0)

    return cube

def import_swissbuildings3D_from_list_dxf(lst_dxfs,doc, origin = None):
    #mise en cm des options d'importation DXF
    plug = c4d.plugins.FindPlugin(1001035, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        print ("pas de module d'import 3DS")
        return
    op = {}

    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, op):

        import_data = op.get("imexporter",None)

        if not import_data:
            return False

        scale = import_data[c4d.DXFIMPORTFILTER_SCALE]
        scale.SetUnitScale(1,c4d.DOCUMENT_UNIT_M)

        import_data[c4d.DXFIMPORTFILTER_SCALE] = scale

        import_data[c4d.DXFIMPORTFILTER_LAYER] = c4d.DXFIMPORTFILTER_LAYER_NONE
    
    first_obj = doc.GetFirstObject()
    
    for fn in lst_dxfs:
        c4d.documents.MergeDocument(doc, fn, c4d.SCENEFILTER_OBJECTS,None)
        obj = doc.GetFirstObject()
        if not obj : continue
        mg = obj.GetMg()
        if not origin :
            doc[CONTAINER_ORIGIN] =mg.off
            origin = doc[CONTAINER_ORIGIN]
        mg.off-=origin
        obj.SetMg(mg)

    
    

# Main function
def main():
    
    pth = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/St_Cergue/extraction_swisstopo'
    pth = c4d.storage.LoadDialog(flags = c4d.FILESELECT_DIRECTORY,title="Dossier contenant les .dxf de swisstopo")
    if not pth : return
    
    lst_asc = [fn_asc for fn_asc in glob(os.path.join(pth,'*.asc'))]
    lst_dxf = get_swissbuildings3D_dxfs(pth)
    lst_imgs = get_imgs_georef(pth)
    
    if not lst_asc and not lst_dxf:
        c4d.gui.MessageDialog("""Il n'y a ni terrain ni swissbuidings3D au format dxf dans le dossier, import impossible""")
        return
    
    #document en mètre
    doc = c4d.documents.GetActiveDocument()

    usdata = doc[c4d.DOCUMENT_DOCUNIT]
    scale, unit = usdata.GetUnitScale()
    if  unit!= c4d.DOCUMENT_UNIT_M:
        rep = c4d.gui.QuestionDialog(DOC_NOT_IN_METERS_TXT)
        if not rep : return
        unit = c4d.DOCUMENT_UNIT_M
        usdata.SetUnitScale(scale, unit)
        doc[c4d.DOCUMENT_DOCUNIT] = usdata

    

    origin = doc[CONTAINER_ORIGIN]
    
    doc.StartUndo()
    
    
    #Modèle(s) de terrain
    mnt = None
    cube_mnt = None
    for fn_asc in lst_asc:
        mnt = importMNT.terrainFromASC(fn_asc)
        #socle
        if mnt:
            socle(mnt,doc)
            doc.InsertObject(mnt)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,mnt)
            cube_mnt = get_cube_from_obj(mnt)
            doc.InsertObject(cube_mnt)
    
    #Swissbuidings3D
    import_swissbuildings3D_from_list_dxf(lst_dxf,doc, origin = origin)
    
    c4d.EventAdd()
    doc.EndUndo()
    return

    

    pth = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/St_Cergue/extraction_swisstopo'
    
    
    
    print(get_swissbuildings3D_dxfs(pth))
    return
    for root, dirs, files in os.walk(pth, topdown=False):
        for name in dirs:
            if 'swissbuildings3d' in name:
                print(name)
                print(os.path.join(root, name))
    
    return
    print(get_imgs_georef(pth))
    
    return
    
    
    
    
    
    
            
            
    
    c4d.EventAdd()
    doc.EndUndo()
    return
    fn = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/St_Cergue/extraction_swisstopo/swissalti3d_50cm.asc'
    
    

    doc.StartUndo()
    
    
    
    
    
    
    
    
    c4d.EventAdd()
    doc.EndUndo()

# Execute main()
if __name__=='__main__':
    main()