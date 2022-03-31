import c4d
import os
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

import sys
from pprint import pprint

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


# Main function
def main():  
    url = 'https://github.com/olid65/C4D_import_dwg_georef/archive/refs/heads/main.zip'
    path_dst = '/Users/olivierdonze/Documents/TEMP/Unzip'
    
    with urlopen(url) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(path_dst)
    
    return   
    path = os.path.join(c4d.storage.GeGetStartupWritePath(),'plugins')
    if os.path.isdir(path):
        for fn in os.listdir(path):
         print(fn)

# Execute main()
if __name__=='__main__':
    main()