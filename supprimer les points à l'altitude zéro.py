import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

def select_pts_alt_0(op):
    bs = op.GetPointS()
    bs.DeselectAll()
    for i,p in enumerate(op.GetAllPoints()):
        if p.y == 0:
            bs.Select(i)

# Main function
def main():
    mode = doc.GetMode()
    select_pts_alt_0(op)
    c4d.CallCommand(12139) # Points
    c4d.CallCommand(12109) # Delete
    doc.SetMode(mode)
    c4d.EeventAdd()
    

# Execute main()
if __name__=='__main__':
    main()