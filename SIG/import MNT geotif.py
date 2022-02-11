
import c4d
import struct

"""Attention ne lit pas (encore l'entete il faut conna^itre la valeur du pixel"""
VAL_PX = 0.5


def main():
    # Opens a Dialog to choose a picture file
    #path = '/Users/donzeo/Downloads/_ags_0dd0a8a6_18c4_4024_9100_4ef1d4813bef.tif'
    path = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Please Choose a 32-bit Image:")
    
    bmp = c4d.bitmaps.BaseBitmap()
    bmp.InitWith(path)
    
    width, height = bmp.GetSize()
    print(bmp.GetSize())
    bits = bmp.GetBt()
    inc = bmp.GetBt() // 8
    bytesArray = bytearray(inc)
    memoryView = memoryview(bytesArray)
    i=0
    
    nb_pts = width*height
    nb_polys = (width-1)*(height-1)
    poly = c4d.PolygonObject(nb_pts,nb_polys)
    pts = []
    polys =[]
    pos = c4d.Vector(0)
    i = 0
    id_poly =0
    
    for line in range(height):
        for row in range(width):
            bmp.GetPixelCnt(row, line, 1, memoryView, inc, c4d.COLORMODE_GRAYf, c4d.PIXELCNT_0) 
            [y] = struct.unpack('f', bytes(memoryView[0:4]))
            pos.y = y
            pts.append(c4d.Vector(pos))
            pos.x+=VAL_PX
            
            if line >0 and row>0:
                c=i
                b=i-width
                a=b-1
                d = i-1
                
                poly.SetPolygon(id_poly,c4d.CPolygon(a,b,c,d))
                id_poly+=1
                
            i+=1
            
        pos.x = 0
        pos.z-= VAL_PX
    
    poly.SetAllPoints(pts)
    poly.Message(c4d.MSG_UPDATE)
    
    doc.InsertObject(poly)
    c4d.EventAdd()


if __name__ == '__main__':
    main()