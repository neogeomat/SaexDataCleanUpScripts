import tkMessageBox
import arcpy
import os
import time
import shared_data

def Remove_Identical_Feature(self):  # sourcery skip
    startTime = time.time ()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_identical.csv","a")
    count = 0

    for i in mdb_list:
        count +=1
        try:
            arcpy.DeleteIdentical_management(i+"\\Construction",["Shape_Area","Shape_Length","ParFID"])
            #arcpy.DeleteIdentical_management(i+"\\Parcel",["Shape_Area","Shape_Length","PARCELNO"])
        except:
            exception_list.write("Remove Identical Feature Error for ," + i + "\n")
            print("Remove Identical Feature error for "+i)
        print (i + " (" + str(count) + "/" + str(len(mdb_list)) + ")")
    print("Remove Identical Feature process complete")
    exception_list.close()
    print ('The script took {0} second !'.format(time.time() - startTime))

    tkMessageBox.showinfo(title="Remove Identical Feature" + version, message="Done")
