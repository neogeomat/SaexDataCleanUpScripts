import tkMessageBox
import arcpy
import os
import time
import shared_data
def Repair_Geometry(self):  # sourcery skip
    startTime = time.time ()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_repair.csv","a")
    count = 0

    for i in mdb_list:
        count +=1
        try:
            arcpy.RepairGeometry_management(i+"\\Parcel")
            arcpy.RepairGeometry_management(i+"\\Construction")
        except:
            exception_list.write("Repair Geometry Error for ," + i + "\n")
            print("Repair Geometry error for "+i)
        print (i + " (" + str(count) + "/" + str(len(mdb_list)) + ")")
    print(" Repair Geometry process complete")
    exception_list.close()
    print ('The script took {0} second !'.format(time.time() - startTime))

    tkMessageBox.showinfo(title="Repair Geometry" , message="Done")
