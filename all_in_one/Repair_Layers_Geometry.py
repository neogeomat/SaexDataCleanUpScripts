import tkMessageBox
import arcpy
import os
import time
import shared_data

def Repair_Geometry(self, status_update=None, show_messagebox=True):
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
        try:
            arcpy.RepairGeometry_management(os.path.join(mdb, "Parcel"))
            arcpy.RepairGeometry_management(os.path.join(mdb, "Construction"))
            if status_update:
                status_update("Repaired geometry for {} ({}/{})".format(mdb, count, total_files))
        except Exception as e:
            exception_list.write("Repair Geometry Error for: " + mdb + "\n")
            print("Repair Geometry error for " + mdb + "\nError=\n\n", e)
            if status_update:
                status_update("Error repairing geometry for {}: {}".format(mdb, str(e)))

    exception_list.close()
    print("Repair Geometry process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))

    if show_messagebox:
        tkMessageBox.showinfo(title="Repair Geometry", message="Geometry repair process is complete.")
