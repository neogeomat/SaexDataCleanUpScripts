# -*- coding: utf-8 -*-
import sys
import tkMessageBox
import arcpy
import shared_data
import os
import time
from send_notif_telegram import send_telegram_message  # <- import your function here

def Generalize(self, tolerance,central_medirian, status_update=None, show_messagebox=True, update_progress=None):

    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(path + "\\exception_list_generalize.csv", "a")
    count = 0
    exception_occurred = False  # Flag to track errors

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
            option_choosed = central_medirian
            blank_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\" + option_choosed

            if os.path.exists(blank_data):
                BLANK_Template = blank_data
            else:
                print("Blank Template database not found, install saex")

            # Process: Copy Features
            arcpy.CopyFeatures_management(i + "\\Parcel", DataCleanTemp + "\\Parcel_to_Simplify", "", "0", "0", "0")

            arcpy.SimplifyPolygon_cartography(i + "\\Parcel", DataCleanTemp + "\\Simplified_2", "POINT_REMOVE", tolerance, "0 SquareMeters", "RESOLVE_ERRORS", "NO_KEEP", "")

            arcpy.Delete_management(i + "\\Parcel")

            # Process: Copy Features
            arcpy.CopyFeatures_management(BLANK_Template + "\\Parcel", i + "\\Parcel", "", "0", "0", "0")

            # Process: Append
            arcpy.Append_management(DataCleanTemp + "\\Simplified_2.shp", i + "\\Parcel", "NO_TEST")

            # Remove processing folder
            arcpy.Delete_management(DataCleanTemp, "Folder")

            arcpy.Compact_management(i)

        except Exception as e:
            exception_occurred = True
            exception_list.write("Generalize Error for: " + i + "\n")
            print("Generalize error for " + i + "\nError=\n\n", sys.exc_info())
            if status_update:
                status_update("Error processing {}: {}".format(filename, str(e)))

            # 🛑 Send Telegram notification for the error
            error_message = "⚠️ Generalize Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Generalize\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, filename, str(e))
            send_telegram_message(error_message)

        if status_update:
            status_update("{} \n({}/{}) processed".format(filename, count, len(mdb_list)))

        if update_progress:
            x = count / float(len(mdb_list))
            progress_value = (x) * 100
            update_progress(progress_value, len(mdb_list))
        self.master.update_idletasks()  # Ensure GUI updates

    print("Generalize process complete")
    exception_list.close()

    if status_update:
        status_update("Generalize process complete. Check exception_list_generalize.csv for errors.")

    duration = time.time() - startTime
    print('The script took {0} seconds!'.format(duration))

    # Final notification based on success or failure
    if exception_occurred:
        final_message = "⚠️ Generalization Process completed with errors.\n\nCheck exception_list_generalize.csv for details."
    else:
        final_message = "✅ Generalization Process completed successfully."

    # Send the success or error message to Telegram
    send_telegram_message(final_message + "\n🗂 Path: {}\n📜 Script: Generalize\n⏱ Duration: {:.2f} seconds".format(path, duration))

    if show_messagebox:
        tkMessageBox.showinfo(title="Generalize database", message="Generalization process is complete.")
