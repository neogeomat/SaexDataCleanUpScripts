import sys
import tkMessageBox
import arcpy
import shared_data
import os
import time


def Generalize(self,tolerance):  # sourcery skip
    startTime = time.time ()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_generalize.csv","a")
    count = 0

    for i in mdb_list:
        count +=1
        try:
            Folder_Location = "d:"
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            if (os.path.exists(DataCleanTemp)):  # delete folder if exits, otherwise it causes error
                arcpy.Delete_management(DataCleanTemp, "Folder")
            arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
            arcpy.env.workspace = DataCleanTemp
            arcpy.env.overwriteOutput = True

            Data_Location = i
            option_choosed = self.variable.get()
            blank_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\" + option_choosed

            if (os.path.exists(blank_data)):
                BLANK84_Template = blank_data
            else:
                print("Blank Template database not found, install saex")
                exit()

            # Process: Copy Features
            arcpy.CopyFeatures_management(i + "\\Parcel", DataCleanTemp + "\\Parcel_to_Simplify", "", "0", "0","0")

            arcpy.SimplifyPolygon_cartography(i + "\\Parcel",DataCleanTemp+"\\Simplified_2","POINT_REMOVE",tolerance, "0 SquareMeters", "RESOLVE_ERRORS", "NO_KEEP", "")

            arcpy.Delete_management(i + "\\Parcel")

            # Process: Copy Features
            arcpy.CopyFeatures_management(BLANK84_Template + "\\Parcel", i + "\\Parcel", "", "0", "0","0")
            # Process: Append
            arcpy.Append_management(DataCleanTemp + "\\Simplified_2.shp", i + "\\Parcel", "NO_TEST")

            ## remove processing folder
            # Process: Delete
            arcpy.Delete_management(DataCleanTemp, "Folder")

            arcpy.Compact_management(i)
        except:
            exception_list.write("Generalize Error for ," + i + "\n")
            print("Generalize error for "+i+"\nError=\n\n",sys.exc_info())
        print (i + " (" + str(count) + "/" + str(len(mdb_list)) + ")")
    print("Generalize process complete")
    exception_list.close()
    print ('The script took {0} second !'.format(time.time() - startTime))

    tkMessageBox.showinfo(title="Generalize database", message="Done")
