# -*- coding: utf-8 -*-
import os
import shutil
import arcpy
import shared_data
import tkMessageBox as tkMessageBox
from send_notif_telegram import send_telegram_message
import time

def mergeSaexMdbs(self, choosen_meridian):
    startTime = time.time()
    path = shared_data.directory
    exception_file_path = os.path.join(path, "exception_list_merge.csv")
    failed_mdb_csv = os.path.join(path, "failed_mdb_list.csv")  # new CSV for MDBs that fail entirely
    merged_file_name = "{}_merged.mdb".format(os.path.basename(path))
    merged_file_path = os.path.join(path, merged_file_name)
    blank_mdb_path = r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates'
    blank_mdb = os.path.join(blank_mdb_path, choosen_meridian)

    # ✅ Delete old merged file first
    if os.path.exists(merged_file_path):
        try:
            os.remove(merged_file_path)
            print("Old merged file deleted: {}".format(merged_file_path))
        except Exception as e:
            print("❌ Failed to delete old merged file: {}".format(e))
            send_telegram_message(
                "⚠️ Failed to delete existing merged MDB!\n\n"
                "🗂 Path: {}\n"
                "📜 Script: Merge_Database\n"
                "❌ Error: {}".format(path, str(e))
            )
            return  # Stop here if we can't delete it

    try:
        with open(exception_file_path, "a") as exception_list, \
             open(failed_mdb_csv, "w") as failed_list:

            failed_list.write("Failed MDBs\n")  # CSV header

            mdb_list = shared_data.filtered_mdb_files
            total_mdbs = len(mdb_list)

            try:
                shutil.copy(blank_mdb, merged_file_path)
                print("{} copied as {}".format(blank_mdb, merged_file_path))
            except IOError as e:
                exception_list.write("Unable to Copy Error for {}\n".format(path))
                print("Unable to copy file. {}".format(e))
                return
            except Exception as e:
                exception_list.write("Unexpected Error for {}\n".format(path))
                print("Unexpected error: {}".format(e))
                return

            arcpy.env.workspace = merged_file_path
            arcpy.AddField_management("Parcel", "source_file", "TEXT")

            layers = ["Parcel", "Segments", "Construction", "Parcel_History"]
            count = 0

            for mdb in mdb_list:
                arcpy.env.workspace = mdb
                count += 1
                print("{} ({}/{})".format(arcpy.env.workspace, count, total_mdbs))

                mdb_failed = False  # track if this MDB fails

                for l in layers:
                    try:
                        if l == "Parcel":
                            parcel_path = os.path.join(mdb, "Parcel")
                            arcpy.AddField_management(parcel_path, "source_file", "TEXT")
                            head, tail = os.path.split(mdb)
                            tail = tail.replace(" ", "")
                            location_str = str(tail[:-4])
                            arcpy.CalculateField_management(parcel_path, "source_file", "'{}'".format(location_str), "PYTHON")

                        layer_path = os.path.join(merged_file_path, l)
                        arcpy.Append_management(mdb + "\\" + l, layer_path, "NO_TEST", "", "")
                        arcpy.DeleteField_management(l, ["source_file"])
                    except Exception as e:
                        # Log in exception list
                        exception_list.write("Merge Database Error for {} at layer {}\n".format(mdb, l))
                        print("❌ Error processing layer {} from {}: {}".format(l, mdb, e))

                        # Mark MDB as failed
                        failed_list.write("{}\n".format(mdb))
                        mdb_failed = True

                        # Send Telegram alert
                        error_message = "⚠️ Merge Database Error!\n\n" \
                                        "🗂 Path: {}\n" \
                                        "📜 Script: Merge_Database\n" \
                                        "🗂 MDB: {}\n" \
                                        "❌ Error: {}".format(path, mdb, str(e))
                        send_telegram_message(error_message)
                        break  # stop processing more layers of this MDB

                if mdb_failed:
                    print("⚠️ Skipped remaining layers for MDB: {}".format(mdb))

        # Print failed MDBs from CSV
        print("\n===== FAILED MDBs =====")
        with open(failed_mdb_csv, "r") as f:
            print(f.read())

        print("Merge all data Process complete")
        tkMessageBox.showinfo(title="Merge Saex Mdb files", message="Done")

    except Exception as e:
        print("Failed to write to exception file: {}".format(e))
        error_message = "⚠️ Merge Database Error!\n\n" \
                        "🗂 Path: {}\n" \
                        "📜 Script: Merge_Database\n" \
                        "❌ Error: {}".format(path, str(e))
        send_telegram_message(error_message)

    # Success notification
    success_message = "✅ Merge Database Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Merge_Database\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)
