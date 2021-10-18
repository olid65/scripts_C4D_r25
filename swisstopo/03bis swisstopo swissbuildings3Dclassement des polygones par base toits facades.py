import c4d

def getPtsPoly(poly,obj):
    return obj.GetPoint(poly.a),obj.GetPoint(poly.b),obj.GetPoint(poly.c),obj.GetPoint(poly.d)

def recup_norm(poly, obj) :
    a,b,c,d = getPtsPoly(poly,obj)
    normale = (a - c).Cross(b - d)
    normale.Normalize()
    return normale

def isInMin(poly,obj, miny):
    a,b,c,d = getPtsPoly(poly,obj)
    return a.y==miny and b.y==miny and c.y==miny

def touchMin(poly,obj, miny):
    """renvoie vrai si au moins un des points est un point minimum"""
    a,b,c,d = getPtsPoly(poly,obj)
    return a.y==miny or b.y==miny or c.y==miny
    

def classementPolygone(op):
    
    tag_base = c4d.SelectionTag(c4d.Tpolygonselection)
    tag_base.SetName('base')
    bs_base = tag_base.GetBaseSelect()
    
    tag_facade = c4d.SelectionTag(c4d.Tpolygonselection)
    tag_facade.SetName('facade')
    bs_facade = tag_facade.GetBaseSelect()
    
    tag_toit = c4d.SelectionTag(c4d.Tpolygonselection)
    tag_toit.SetName('toit')
    bs_toit = tag_toit.GetBaseSelect()
    #on récupère le tyype d'objet
    #dans le cas des Bâtiment ouvert et Toits flottants qu'on ne prenne pas la base
    typ_obj = op.GetName()
    
    #si on a un type "Bâtiment ouvert" ou "Toit flottant" on considère
    #que c'est tout de la toiture
    #if typ_obj=='Bâtiment ouvert' or typ_obj == 'Toit flottant':
        #for i in xrange(op.GetPolygonCount()):
            #bs_toit.Select(i)
    
    #on prend le minimum en y pour détecter le plancher
    y = [p.y for p in op.GetAllPoints()]
    miny = min(y)
    
    
    #maxy = max(y)
    
    #calcul des normales
    for i,p in enumerate(op.GetAllPolygons()):
        norm =recup_norm(p, op)
        norm.y = round(norm.y,3)
        
        #BASE
        if  norm == c4d.Vector(0,-1,0) and isInMin(p,op, miny):
            bs_base.Select(i)
            
        #FACADES
        elif norm.y ==0:#and touchMin(p,op, miny):
            bs_facade.Select(i)
        
        #TOITS
        else:
            bs_toit.Select(i)
        
    if bs_base.GetCount():
        op.InsertTag(tag_base)
    if bs_toit.GetCount():
        op.InsertTag(tag_toit)
    if bs_facade.GetCount():
        op.InsertTag(tag_facade)

def main():
    for o in doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0):
        classementPolygone(o)
    #for obj in op.GetChildren():
        #classementPolygone(obj)
    c4d.EventAdd()           
    
if __name__=='__main__':
    main()
