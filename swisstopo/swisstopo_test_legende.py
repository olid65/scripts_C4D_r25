import c4d
import urllib


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    url = 'https://wms.geo.admin.ch/'
    layer = 'ch.swisstopo.geologie-geologischer_atlas'
    
    fn_dst = '/Users/olivierdonze/Documents/TEMP/legende.png'
    xmin,ymin,xmax,ymax = 2534072.950785629,1158581.16976318,2538632.3862751676,1162130.4039177466
    width = 1024
    height = 1024
    url = f"https://wms.geo.admin.ch/?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.3.0&LAYERS={layer}&STYLES=default&LANG=fr&CRS=EPSG:2056&WIDTH={width}&{height}=582&FORMAT=image/png"
    print(url)
    data = urllib.parse.urlencode({ 'service': "wms",
                                    'request':'GetLegenGraphic',
                                    'version': 1.3,
                                    'layers':layer,
                                    'styles':'default',
                                    'lang':'fr',
                                    'EPSG':2056,
                                    'bbox':f'{xmin},{ymin},{xmax},{ymax}',
                                    'width':width,
                                    'height':height,
                                    'format':'image/png'
                                    })
                                    
    data = data.encode('ascii')
    
    response = urllib.request.urlopen(url)
    #print(response.read())
    #print(response.info())
    #if response.getcode() == 200:
    with open(fn_dst, 'wb') as localFile:
        localFile.write(response.read())
    return
    for t in dir(response):
        print(t)
    
    #?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.3.0&LAYERS={lyr.name}&STYLES=default&LANG=fr&CRS=EPSG:2056&BBOX={xmin},{ymin},{xmax},{ymax}&WIDTH={width}&{height}=582&FORMAT=image/png

# Execute main()
if __name__=='__main__':
    main()