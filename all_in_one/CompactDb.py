import tkMessageBox
import arcpy
import time
import shared_data
import os


def compactDb(self, status_update=None, show_messagebox=True, update_progress=None):
    """Compact the database files, update status using the provided function, and optionally show a message box."""
    startTime = time.time()
    path = shared_data.directory
    exception_list = open(os.path.join(path, "exception_list_compact.csv"), "a")
    count = 0
    total = len(shared_data.filtered_mdb_files)

    # Update status to indicate the start of the process
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
            exception_list.write("Compact Error for: " + i + "\n")
            print("Compact error for " + i)
            if status_update:
                status_update("Error compacting {}: {}".format(filename, str(e)))

        if update_progress:
            x= progress/float(total)
            progress_value = (x) * 100
            update_progress(progress_value, total)
        self.master.update_idletasks()  # Ensure GUI updates

    print("Compact process complete")
    exception_list.close()

    # Final status update
    if status_update:
        status_update("Compact process complete. Check exception_list_compact.csv for errors.")

    print('The script took {0} seconds!'.format(time.time() - startTime))

    # Show message box if the flag is set
    if show_messagebox:
        tkMessageBox.showinfo(title="Compact database", message="Compacting process is complete.")
