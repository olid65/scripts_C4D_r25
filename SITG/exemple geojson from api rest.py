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
    url = 'https://ge.ch/sitgags1/rest/services/VECTOR/SITG_GEOSERVICEDATA/MapServer/7048/query?where=&text=&objectIds=&time=&geometry=2465789.4328%2C1086777.4394%2C2531325.5829%2C1155694.86&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=geojson'
    req = urllib.request.Request(url=url)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    
    fn = '/Users/olivierdonze/Documents/Mandats/AGGLO_maquettes_PACA/SIG/PACA.geojson'
    with open(fn,'w') as f:
        f.write(json.dumps(data))
        
    
    
# Execute main()
if __name__=='__main__':
    main()