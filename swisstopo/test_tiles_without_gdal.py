import c4d,os
from glob import glob
import imghdr
import math

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True


import sys

sys.path.append('/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R25_EBA43BEE/library/scripts')

import C4DGIS.core.lib.Tyf as Tyf

#import C4DGIS.core.utils.bbox as bbox


class Bbox():

    def __init__(self, xmin,ymin,xmax,ymax):
        self.xmin,self.ymin,self.xmax,self.ymax = xmin,ymin,xmax,ymax


    def overlap(self, bb):
        '''Test if 2 bbox objects have intersection areas (in 2D only)'''
        def test_overlap(a_min, a_max, b_min, b_max):
            return not ((a_min > b_max) or (b_min > a_max))
        return test_overlap(self.xmin, self.xmax, bb.xmin, bb.xmax) and test_overlap(self.ymin, self.ymax, bb.ymin, bb.ymax)

    def get_intersection(self,bb):
        if self.overlap(bb):
            return Bbox(max((self.xmin,bb.xmin)),max((self.ymin,bb.ymin)),min((self.xmax,bb.xmax)),min((self.ymax,bb.ymax)))
        return None

    def __str__(self):
        return f"xmin: {round(self.xmin,3)}, ymin: {round(self.ymin,3)}, xmax: {round(self.xmax,3)}, ymax: {round(self.ymax,3)}"

def infoGeoTif(fn):
    tif = Tyf.open(fn)[0]
    size = tif['ImageWidth'], tif['ImageLength']
    nbBands = tif['SamplesPerPixel']
    depth = tif['BitsPerSample']
    print(depth)
    #print(float(tif['GDAL_NODATA']))
    #print(tif['ModelTransformationTag'])
    print(tif['ModelTiepointTag'])
    print(tif['ModelPixelScaleTag'])
    print(size)


def adaptBbox(xmin,ymin,xmax,ymax,taille_px):
    """Pour adapter la bbox au pixel inférieur (min) ou supérieur (max)"""
    facteur = 1./taille_px

    xmin = math.floor(xmin*facteur)/facteur
    ymin = math.floor(ymin*facteur)/facteur

    xmax = math.ceil(xmax*facteur)/facteur
    ymax = math.ceil(ymax*facteur)/facteur

    return xmin,ymin,xmax,ymax



# Main function
def main():
    path = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Martigny/swissimage-dop10_10cm'
    path = '/Users/olivierdonze/Documents/TEMP/test_dwnld_swisstopo/Onex/extraction/swissalti3d_50cm'

    xmin,ymin,xmax,ymax = 2496201.6689999998,1115075.5944229236,2497224.8595138337,1115711.0410632398

    taille_px = 0.5

    #Adaptation à la taille du pixel : on prend plus que la zone pour tomber sur le prochain pixel
    xmin,ymin,xmax,ymax = adaptBbox(xmin,ymin,xmax,ymax,2)

    bbx = Bbox(xmin,ymin,xmax,ymax)
    print(bbx)
    px_width = (xmax-xmin)/taille_px
    print(px_width)

    px_height = (ymax-ymin)/taille_px
    print(px_height)
    print('-----------------------')

    # 'swissalti3d', 'swissimage-dop10'

    for fn in glob(os.path.join(path,'*.tif')):
        #infoGeoTif(fn)
        name = os.path.basename(fn)

        index = name.rfind('-')
        xmin_tile = float(name[index-4:index])*1000
        ymin_tile = float(name[index+1:index+5])*1000
        xmax_tile = xmin_tile+1000
        ymax_tile = ymin_tile+1000


        bbx_tile = Bbox(xmin_tile,ymin_tile,xmax_tile,ymax_tile)

        intersect = bbx.get_intersection(bbx_tile)

        if intersect:
            print(name)
            print(bbx_tile)
            print(intersect)
            print('---')





# Execute main()
if __name__=='__main__':
    main()