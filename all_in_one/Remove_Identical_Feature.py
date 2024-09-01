import tkMessageBox
import arcpy
import os
import time
import shared_data

def Remove_Identical_Feature(self, status_update=None, show_messagebox=True):
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
            arcpy.DeleteIdentical_management(os.path.join(mdb, "Construction"), ["Shape_Area", "Shape_Length", "ParFID"])
            # arcpy.DeleteIdentical_management(os.path.join(mdb, "Parcel"), ["Shape_Area", "Shape_Length", "PARCELNO"])
            if status_update:
                status_update("Removed identical features from {} \n({}/{})".format(filename, count, total_files))
        except Exception as e:
            exception_list.write("Remove Identical Feature Error for: " + mdb + "\n")
            print("Remove Identical Feature error for " + mdb + "\nError=\n\n", e)
            if status_update:
                status_update("Error removing identical features from {}: {}".format(filename, str(e)))

    exception_list.close()
    print("Remove Identical Feature process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))

    if show_messagebox:
        tkMessageBox.showinfo(title="Remove Identical Feature", message="Removal of identical features is complete.")
