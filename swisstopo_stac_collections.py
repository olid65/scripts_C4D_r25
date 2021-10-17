import c4d
import urllib.request
import json


#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.landeskarte-farbe-10 -> CN10
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.pixelkarte-farbe-pk25.noscale -> CN 25
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.pixelkarte-farbe-pk50.noscale -> CN 50
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d -> MNT
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissbuildings3d_2 -> bati3D
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissimage-dop10 -> ortho 10 cm ou 2m ?
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swisssurface3d-raster -> MNS
#https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swisssurface3d -> LIDAR

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    url = 'https://data.geo.admin.ch/api/stac/v0.9/collections'

    f = urllib.request.urlopen(url)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)
    for colection in json_res['collections']:
        print(colection['title'], colection['links'][0]['href']) #, colection['links'][0]['href']

# Execute main()
if __name__=='__main__':
    main()
