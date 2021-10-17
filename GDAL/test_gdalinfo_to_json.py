import c4d
import subprocess
import json


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    xml = '/Users/olivierdonze/Documents/Python/GDAL/SITG_ortho2020_wms.xml'
    args = ['/Applications/QGIS.app/Contents/MacOS/bin/gdalinfo', xml,'-json']
    proc = subprocess.Popen(args,  stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout,stderr=proc.communicate()
    
    #with open('/Users/olivierdonze/Documents/Python/GDAL/test_gdalinfo.json','w') as f:
        #f.write(stdout.decode('utf-8'))
        
    infos = json.loads(stdout.decode('utf-8'))
    
    for k,v in infos.items():
        print(k,v)
    print(infos)


# Execute main()
if __name__=='__main__':
    main()