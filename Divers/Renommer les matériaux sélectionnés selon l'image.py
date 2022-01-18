import c4d
import os


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():
    for mat in doc.GetActiveMaterials():
        shd = mat[c4d.MATERIAL_COLOR_SHADER]
        if shd and shd.CheckType(c4d.Xbitmap):
            fn = shd[c4d.BITMAPSHADER_FILENAME]
            if fn:
                name = os.path.basename(fn)[:-4]
                mat.SetName(name)
    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()