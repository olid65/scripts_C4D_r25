import c4d
import subprocess
import os


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi, largeur, hauteur


def empriseObject(obj, origine):
    mg = obj.GetMg()

    rad = obj.GetRad()
    centre = obj.GetMp()

    # 4 points de la bbox selon orientation de l'objet
    pts = [c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z + rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x - rad.x, centre.y + rad.y, centre.z - rad.z) * mg,
           c4d.Vector(centre.x + rad.x, centre.y - rad.y, centre.z + rad.z) * mg]

    mini = c4d.Vector(min([p.x for p in pts]), min([p.y for p in pts]), min([p.z for p in pts])) + origine
    maxi = c4d.Vector(max([p.x for p in pts]), max([p.y for p in pts]), max([p.z for p in pts])) + origine

    return mini, maxi

# Main function
def main():

    origine = doc[CONTAINER_ORIGIN]

    mini,maxi = empriseObject(op,origine)
    xmin,ymin,xmax,ymax = mini.x,mini.z,maxi.x,maxi.z
    
    ogr2ogr = '/Library/Frameworks/GDAL.framework/Versions/3.2/Programs/ogr2ogr'

    fn_src = '/Volumes/My Passport Pro/swisstopo/SWISSTLM_arbres_maquette/swissTLM3D_TLM_EINZELBAUM_GEBUESCH.shp'
    fn_dst = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/meyrin_arbres.shp'
    
    req = f'{ogr2ogr} -spat {xmin} {ymin} {xmax} {ymax} -f "ESRI shapefile" "{fn_dst}" "{fn_src}"'
    #print(req)
    
    result = subprocess.run(req,shell=True,text=True, capture_output=True)
    
    print("stdout:", result.stdout)
    print("stderr:", result.stderr)
    
    if os.path.isfile(fn_dst):
        print('ok')


    


# Execute main()
if __name__=='__main__':
    main()