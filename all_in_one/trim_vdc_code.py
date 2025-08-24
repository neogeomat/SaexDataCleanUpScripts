# -*- coding: utf-8 -*-
import time
import os
import tkMessageBox
import shared_data
import arcpy
from send_notif_telegram import send_telegram_message  # <- import your function here
from FixGapsAndOverlaps_saex_mdbs import calculate_suspicious_and_circularity

def trim_vdc_code(self, status_update=None, show_messagebox=True, update_progress=None):

    startTime = time.time()
    path = shared_data.directory
    exception_path = os.path.join(path, "exception_list_trim.csv")
    exception_list = open(exception_path, "a")
    count = 0
    total = len(shared_data.filtered_mdb_files)
    exception_occurred = False  # Flag to track errors
    layers = ["Parcel"]

    if status_update:
        status_update("Starting triming process...")

    for progress, i in enumerate(shared_data.filtered_mdb_files, start=1):
        count += 1
        filename = os.path.basename(i)
        print (i + " (" + str(count) + "/" + str(total) + ")")

        # calculate_suspicious_and_circularity(i+"//Parcel")
        # continue

        try:
            if status_update:
                status_update("Triming {} \n({}/{})".format(filename, count, total))
            for l in layers:
                TheShapefile = os.path.join(i, l)
                if arcpy.Exists(TheShapefile):
                    with arcpy.da.UpdateCursor(TheShapefile, ["VDC"]) as cursor:
                        for row in cursor:
                            if row[0] and isinstance(row[0], (int, long, float)):  # numeric VDC code (int or float)
                                # Convert to integer first so 695037.0 becomes 695037
                                vdc_int = int(row[0])
                                if vdc_int > 99:
                                    row[0] = vdc_int % 100  # keep last 2 digits
                                    cursor.updateRow(row)
                            elif row[0] and isinstance(row[0], basestring):  # string VDC code
                                if row[0].isdigit() and int(row[0]) > 99:
                                    row[0] = row[0][-2:]
                                    cursor.updateRow(row)

        except Exception as e:
            exception_occurred = True
            exception_list.write("triming Error for: " + i + "\n")
            print("triming error for " + i)
            if status_update:
                status_update("Error triming {}: {}".format(filename, str(e)))

            # 🛑 Send Telegram notification for the error
            error_message = "⚠️ Trim Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Trim_VDC_code\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, filename, str(e))
            send_telegram_message(error_message)

        if update_progress:
            x = progress / float(total)
            progress_value = (x) * 100
            update_progress(progress_value, total)
        self.master.update_idletasks()

    print("Trim process complete")
    exception_list.close()

    if status_update:
        status_update("Trim process complete. Check exception_list_Trim.csv for errors.")

    duration = time.time() - startTime
    print('The script took {0} seconds!'.format(duration))

    # Final notification based on success or failure
    if exception_occurred:
        final_message = "⚠️ Triming Process completed with errors.\n\nCheck exception_list_Trim.csv for details."
    else:
        final_message = "✅ Triming Process completed successfully."

    # Send the success or error message to Telegram
    send_telegram_message(final_message + "\n🗂 Path: {}\n📜 Script: TrimDb\n⏱ Duration: {:.2f} seconds".format(path, duration))

    if show_messagebox:
        tkMessageBox.showinfo(title="Trim database", message="Triming process is complete.")
