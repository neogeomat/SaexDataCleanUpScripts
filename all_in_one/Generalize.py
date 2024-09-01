import sys
import tkMessageBox
import arcpy
import shared_data
import os
import time

def Generalize(self, tolerance, status_update=None, show_messagebox=True):
    """Generalize the features in the database files, update status using the provided function, and optionally show a message box."""
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(path + "\\exception_list_generalize.csv", "a")
    count = 0

    if status_update:
        status_update("Starting generalization process...")

    for i in mdb_list:
        filename = os.path.basename(i)
        count += 1
        print ("Generalizing in {} \n({}/{})".format(filename, count, len(mdb_list)))
        try:
            if status_update:
                status_update("Generalizing in {0} \n({1}/{2})".format(filename, count, len(mdb_list)))

            Folder_Location = "d:"
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            if os.path.exists(DataCleanTemp):  # delete folder if it exists, otherwise it causes error
                arcpy.Delete_management(DataCleanTemp, "Folder")
            arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
            arcpy.env.workspace = DataCleanTemp
            arcpy.env.overwriteOutput = True

            Data_Location = i
            option_choosed = self.variable.get()
            blank_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\" + option_choosed

            if os.path.exists(blank_data):
                BLANK84_Template = blank_data
            else:
                print("Blank Template database not found, install saex")

            # Process: Copy Features
            arcpy.CopyFeatures_management(i + "\\Parcel", DataCleanTemp + "\\Parcel_to_Simplify", "", "0", "0", "0")

            arcpy.SimplifyPolygon_cartography(i + "\\Parcel", DataCleanTemp + "\\Simplified_2", "POINT_REMOVE", tolerance, "0 SquareMeters", "RESOLVE_ERRORS", "NO_KEEP", "")

            arcpy.Delete_management(i + "\\Parcel")

            # Process: Copy Features
            arcpy.CopyFeatures_management(BLANK84_Template + "\\Parcel", i + "\\Parcel", "", "0", "0", "0")

            # Process: Append
            arcpy.Append_management(DataCleanTemp + "\\Simplified_2.shp", i + "\\Parcel", "NO_TEST")

            # Remove processing folder
            arcpy.Delete_management(DataCleanTemp, "Folder")

            arcpy.Compact_management(i)

        except Exception as e:
            exception_list.write("Generalize Error for: " + i + "\n")
            print("Generalize error for " + i + "\nError=\n\n", sys.exc_info())
            if status_update:
                status_update("Error processing {}: {}".format(filename, str(e)))

        if status_update:
            status_update("{} \n({}/{}) processed".format(filename, count, len(mdb_list)))

    print("Generalize process complete")
    exception_list.close()

    if status_update:
        status_update("Generalize process complete. Check exception_list_generalize.csv for errors.")

    print('The script took {0} seconds!'.format(time.time() - startTime))

    if show_messagebox:
        tkMessageBox.showinfo(title="Generalize database", message="Generalization process is complete.")
