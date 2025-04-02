import time
import tkMessageBox
import arcpy
import shared_data
import os as os
from csv_logging import write_error_to_csv, create_csv_log_file

def merge_dummy_planning(self,choosen_meridian,status_update=None, show_messagebox=True, update_progress=None):
    starttime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(os.path.join(path, "exception_list_dummy.csv"), "a")
    exception_list.truncate(0)

    blank_mdb_path = r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates'
    blank_mdb =os.path.join(blank_mdb_path,choosen_meridian)
    error_log_path = os.path.join(shared_data.directory, "error_log.csv")
    # Create and open the CSV file for error logging
    file_handler, csv_writer = create_csv_log_file(error_log_path)

    count = 1
    total_mdbs = len(shared_data.filtered_mdb_files)

    for progress, i in enumerate(mdb_list, start=1):
        filename = os.path.basename(i)
        if status_update:
                status_update("merging Dummy Plannnings for {} \n({}/{})".format(filename, count, total_mdbs))
        try:
            arcpy.env.workspace = i

            Folder_Location = "d:"
            Data_Location = i
            basename = os.path.basename(Data_Location)

            print("Checking Dummy Merge for: "+ basename)

            if (os.path.exists(blank_mdb)):
                BLANK84_Template = blank_mdb
            else:
                print("Blank Template database not found, install saex")
                exit()
            # Process: Create Temp Folder to strore all processing intermediaries
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            if (os.path.exists(DataCleanTemp)): # delete folder if exits, otherwise it causes error
                arcpy.Delete_management(DataCleanTemp, "Folder")
            arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            file_id = i[-12:-4]
            arcpy.CreateFolder_management(DataCleanTemp, file_id)
            DataCleanTemp = DataCleanTemp + "\\" + file_id
            arcpy.env.workspace = DataCleanTemp

            arcpy.FeatureClassToFeatureClass_conversion(Data_Location + "\\Parcel", DataCleanTemp, "Parcel.shp")

            Parcel = DataCleanTemp + "\\Parcel.shp"
            # Process: Feature To Point
            arcpy.FeatureToPoint_management(Parcel, DataCleanTemp + "\\ParcelCentroid.shp", "INSIDE")

            # Process: Select Layer By Attribute
            temp = "temp" + file_id
            arcpy.MakeFeatureLayer_management(Parcel, temp)
            arcpy.SelectLayerByAttribute_management(temp, 'NEW_SELECTION', 'PARCELNO < 9000 AND PARCELNO <> 0')

            # arcpy.SelectLayerByAttribute_management("tempInvert", "SWITCH_SELECTION")
            # Process: Dissolve
            arcpy.Dissolve_management(temp, DataCleanTemp + "\\ParcelDissolve.shp", "PARCELNO;DISTRICT;VDC;WARDNO;GRIDS1", "", "SINGLE_PART", "DISSOLVE_LINES")
            arcpy.MakeFeatureLayer_management(Parcel, temp +"invert","PARCELNO >= 9000 OR PARCELNO = 0")
            arcpy.SelectLayerByAttribute_management(temp + "invert", "NEW_SELECTION", "PARCELNO >= 9000 OR PARCELNO = 0")
            arcpy.CopyFeatures_management(temp + "invert", DataCleanTemp + "\\ParcelRemain.shp")

            # Join management
            arcpy.SpatialJoin_analysis(DataCleanTemp + "\\ParcelDissolve.shp", DataCleanTemp + "\\ParcelCentroid.shp", DataCleanTemp + "\\NewJoinedData.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL","PARCELNO \"PARCELNO\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,DISTRICT,-1,-1;VDC \"VDC\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,GRIDS1,-1,-1;PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelCentroid.shp,PARCELKEY,-1,-1;PARCELTY \"PARCELTY\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelCentroid,shp,PARCELTY,-1,-1;ParcelNote \"ParcelNote\" true true false 200 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelCentroid.shp,ParcelNote,-1,-1", "CONTAINS", "", "")

            arcpy.Delete_management(Data_Location + "\\Parcel")
            # Process: Copy Features
            arcpy.CopyFeatures_management(BLANK84_Template + "\\Parcel", Data_Location + "\\Parcel")
            arcpy.Append_management(DataCleanTemp + "\\NewJoinedData.shp", Data_Location + "\\Parcel", "NO_TEST")
            arcpy.Append_management(DataCleanTemp + "\\ParcelRemain.shp", Data_Location + "\\Parcel", "NO_TEST")

        except Exception as e:

            exception_list.write("Gap Overlap Error for ," + i + "\n")
            write_error_to_csv(csv_writer, os.path.basename(i), str(e))

            print ("error for " + i)

            if status_update:
                status_update("Error during processing: {}".format(str(e)))
            if show_messagebox:
                tkMessageBox.showerror(title="Error", message="An error occurred: {}".format(str(e)))

        if update_progress:
            x= progress/float(total_mdbs)
            progress_value = (x) * 100
            update_progress(progress_value, total_mdbs)
        self.master.update_idletasks()  # Ensure GUI updates

    print("Merge Dummy Planning process complete")
