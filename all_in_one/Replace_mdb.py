# -*- coding: utf-8 -*-
import tkMessageBox
import arcpy
import os
import time
import shared_data
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

def replaceMDb(self, central_meridian, status_update=None, show_messagebox=True):
    """Replace MDB files with updated data from specified templates, with status updates and optional message box."""
    arcpy.env.overwriteOutput = True
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(os.path.join(path, "exception_list_whole_mdb_replace.csv"), "a")
    exception_list.truncate(0)
    count = 0

    option_choosed = central_meridian
    local_cm_loc = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"
    blank_default = os.path.join(local_cm_loc, "BLANK.mdb")
    blank_data = os.path.join(local_cm_loc, option_choosed)

    print("Option chosen: " + blank_data)
    arcpy.env.workspace = blank_data

    for count, i in enumerate(mdb_list, start=1):
        try:
            replace_and_append_layers(blank_default, i, count, mdb_list)
            replace_and_append_layers(blank_data, i, count, mdb_list)

            if status_update:
                status_update("Processed {} ({}/{})".format(i, count, len(mdb_list)))

        except Exception as e:
            exception_list.write("Replace Whole Mdb Error for: " + i + "\n")
            print("Error replacing whole MDB for " + i + "\nError: ", e)

            # Send Telegram notification for error
            error_message = "⚠️ Replace MDB Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: replaceMDb\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, i, str(e))
            send_telegram_message(error_message)

    exception_list.close()

    # Send Telegram notification for successful processing
    success_message = "✅ MDB Replace Process Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: replaceMDb\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    print("Replace Whole Mdb process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))

    if show_messagebox:
        tkMessageBox.showinfo(title="Extent ReCalculation database", message="Done")

import arcpy
import os

def replace_and_append_layers(blank_data, i, count, mdb_list):
    try:
        arcpy.env.workspace = blank_data

        out_data = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\test.mdb"
        arcpy.Copy_management(blank_data, out_data)

        print("\nReplacing Whole Mdb in : ")
        print(i + " (" + str(count) + "/" + str(len(mdb_list)) + ")")

        # Define layer names to process
        layer_names = ["Parcel", "Construction", "Parcel_History", "Segments"]

        for layer in layer_names:
            source_layer = os.path.join(i, layer)
            target_layer = os.path.join(out_data, layer)
            if arcpy.Exists(source_layer):
                arcpy.Append_management(source_layer, target_layer, "NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(source_layer)
            else:
                print(layer + " Layer not found for " + i)

        arcpy.env.workspace = i
        point_features_list = arcpy.ListFeatureClasses("*", "Point")

        for pt_feature in point_features_list:
            arcpy.AddField_management(pt_feature, "Symbol_Type", "TEXT")
            layer_name = os.path.basename(pt_feature)
            expression = '"' + layer_name + '"'
            arcpy.CalculateField_management(pt_feature, "Symbol_Type", expression, "PYTHON")
            arcpy.Append_management(pt_feature, os.path.join(out_data, "Other_Symbols"), "NO_TEST")

        arcpy.Copy_management(out_data, i)
        arcpy.Delete_management(out_data)

    except Exception as e:
        print("An error occurred while processing " + i + ": " + str(e))

