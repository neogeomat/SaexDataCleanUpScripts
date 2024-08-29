import tkMessageBox
import arcpy
import os
import time
import shared_data

def recalculate_extent(self, status_update=None, show_messagebox=True):
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
        feature_classes = []
        walk = arcpy.da.Walk(mdb, datatype="FeatureClass")
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                feature_classes.append(os.path.join(dirpath, filename))

        try:
            for feature in feature_classes:
                arcpy.RecalculateFeatureClassExtent_management(feature)
            if status_update:
                status_update("Recalculated extent for {} ({}/{})".format(mdb, count, total_files))
        except Exception as e:
            exception_list.write("Extent ReCalculation Error for: " + mdb + "\n")
            print("Extent ReCalculation error for " + mdb + "\nError=\n\n", e)
            if status_update:
                status_update("Error recalculating extent for {}: {}".format(mdb, str(e)))

    exception_list.close()
    print("Extent ReCalculation process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))

    if show_messagebox:
        tkMessageBox.showinfo(title="Extent ReCalculation", message="Extent recalculation process is complete.")
