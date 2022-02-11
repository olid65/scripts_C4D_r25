# -*- coding: utf-8 -*-
import c4d, math
import os.path

DELTA_ALT = 100 #marge de sécurité pour altitude (utilisé dans getMinMax)
SUFFIX_EXTRACT = "_extrait"
NOM_RES = "Arbres_surfaces"
CLONE_QUANTITY = 1000

RAYON_SPHERE_DEFAULT = 6

TXT_NO_SPLINE = "Vous devez sélectionner au moins une spline ou un objet neutre contenant des splines !"
TXT_CHECK_SPLINE = "Il y a une ou plusieurs splines qui ne sont soit pas fermées soit qui possèdent moins que 3 points.\nVoulez-vous continuer ?"
TXT_NO_POLYOBJECT = "Vous devez sélectionner également un objet polygonal (terrain)"
TXT_MANY_POLYOBJECT = "Il y a plusieurs objets polygonaux sélectionné, le premier ({}) sera utilisé comme terrain.\nVoulez-vous continuer?"

NOM_SRCE_ARBRES = 'sources_vegetation'


##############################################
def main(fn_arbres_srce):
    """ """
    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    # récupération des splines sélectionnées et du terrain
    sel = getSplinesAndMNT(doc)
    if not sel: return
    splines, mnt = sel

    res = arbresSurface(splines, mnt, fn_arbres_srce=fn_arbres_srce)
    if res :
        doc.InsertObject(res, pred=mnt)
        doc.AddUndo(c4d.UNDOTYPE_NEW, res)
        res.ChangeNBit(c4d.NBIT_OM1_FOLD, c4d.NBITCONTROL_SET)
        doc.EndUndo()
    c4d.EventAdd()

################################################


def getArbresSourcesFromFile(
        fn='/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/plugins/SITG_C4D/__arbres_2018__.c4d'):
    if not fn: return None

    if not os.path.isfile(fn):
        return None

    doc_arbres = c4d.documents.LoadDocument(fn, c4d.SCENEFILTER_OBJECTS)
    srce_veget = doc_arbres.SearchObject('sources_vegetation')

    if not srce_veget: return None

    return [o.GetClone() for o in srce_veget.GetChildren()]


# RECUPERATION SPLINES ET TERRAIN ######################################################

def checkSpline(splines):
    for sp in splines:
        if not sp.IsClosed(): return False
        # s'il n'y a pas au moins 3 points on renvoie false
        if sp.GetPointCount() < 3: return False
    return True


def getSplinesAndMNT(doc):
    """renvoie les splines sélectionnées et le premier objet polygonal (MNT)
       du document actif"""

    splines = doc.GetActiveObjectsFilter(1, c4d.Ospline, c4d.NOTOK)
    if not splines:
        c4d.gui.MessageDialog(TXT_NO_SPLINE)
        return False

    if not checkSpline(splines):
        rep = c4d.gui.QuestionDialog(TXT_CHECK_SPLINE)
        if not rep: return False

    polyobj = doc.GetActiveObjectsFilter(1, c4d.Opolygon, c4d.NOTOK)
    if not polyobj:
        c4d.gui.MessageDialog(TXT_NO_POLYOBJECT)
        return False

    # si il y a au moins un objet polygonal on prend le premier
    if polyobj: mnt = polyobj[0]

    if len(polyobj) > 1:
        rep = c4d.gui.QuestionDialog(TXT_MANY_POLYOBJECT.format(mnt.GetName()))
        if not rep: return False

    return splines, mnt


##############################################################################


def area2Dpoly(pts):
    """calcule la surface planaire (x,z) d'un polygone
       d'après https://www.mathopenref.com/coordpolygonarea2.html"""
    area = 0
    j = len(pts) - 1
    for i in range(len(pts)):
        area += (pts[j].x + pts[i].x) * (pts[j].z - pts[i].z)
        j = i
    return area / 2.


def area2Dpolyobj(poly_obj):
    """calcule la surface 2D (xz) d'un objet polygonal"""
    area = 0
    mg = poly_obj.GetMg()
    pts = [p * mg for p in poly_obj.GetAllPoints()]
    polys = poly_obj.GetAllPolygons()

    for poly in polys:
        p1 = pts[poly.a]
        p2 = pts[poly.b]
        p3 = pts[poly.c]
        p4 = pts[poly.d]

        if p3 == p4:
            area += area2Dpoly([p1, p2, p3])
        else:
            area += area2Dpoly([p1, p2, p3, p4])
    return area


def getMinMaxY(obj):
    """renvoie le minY et le maxY en valeur du monde d'un objet"""
    mg = obj.GetMg()
    alt = [(pt * mg).y for pt in obj.GetAllPoints()]
    return min(alt) - DELTA_ALT, max(alt) + DELTA_ALT


def changeAltAbs(pt, mg, alt):
    """modifie l'altitude selon le monde d'un points"""
    pt = pt * mg
    pt.y = alt
    return pt * ~mg


def volumeFromSpline(null_splines, minY, maxY):
    """retourne un objet extrusion en mode hiérarchique avec le null_splines en enfant
       la bas du volume est au minY et le haut à maxY"""
    for sp in null_splines.GetChildren():
        mg = sp.GetMg()

        # on met les points de la spline au minY
        pts = [changeAltAbs(p, mg, minY) for p in sp.GetAllPoints()]
        sp.SetAllPoints(pts)
        sp.Message(c4d.MSG_UPDATE)

    # extrusion
    extr = c4d.BaseObject(c4d.Oextrude)
    extr[c4d.EXTRUDEOBJECT_DIRECTION] = c4d.EXTRUDEOBJECT_DIRECTION_Y
    extr[c4d.EXTRUDEOBJECT_EXTRUSIONOFFSET] = maxY - minY
    extr[c4d.EXTRUDEOBJECT_HIERARCHIC] = True
    null_splines.InsertUnder(extr)
    return extr


def cutMNTfromSpline(mnt, splines):
    """retourne une découpe de l'objet polygonal mnt selon la liste de splines"""
    null_sp = c4d.BaseObject(c4d.Onull)
    for sp in splines:
        sp.GetClone().InsertUnder(null_sp)

    # calculation of altitude min and max from terrain (avec security margin)
    minY, maxY = getMinMaxY(mnt)

    # volume from spline for extraction
    extr = volumeFromSpline(null_sp, minY, maxY)

    # boolean
    boolObj = c4d.BaseObject(c4d.Oboole)
    boolObj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_INTERSECT
    boolObj[c4d.BOOLEOBJECT_HIGHQUALITY] = False

    extr.InsertUnder(boolObj)
    mnt.GetClone().InsertUnder(boolObj)

    # temporary file
    temp_doc = c4d.documents.BaseDocument()

    mnt_extract = None
    # TODO : manage exceptions if not ...
    if temp_doc:
        temp_doc.InsertObject(boolObj)
        temp_doc_polygonize = temp_doc.Polygonize()
        bool_res = temp_doc_polygonize.GetFirstObject()

        if bool_res:
            mnt_extract = bool_res.GetDown()

            if mnt_extract:
                mnt_extract.SetName(mnt.GetName() + SUFFIX_EXTRACT)

    return mnt_extract.GetClone()


def clonerFromPolyObject(poly_object, objs_to_clone=None):
    """renvoie un null contenant un cloner mograph en mode objet en mode quantité
       sur l'objet polygonal poly_object et un effecteur random avec rotation h aléatoire à 360°"""

    res = c4d.BaseObject(c4d.Onull)
    res.SetName('cloneur_mograph')

    # cloneur
    cloner = c4d.BaseObject(1018544)
    cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = c4d.ID_MG_MOTIONGENERATOR_MODE_OBJECT
    cloner[c4d.MGCLONER_MODE] = c4d.MGCLONER_MODE_RANDOM
    cloner[c4d.MGCLONER_VOLUMEINSTANCES_MODE] = c4d.MGCLONER_VOLUMEINSTANCES_MODE_RENDERMULTIINSTANCE
    cloner[c4d.MG_OBJECT_LINK] = poly_object
    cloner[c4d.MG_POLY_MODE_] = c4d.MG_POLY_MODE_SURFACE
    cloner[c4d.MG_OBJECT_ALIGN] = False
    cloner[c4d.MG_POLYSURFACE_COUNT] = CLONE_QUANTITY
    cloner.InsertUnder(res)

    if objs_to_clone:
        for o in objs_to_clone:
            o.InsertUnderLast(cloner)

    else:
        nobj = c4d.BaseObject(c4d.Onull)
        sphere = c4d.BaseObject(c4d.Osphere)
        sphere[c4d.PRIM_SPHERE_RAD] = RAYON_SPHERE_DEFAULT
        sphere.InsertUnder(nobj)
        sphere.SetRelPos(c4d.Vector(0, RAYON_SPHERE_DEFAULT, 0))

        nobj.InsertUnder(cloner)

    # random effector
    rdm_effector = c4d.BaseObject(1018643)
    in_ex_data = cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST]
    in_ex_data.InsertObject(rdm_effector, 1)
    cloner[c4d.ID_MG_MOTIONGENERATOR_EFFECTORLIST] = in_ex_data

    rdm_effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = False
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_ROTATE_ACTIVE] = True
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_ROTATION, c4d.VECTOR_X] = math.pi * 2

    rdm_effector[c4d.ID_MG_BASEEFFECTOR_SCALE_ACTIVE] = True
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_UNIFORMSCALE] = True
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_POSITIVESCALE] = True
    rdm_effector[c4d.ID_MG_BASEEFFECTOR_USCALE] = 0.5

    rdm_effector.InsertUnder(res)
    return res


def arbresSurface(splines, mnt, name=NOM_RES, fn_arbres_srce=None):
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(name)

    mnt_extract = cutMNTfromSpline(mnt, splines)
    mnt_extract[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_OFF
    mnt_extract[c4d.ID_BASEOBJECT_VISIBILITY_RENDER] = c4d.OBJECT_OFF

    # TODO : calculer le nombre de clone d'après la surface
    # par rapport à la taille des clones
    surface = area2Dpolyobj(mnt_extract)

    arbres_source = None
    if fn_arbres_srce:
        arbres_source = getArbresSourcesFromFile(fn_arbres_srce)

    if mnt_extract:
        mnt_extract = mnt_extract.GetClone()
        mnt_extract.InsertUnder(res)
        cloner = clonerFromPolyObject(mnt_extract, objs_to_clone=arbres_source)
        cloner.InsertUnderLast(res)
    return res

def main():
    fn_arbres_srce = '/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/plugins/SITG_C4D/__arbres_2018__.c4d'
    splines = op.GetChildren()
    mnt = op.GetNext()
    res = arbresSurface(splines, mnt, name=NOM_RES, fn_arbres_srce = fn_arbres_srce )
    doc.InsertObject(res)
    c4d.EventAdd()

# Execute main()
if __name__ == '__main__':
    main()