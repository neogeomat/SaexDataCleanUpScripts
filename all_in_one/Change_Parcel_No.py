# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import arcpy
import os
import shared_data
import time
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

version = "v2.1.6"

def Change_parcel_no(self, max_parcel_no):
    startTime = time.time()
    path = shared_data.directory
    exception_file_path = open(path + "\\exception_list_max_parcel_no.csv", "a")
    mdb_list = shared_data.filtered_mdb_files
    exception_file_path.truncate(0)

    for count, mdb_file in enumerate(mdb_list, start=1):
        parcelfile = os.path.join(mdb_file, "Parcel")
        filename = os.path.basename(mdb_file)
        try:
            update_parcelno(mdb_file,max_parcel_no)
        except Exception as e:
            exception_file_path.write("Compact Error for: " + filename + "\n")


def update_parcelno(mdb, max_parcelno):
    """Update ParcelNo values"""
    try:
        query = "[PARCELNO] >= {}".format(max_parcelno)
        arcpy.MakeFeatureLayer_management("{}\\Parcel".format(mdb), "parcel_layer")

        # Validate field existence
        fields = [f.name for f in arcpy.ListFields("parcel_layer")]
        if "PARCELNO" not in fields:
            raise Exception("Field 'PARCELNO' not found in the Parcel layer.")

        # Apply selection
        arcpy.SelectLayerByAttribute_management("parcel_layer", "NEW_SELECTION", query)

        selected_count = int(arcpy.GetCount_management("parcel_layer").getOutput(0))

        if selected_count > 0:
            arcpy.CalculateField_management("parcel_layer", "PARCELNO", "0", "PYTHON_9.3")
            print "Updated {} parcels with PARCELNO > {}".format(selected_count, max_parcelno)
        else:
            print "No parcels found with PARCELNO > {}".format(max_parcelno)

    except Exception as e:
        print "Error processing {}: {}".format(mdb, str(e))
        raise  # Re-raise the error so it can be caught in fix_gaps_and_overlaps
        # Send Telegram notification for error
        error_message = "⚠️ Change Parcel No to 0 Error!\n\n" \
                        "🗂 Path: {}\n" \
                        "📜 Script: Change_Parcel_No_to_0\n" \
                        "🗂 File: {}\n" \
                        "❌ Error: {}".format(path, mdb_file, str(e))
        send_telegram_message(error_message)

    finally:
        if arcpy.Exists("parcel_layer"):
            arcpy.Delete_management("parcel_layer")

        # Compact the database after processing
        arcpy.Compact_management(mdb)
    # Send Telegram notification for successful processing
    success_message = "✅ Change Parcel No to 0 Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Change_Parcel_No_to_0\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

