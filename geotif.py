import c4d
import struct

#https://www.adobe.io/content/dam/udp/en/open/standards/tiff/TIFF6.pdf -> pour le tif
#https://www.usna.edu/Users/oceano/pguth/md_help/html/tbme9v52.htm -> pour le geoTitt
#https://www.mattbrealey.com/articles/reading-tiff-tags/

#Attention ne fonctionne pas avec les tuiles mnt de swisstopo -> why ???!!!
#par contre fonctionne avec résultat du mnt Rest World d'Esri

#https://medium.com/planet-stories/reading-a-single-tiff-pixel-without-any-tiff-tools-fcbd43d8bd24



def getCalageFromGeoTif(fn):
    """retourne la valeur du pixel en x et y et la position du coin en haut à gauche en x et y
       attention c'est bien le coin du ratser et pas le centre du pixel
       Ne fonctionne pas avec les rasters tournés, fonctionne bien avec les MNT de l'API REST d'ESRI
       Ne fonctionne pas avec les tuiles du MNT de swisstopo"""

    #voir page 16 pdf description tiff
    #et sur https://docs.python.org/3/library/struct.html pour les codes lettres de struct
    #le nombre en clé représente le type selon description du tif
    # le tuple en valeur représente le nombre d'octets (bytes) et le code utilissé pour unpacker
    # il y en a quelques un dont je ne suis pas sûr !
    dic_types = {1:(1,'x'),
                 2:(1,'c'),
                 3:(2,'h'),
                 4:(4,'l'),
                 5:(8,'ll'),
                 6:(1,'b'),
                 7:(1,'b'),
                 8:(2,'h'),
                 9:(4,'i'),
                 10:(8,'ii'),
                 11:(4,'f'),
                 12:(8,'d'),}

    with open(fn,'rb') as f:
        #le premier byte sert à savoir si on es en bigendian ou pas
        r = f.read(2)
        big = True
        if r == b'II':
            big = False
        if big : big ='>'
        else : big = '<'
        #ensuite on a un nombre de verification ? -> normalement 42  sinon 43 pour les bigTiff
        #le second c'est le début du premier IFD (image file directory) en bytes -> 8 en général (commence à 0)
        s = struct.Struct(f"{big}Hl")
        rec = f.read(6)
        #print(s.unpack(rec))

        #début de l'IFD' normalement commence à 8
        #nombre de tags
        s = struct.Struct(f"{big}H")
        rec = f.read(2)
        nb_tag, = s.unpack(rec)
        dic_tags = {}
        for i in range(nb_tag):
            s = struct.Struct(f"{big}HHlHH")
            rec = f.read(12)
            no,typ,nb,value,xx = s.unpack(rec)
            #print(no,typ,nb,value,xx)
            dic_tags[no] = (typ,nb,value,xx)

        #4 bytes pour si on a plusieurs IFD
        s = struct.Struct(f"{big}l")
        rec = f.read(4)

        #VALEUR DES PIXELS
        t = dic_tags.get(33550,None)
        val_px = []
        if t:
            typ,nb,offset,xx = t
            f.seek(offset)
            nb_bytes,code = dic_types.get(typ,None)
            for i in range(nb):
                s = struct.Struct(f"{big}{code}")
                rec = f.read(nb_bytes)
                [val] = s.unpack(rec)
                val_px.append(val)
        val_px_x,val_px_y,v_z = val_px

        #MATRICE DE CALAGE (coin en bas à gauche)
        t = dic_tags.get(33922,None)
        mat_calage = []
        if t:
            typ,nb,offset,xx = t
            f.seek(offset)
            nb_bytes,code = dic_types.get(typ,None)
            for i in range(nb):
                s = struct.Struct(f"{big}{code}")
                rec = f.read(nb_bytes)
                [val] = s.unpack(rec)
                mat_calage.append(val)
        coord_x = mat_calage[3]
        coord_y = mat_calage[4]

        #PROJECTION (pas utilisée pour l'instant dans la fonction)
        t = dic_tags.get(34737,None)
        if t:
            typ,nb,offset,xx = t
            f.seek(offset)
            nb_bytes,code = dic_types.get(typ,None)
            geoAscii = ''
            for i in range(nb):
                s = struct.Struct(f"{big}{code}")
                rec = f.read(nb_bytes)
                [car] = s.unpack(rec)
                geoAscii+=car.decode('utf-8')

        return val_px_x,val_px_y,coord_x,coord_y

def main():
    fn = '/Users/donzeo/Documents/TEMP/test.tif'
    fn = '/Users/donzeo/Downloads/exportImage.tif'
    fn ='/Users/donzeo/Downloads/_ags_0dd0a8a6_18c4_4024_9100_4ef1d4813bef.tif'
    fn ='/Users/olivierdonze/Downloads/exportImage(1).tiff'
    fn = '/Users/olivierdonze/Downloads/exportImage(2).tiff'
    fn = '/Users/olivierdonze/Downloads/exportImage(3).tiff'

    print(getCalageFromGeoTif(fn))


# Execute main()
if __name__=='__main__':
    main()