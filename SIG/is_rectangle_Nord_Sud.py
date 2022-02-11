import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def isRectangleNordSud(sp):
    if sp.GetPointCount()!= 4:
        return False
    
    p1,p2,p3,p4 = [p*sp.GetMg() for p in sp.GetAllPoints()]
    
    for p1,p2 in zip([p1,p2,p3,p4],[p2,p3,p4,p1]):
        v = p2-p1
        
        if v.x !=0 and v.z !=0:
            return False
    return True



# Main function
def main():
    sp = op.GetRealSpline()
    
    if not sp :
        return
    
    print(isRectangleNordSud(sp))

# Execute main()
if __name__=='__main__':
    main()