# -*- coding: utf-8 -*-
import tkMessageBox
import arcpy
import os
import time
import shared_data
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

def Remove_Identical_Feature(self, status_update=None, show_messagebox=True, update_progress=None):
    """Remove identical features from the specified feature classes, with status updates and optional message box."""
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(path + "\\exception_list_identical.csv", "a")
    count = 0
    total_files = len(mdb_list)

    if status_update:
        status_update("Starting removal of identical features...")

    for count, mdb in enumerate(mdb_list, start=1):
        filename = os.path.basename(mdb)
        print ("Removing identical const in {} \n({}/{})".format(filename, count, len(mdb_list)))
        if status_update:
            status_update("Processing {} \n({}/{})".format(filename, count, len(mdb_list)))

        try:
            arcpy.DeleteIdentical_management(os.path.join(mdb, "Construction"), ["Shape"])
            arcpy.DeleteIdentical_management(os.path.join(mdb, "Segments"), [ "Shape"])
            if status_update:
                status_update("Removed identical features from {} \n({}/{})".format(filename, count, total_files))
        except Exception as e:
            exception_list.write("Remove Identical Feature Error for: " + mdb + "\n")
            print("Remove Identical Feature error for " + mdb + "\nError=\n\n", e)
            # Send Telegram notification for error
            error_message = "⚠️ Remove Identical Construction and Segments Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Remove_Identical_Construction_and_Segments\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, mdb, str(e))
            send_telegram_message(error_message)

            if status_update:
                status_update("Error removing identical features from {}: {}".format(filename, str(e)))
        if update_progress:
            x= count/float(len(mdb_list))
            progress_value = (x) * 100
            update_progress(progress_value, len(mdb_list))
        self.master.update_idletasks()  # Ensure GUI updates

    exception_list.close()
    print("Remove Identical Feature process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))
    # Send Telegram notification for successful processing
    success_message = "✅ Remove Identical Construction and Segments Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Remove_Identical_Construction_and_Segments\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    if show_messagebox:
        tkMessageBox.showinfo(title="Remove Identical Feature", message="Removal of identical features is complete.")
