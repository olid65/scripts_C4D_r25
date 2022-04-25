import c4d
from c4d import gui
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

# Main function
def main():

    fn_in = '/Users/olivierdonze/Downloads/swissBUILDINGS3D_3-0_1300-22.gdb'

    table_name = 'Building_solid'
    fn_out = f'/Users/olivierdonze/Documents/TEMP/swissbuildings3_tests/ogr/swissbuildings_3_{table_name}.shp'
    #ogr2ogr extracted.shp original_data.gdb
    req = f'ogr2ogr -overwrite -progress -skipfailures "{fn_out}" "{fn_in}" "{table_name}"'
    print(req)
    
    fn_in = fn_out
    fn_out = fn_in.replace('.shp','_test.geojson')
    req = f'ogr2ogr -overwrite -progress -skipfailures "{fn_out}" "{fn_in}"'
    print(req)

# Execute main()
if __name__=='__main__':
    main()