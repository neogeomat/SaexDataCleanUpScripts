import tkMessageBox
import arcpy
import os
import time
import shared_data
def recalculate_extent(self):  # sourcery skip
    arcpy.env.overwriteOutput = True
    startTime = time.time ()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_recalculate_extent.csv","a")
    count = 0
    for i in mdb_list:
        count +=1
        feature_classes = []
        walk = arcpy.da.Walk(i, datatype="FeatureClass")
        for dirpath, dirnames, filenames in walk:
             for filename in filenames:
                 feature_classes.append(os.path.join(dirpath, filename))
        try:
            for feature in feature_classes:
                # print feature
                arcpy.RecalculateFeatureClassExtent_management(feature)
        except:
            exception_list.write("Extent ReCalculation Error for ," + i + "\n")
            print("Extent ReCalculation error for "+i)
        print (i + " (" + str(count) + "/" + str(len(mdb_list)) + ")")
    print("Extent ReCalculation process complete")
    exception_list.close()
    print ('The script took {0} second !'.format(time.time() - startTime))

    tkMessageBox.showinfo(title="Extent ReCalculation database", message="Done")
