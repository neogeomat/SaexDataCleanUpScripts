# -*- coding: utf-8 -*-
import tkMessageBox
import arcpy
import os
import time
import shared_data
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

def Repair_Geometry(self, status_update=None, show_messagebox=True, update_progress=None):
    """Repair geometry of the specified feature classes, with status updates and optional message box."""
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(path + "\\exception_list_repair.csv", "a")
    count = 0
    total_files = len(mdb_list)

    if status_update:
        status_update("Starting geometry repair...")

    for count, mdb in enumerate(mdb_list, start=1):
        filename = os.path.basename(mdb)
        print ("Repair Geometry in {} \n({}/{})".format(filename, count, len(mdb_list)))
        if status_update:
            status_update("Processing {} \n({}/{})".format(filename, count, len(mdb_list)))

        try:
            arcpy.RepairGeometry_management(os.path.join(mdb, "Parcel"))
            arcpy.RepairGeometry_management(os.path.join(mdb, "Construction"))
            if status_update:
                status_update("Repaired geometry for {} ({}/{})".format(filename, count, total_files))
        except Exception as e:
            exception_list.write("Repair Geometry Error for: " + mdb + "\n")
            print("Repair Geometry error for " + mdb + "\nError=\n\n", e)
            # Send Telegram notification for error
            error_message = "⚠️ Repair Geometry Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Repair_Geometry\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, mdb, str(e))
            send_telegram_message(error_message)

            if status_update:
                status_update("Error repairing geometry for {}: {}".format(filename, str(e)))
        if update_progress:
            x= count/float(total_files)
            progress_value = (x) * 100
            update_progress(progress_value, total_files)
        self.master.update_idletasks()  # Ensure GUI updates

    exception_list.close()
    print("Repair Geometry process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))
    # Send Telegram notification for successful processing
    success_message = "✅ Repair Geometry Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Repair_Geometry\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    if show_messagebox:
        tkMessageBox.showinfo(title="Repair Geometry", message="Geometry repair process is complete.")
