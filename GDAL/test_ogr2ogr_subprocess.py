import c4d
import subprocess


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    
    path_ogr2ogr = '/Applications/QGIS.app/Contents/MacOS/bin/ogr2ogr'
    path_ogrinfo = '/Applications/QGIS.app/Contents/MacOS/bin/ogrinfo'
    
    

    
    #Exemple clause where -> extraction des 3 catégories de foret dans le swissTLM3D
    src = '/Volumes/My Passport Pro/swisstopo/2021_SWISSTLM3D_SHP_CHLV95_LN02/TLM_BB/swissTLM3D_TLM_BODENBEDECKUNG_west.shp'
    dst = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/wald_west.shp'
    
    req = f'''"{path_ogr2ogr}" \
               -where "\"OBJEKTART\"=\'Wald\' OR  \"OBJEKTART\"=\'Wald offen\' OR \"OBJEKTART\"=\'Gebueschwald\'"\
               "{dst}" \
               "{src}"'''
    
    
    
    
    #Exemple clip avec boundinbox
    xmin,ymin,xmax,ymax = 2567370.0,1107818.0,2571388.0,1109930.0
    
    src = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/wald_west.shp'
    dst = '/Users/olivierdonze/Documents/TEMP/swisstopo_abres/wald_west_decoupe.shp'
    
    #-clipsrc -> découpe
    #-spat -> prend toutes les entités touchées par la bbox
    
    req = f'''"{path_ogr2ogr}" \
               -clipsrc {xmin} {ymin} {xmax} {ymax} \
               "{dst}" \
               "{src}"'''
    
    
    
    print(req)          
    output = subprocess.check_output(req,shell=True)
    print(output)

# Execute main()
if __name__=='__main__':
    main()