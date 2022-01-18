import c4d
import json

import subprocess
import sys




# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    
    fn = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/St_Cergue/extraction_swisstopo/swissimage-dop10_10cm.vrt'
    req = f'/Applications/QGIS.app/Contents/MacOS/bin/gdalinfo -json {fn}'
    result = subprocess.run(
        req, capture_output=True, text=True, shell = True
        )
    res = json.loads(result.stdout)
    corners = res['cornerCoordinates']
    print(corners['upperLeft'],corners['lowerLeft'],corners['lowerRight'],corners['upperRight'])
    
    #print("stderr:", result.stderr)

# Execute main()
if __name__=='__main__':
    main()