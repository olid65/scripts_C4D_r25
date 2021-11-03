import c4d
import csv


""" Il faut importer le fbx que l'on peut télécharger sur :
   https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model.fbx
   et sélectionner l'objet polygonal
   
   Il y a une différence de 10 points entre le modèle et le landmark que je ne comprends pas ...."""

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

#ce facteur d'agrandissement dépend de la vue
FACTEUR = 50

# Main function
def main():
    fn = '/Users/olivierdonze/switchdrive/PYTHON/OpenCV/openCV_and_AI/face_mesh_points.csv'
    
    #on prend le point 0 du modèle (centre bouche sup)
    #comme point de reference
    
    centre = op.GetPoint(0)
    
    with open(fn) as csvfile:
        spamreader = csv.reader(csvfile)
        pts = []
        for row in spamreader:
            x,y,z = [float(v) for v in row]
            pts.append(c4d.Vector(x,-y,z)*FACTEUR)
    
    dif = pts[0]-op.GetPoint(0)
    pts = [p-dif for p in pts]
    #pts.reverse()  
    op.SetAllPoints(pts[:op.GetPointCount()])
    op.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()
    

# Execute main()
if __name__=='__main__':
    main()