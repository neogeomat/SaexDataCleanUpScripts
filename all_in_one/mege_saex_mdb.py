# -*- coding: utf-8 -*-
import os
import shutil
import arcpy
import shared_data
import tkMessageBox as tkMessageBox
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications
import time

def mergeSaexMdbs(self,choosen_meridian):
    startTime = time.time()
    path = shared_data.directory
    exception_file_path = os.path.join(path, "exception_list_merge.csv")
    merged_file_name = "{}_merged.mdb".format(os.path.basename(path))
    merged_file_path = os.path.join(path, merged_file_name)
    blank_mdb_path = r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates'
    blank_mdb =os.path.join(blank_mdb_path,choosen_meridian)

    # Open exception list file with context manager
    try:
        with open(exception_file_path, "a") as exception_list:
            if os.path.exists(merged_file_path):
                os.remove(merged_file_path)
                print("Old merged file deleted")

            mdb_list = shared_data.filtered_mdb_files
            total_mdbs = len(mdb_list)

            try:
                shutil.copy(blank_mdb, merged_file_path)
                print("{} copied as {}".format(blank_mdb, merged_file_path))
            except IOError as e:
                exception_list.write("Unable to Copy Error for {}\n".format(path))
                print("Unable to copy file. {}".format(e))
            except Exception as e:
                exception_list.write("Unexpected Error for {}\n".format(path))
                print("Unexpected error: {}".format(e))

            arcpy.env.workspace = merged_file_path
            arcpy.AddField_management("Parcel", "source_file", "TEXT")

            layers = ["Parcel", "Segments", "Construction", "Parcel_History"]
            count = 0
            for i in mdb_list:
                arcpy.env.workspace = i
                count += 1
                print("{} ({}/{})".format(arcpy.env.workspace, count, total_mdbs))
                for l in layers:
                    try:
                        if l == "Parcel":
                            parcel_path = os.path.join(i, "Parcel")
                            arcpy.AddField_management(parcel_path, "source_file", "TEXT")
                            head, tail = os.path.split(i)
                            tail = tail.replace(" ", "")
                            location_str = str(tail[:-4])
                            arcpy.CalculateField_management(parcel_path, "source_file", "'{}'".format(location_str), "PYTHON")

                        layer_path = os.path.join(merged_file_path, l)
                        arcpy.Append_management(l, layer_path, "NO_TEST", "", "")
                        arcpy.DeleteField_management(l, ["source_file"])
                    except Exception as e:
                        exception_list.write("Merge Database Error for {}\n".format(i))
                        print("Error processing layer {} from {}: {}".format(l, i, e))
                        # Send Telegram notification for error
                        error_message = "⚠️ Merge Database Error!\n\n" \
                                        "🗂 Path: {}\n" \
                                        "📜 Script: Merge_Database\n" \
                                        "🗂 File: {}\n" \
                                        "❌ Error: {}".format(path, mdb_list, str(e))
                        send_telegram_message(error_message)

        print("Merge all data Process complete")
        tkMessageBox.showinfo(title="Merge Saex Mdb files", message="Done")
    except Exception as e:
        print("Failed to write to exception file: {}".format(e))
        # Send Telegram notification for error
        error_message = "⚠️ Merge Database Error!\n\n" \
                        "🗂 Path: {}\n" \
                        "📜 Script: Merge_Database\n" \
                        "🗂 File: {}\n" \
                        "❌ Error: {}".format(path, mdb_list, str(e))
        send_telegram_message(error_message)

    # Send Telegram notification for successful processing
    success_message = "✅ Merge Database Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Merge_Database\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)
