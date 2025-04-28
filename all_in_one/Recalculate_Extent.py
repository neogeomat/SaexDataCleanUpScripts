# -*- coding: utf-8 -*-
import tkMessageBox
import arcpy
import os
import time
import shared_data
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

def recalculate_extent(self, status_update=None, show_messagebox=True, update_progress=None):
    """Recalculate the extent of feature classes in the provided .mdb files, with status updates and optional message box."""
    arcpy.env.overwriteOutput = True
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(path + "\\exception_list_recalculate_extent.csv", "a")
    count = 0
    total_files = len(mdb_list)

    if status_update:
        status_update("Starting extent recalculation process...")

    for count, mdb in enumerate(mdb_list, start=1):
        filename = os.path.basename(mdb)
        print ("Recalculating extent in {} \n({}/{})".format(filename, count, len(mdb_list)))

        if status_update:
            status_update("Processing {} \n({}/{})".format(filename, count, len(mdb_list)))

        feature_classes = []
        walk = arcpy.da.Walk(mdb, datatype="FeatureClass")
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                feature_classes.append(os.path.join(dirpath, filename))

        try:
            for feature in feature_classes:
                arcpy.RecalculateFeatureClassExtent_management(feature)
            if status_update:
                status_update("Recalculated extent for {} \n({}/{})".format(filename, count, total_files))
        except Exception as e:
            exception_list.write("Extent ReCalculation Error for: " + mdb + "\n")
            print("Extent ReCalculation error for " + mdb + "\nError=\n\n", e)
            # Send Telegram notification for error
            error_message = "⚠️ Recalculate Extent Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Recalculate_Extent\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, mdb, str(e))
            send_telegram_message(error_message)

            if status_update:
                status_update("Error recalculating extent for {}: {}".format(filename, str(e)))
        if update_progress:
            x= count/float(len(mdb_list))
            progress_value = (x) * 100
            update_progress(progress_value, len(mdb_list))
        self.master.update_idletasks()  # Ensure GUI updates

    exception_list.close()
    print("Extent ReCalculation process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))
    # Send Telegram notification for successful processing
    success_message = "✅ Recalculate Extent Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Recalculate_Extent\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    if show_messagebox:
        tkMessageBox.showinfo(title="Extent ReCalculation", message="Extent recalculation process is complete.")
