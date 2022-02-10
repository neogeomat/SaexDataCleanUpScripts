import csv, arcpy, os
import sys

from arcpy import env
import re

# Change workspace to your folder location
# Copy Group.lyr and Parcel.lyr to that Location
#__location__ = sys.argv[0]
#print __location__

env.workspace = "D:\\Bhaktapur20771213\\phat_5\\Final_Dibyashwori"
path = env.workspace

datasetList = arcpy.ListDatasets('*', 'Feature')
mxd = arcpy.mapping.MapDocument('CURRENT')
# mxd = arcpy.mapping.MapDocument('D:/data/new.mxd')
df = arcpy.mapping.ListDataFrames(mxd)[0]
mxd.activeView = df.name


#groupLayer = arcpy.mapping.Layer(os.path.join(__location__, r'Group.lyr'))
#parcelLayer = arcpy.mapping.Layer(os.path.join(__location__, r'Parcel.lyr'))
groupLayer = arcpy.mapping.Layer(env.workspace + r'\Group.lyr')
parcelLayer = arcpy.mapping.Layer(env.workspace + r'\Parcel.lyr')
ward_list = []
count = 0
# total_list = arcpy.ListWorkspaces("*", "Access") # doesn't loop inside folders
mdb_list = []
# exception_list= open(path+"\\exception_list_check_attr.csv","a")
# exception_list.truncate(0)
for root, dirnames, filenames in os.walk(path):
    for filename in filenames:
        if filename.endswith('.mdb'):
            mdb_list.append(os.path.join(root, filename))
total_list = mdb_list # imported folder traveser code of mdb_list into total_list
print(total_list)
total_count = len(total_list)
for fc in total_list:
    arcpy.env.workspace = fc
    count += 1
    new_name = os.path.basename(fc)
    new_filename = new_name.replace(" ", "")
    x = re.findall("^...[A-Za-z][A-Za-z\s_-]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
    ward = x[0][0]
    sheet = x[0][0] + x[0][1] + x[0][2]
    if not ward in ward_list:
        ward_list.append(ward)
        grp_lyr = groupLayer
        grp_lyr.name = ward
        arcpy.mapping.AddLayer(df, grp_lyr, "BOTTOM")
    sub_grp_lyr = groupLayer
    sub_grp_lyr.name = sheet
    targetGroupLayer = arcpy.mapping.ListLayers(mxd, ward, df)[0]
    arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, sub_grp_lyr, "BOTTOM")

    fcl = arcpy.ListFeatureClasses("*", "All")
    # fcl = arcpy.ListFeatureClasses("Parcel", "All")
    for feature in fcl:
        targetSubGroupLayer = arcpy.mapping.ListLayers(mxd, sheet, df)
        # print('\n'.join(map(str, targetSubGroupLayer)))
        pathToFC = arcpy.env.workspace + '/' + feature
        newlayer = arcpy.mapping.Layer(pathToFC)
        #if str(feature).startswith("Parce") and str(feature).endswith("arcel"):
            # print "Apply"+feature
            #arcpy.ApplySymbologyFromLayer_management(newlayer, parcelLayer)
        arcpy.mapping.AddLayerToGroup(df, targetSubGroupLayer[0], newlayer, "BOTTOM")

        # arcpy.mapping.AddLayer(df,newlayer,"BOTTOM")
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        mxd.save()
    print (fc + " (" + str(count) + "/" + str(total_count) + ")")

# execfile(r'G:\My Drive\dosamritkarma\CAS\pravesh\pythonscript\DataCleanUpScripts\create_mxd.py')
