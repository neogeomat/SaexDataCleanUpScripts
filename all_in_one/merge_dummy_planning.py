# -*- coding: utf-8 -*-
import re
import shutil
import time
import tkMessageBox
import arcpy
import shared_data
import os as os
from csv_logging import write_error_to_csv, create_csv_log_file
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

def merge_dummy_planning(self, choosen_meridian, status_update=None, show_messagebox=True, update_progress=None):
    starttime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(os.path.join(path, "exception_list_dummy.csv"), "a")
    exception_list.truncate(0)

    blank_mdb_path = r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates'
    blank_mdb = os.path.join(blank_mdb_path, choosen_meridian)
    error_log_path = os.path.join(shared_data.directory, "error_log.csv")
    # Create and open the CSV file for error logging
    file_handler, csv_writer = create_csv_log_file(error_log_path)

    count = 1
    total_mdbs = len(mdb_list)

    for progress, i in enumerate(mdb_list, start=1):
        filename = os.path.basename(i)
        if status_update:
            status_update("Merging Dummy Plannings for {} \n({}/{})".format(filename, count, total_mdbs))
        try:
            arcpy.env.workspace = i
            # Check if 'Parcel' layer exists in the current MDB
            feature_classes = arcpy.ListFeatureClasses()
            if "Parcel" not in feature_classes:
                exception_list.write("Invalid or incorrect MDB: 'Parcel' layer not found. {}\n".format(i))
                raise ValueError("Invalid or incorrect MDB: 'Parcel' layer not found.")

            Folder_Location = "d:"
            Data_Location = i
            basename = os.path.basename(Data_Location)

            print("Checking Dummy Merge for: " + basename)

            if not os.path.exists(blank_mdb):
                print("Blank Template database not found, install saex")
                exit()

            # Process: Create Temp Folder to store all processing intermediaries
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            safe_delete_folder(DataCleanTemp)

            create_clean_temp_folder(Folder_Location,"DataCleanTemp")

            file_id = re.sub(r'\W+', '', os.path.splitext(os.path.basename(i))[0])
            counter = 1

            # Generate a unique folder name if it already exists
            while os.path.exists(os.path.join(DataCleanTemp, file_id)):
                try:
                    arcpy.Delete_management(DataCleanTemp + "\\" +file_id)
                except:
                    file_id = file_id+"_"+counter
                    counter += 1

            DataCleanTempFile = DataCleanTemp + "\\" +file_id
            create_clean_temp_folder(DataCleanTemp,file_id)


            arcpy.env.workspace = DataCleanTempFile

            arcpy.FeatureClassToFeatureClass_conversion(Data_Location + "\\Parcel", DataCleanTempFile, "Parcel.shp")

            Parcel = DataCleanTempFile + "\\Parcel.shp"
            # Process: Feature To Point
            arcpy.FeatureToPoint_management(Parcel, DataCleanTempFile + "\\ParcelCentroid.shp", "INSIDE")

            # Process: Select Layer By Attribute
            temp = "temp" + file_id
            arcpy.MakeFeatureLayer_management(Parcel, temp)
            arcpy.SelectLayerByAttribute_management(temp, 'NEW_SELECTION', 'PARCELNO < 9000 AND PARCELNO <> 0')

            # Process: Dissolve
            arcpy.Dissolve_management(temp, DataCleanTempFile + "\\ParcelDissolve.shp", "PARCELNO;DISTRICT;VDC;WARDNO;GRIDS1", "", "SINGLE_PART", "DISSOLVE_LINES")
            arcpy.MakeFeatureLayer_management(Parcel, temp + "invert", "PARCELNO >= 9000 OR PARCELNO = 0")
            arcpy.SelectLayerByAttribute_management(temp + "invert", "NEW_SELECTION", "PARCELNO >= 9000 OR PARCELNO = 0")
            arcpy.CopyFeatures_management(temp + "invert", DataCleanTempFile + "\\ParcelRemain.shp")


            # Join management
            arcpy.SpatialJoin_analysis(DataCleanTempFile + "\\ParcelDissolve.shp", DataCleanTempFile + "\\ParcelCentroid.shp",
                                       DataCleanTempFile + "\\NewJoinedData.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       "", "CONTAINS", "", "")

            # Clear selection and delete layers referencing Parcel.shp
            try:
                arcpy.SelectLayerByAttribute_management(temp, "CLEAR_SELECTION")
            except:
                pass

            try:
                arcpy.Delete_management(temp)
            except:
                pass

            try:
                arcpy.Delete_management(temp + "invert")
            except:
                pass

            # Force garbage collection to release internal ArcPy references
            import gc
            gc.collect()

            # Optional but helpful to ensure ArcGIS clears in-memory locks
            arcpy.ClearWorkspaceCache_management()

            # Now it's safer to delete Parcel.shp
            arcpy.Delete_management(DataCleanTempFile + "\\Parcel.shp")

            # Process: Copy Features
            arcpy.CopyFeatures_management(blank_mdb + "\\Parcel", DataCleanTempFile + "\\Parcel.shp")
            arcpy.Append_management(DataCleanTempFile + "\\NewJoinedData.shp", Data_Location + "\\Parcel.shp", "NO_TEST")
            arcpy.Append_management(DataCleanTempFile + "\\ParcelRemain.shp", Data_Location + "\\Parcel.shp", "NO_TEST")

            safe_delete_folder(DataCleanTempFile)

        except Exception as e:
            exception_list.write("Gap Overlap Error for ," + i + "\n")
            write_error_to_csv(csv_writer, os.path.basename(i), str(e))

            print("Error for " + i)

            # Send Telegram notification for error
            error_message = "⚠️ Merge Dummy Planning Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: merge_dummy_planning\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, filename, str(e))
            send_telegram_message(error_message)

            if status_update:
                status_update("Error during processing: {}".format(str(e)))
            if show_messagebox and "Parcel" not in str(e):
                tkMessageBox.showerror(title="Error", message="An error occurred: {}".format(str(e)))

        if update_progress:
            x = progress / float(total_mdbs)
            progress_value = (x) * 100
            update_progress(progress_value, total_mdbs)
        self.master.update_idletasks()  # Ensure GUI updates

    # Send Telegram notification for successful processing
    success_message = "✅ Merge Dummy Planning Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: merge_dummy_planning\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - starttime)
    send_telegram_message(success_message)

    print("Merge Dummy Planning process complete")
    exception_list.close()




def safe_delete_folder(path):
    if os.path.exists(path):
        try:
            arcpy.ClearWorkspaceCache_management()
            arcpy.Delete_management(path, "Folder")
            time.sleep(1)
            if os.path.exists(path):  # Still exists? Force delete
                shutil.rmtree(path)
        except Exception as e:
            print("Error deleting folder {}: {}".format(path, str(e)))

def create_clean_temp_folder(base_path, subfolder_name):
    full_path = os.path.join(base_path, subfolder_name)
    safe_delete_folder(full_path)
    try:
        arcpy.CreateFolder_management(base_path, subfolder_name)
    except Exception as e:
        print("Failed to create folder {}: {}".format(full_path, str(e)))
    return full_path
