# -*- coding: utf-8 -*-
import time
import os
import tkMessageBox
import shared_data
import arcpy
from send_notif_telegram import send_telegram_message  # <- import your function here
def compactDb(self, status_update=None, show_messagebox=True, update_progress=None):

    startTime = time.time()
    path = shared_data.directory
    exception_path = os.path.join(path, "exception_list_compact.csv")
    exception_list = open(exception_path, "a")
    count = 0
    total = len(shared_data.filtered_mdb_files)
    exception_occurred = False  # Flag to track errors

    if status_update:
        status_update("Starting compacting process...")

    for progress, i in enumerate(shared_data.filtered_mdb_files, start=1):
        count += 1
        filename = os.path.basename(i)
        print (i + " (" + str(count) + "/" + str(total) + ")")

        try:
            arcpy.Compact_management(i)
            if status_update:
                status_update("Compacting {} \n({}/{})".format(filename, count, total))

        except Exception as e:
            exception_occurred = True
            exception_list.write("Compact Error for: " + i + "\n")
            print("Compact error for " + i)
            if status_update:
                status_update("Error compacting {}: {}".format(filename, str(e)))

            # 🛑 Send Telegram notification for the error
            error_message = "⚠️ Compact Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: compactDb\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, filename, str(e))
            send_telegram_message(error_message)

        if update_progress:
            x = progress / float(total)
            progress_value = (x) * 100
            update_progress(progress_value, total)
        self.master.update_idletasks()

    print("Compact process complete")
    exception_list.close()

    if status_update:
        status_update("Compact process complete. Check exception_list_compact.csv for errors.")

    duration = time.time() - startTime
    print('The script took {0} seconds!'.format(duration))

    # Final notification based on success or failure
    if exception_occurred:
        final_message = "⚠️ Compacting Process completed with errors.\n\nCheck exception_list_compact.csv for details."
    else:
        final_message = "✅ Compacting Process completed successfully."

    # Send the success or error message to Telegram
    send_telegram_message(final_message + "\n🗂 Path: {}\n📜 Script: compactDb\n⏱ Duration: {:.2f} seconds".format(path, duration))

    if show_messagebox:
        tkMessageBox.showinfo(title="Compact database", message="Compacting process is complete.")
