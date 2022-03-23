import c4d
import urllib.request
import json

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    url = 'https://api3.geo.admin.ch/rest/services/api/MapServer?lang=fr'
    
    with urllib.request.urlopen(url) as site :
        data = json.loads(site.read())
        for layer in data['layers']:
            print(layer['layerBodId'])
            
    
    
# Execute main()
if __name__=='__main__':
    main()