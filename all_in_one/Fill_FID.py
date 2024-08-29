import tkMessageBox
import arcpy
import shared_data
import time
import os
from csv_logging import create_csv_log_file, write_error_to_csv


def Correct_FID(self, status_update=None, show_messagebox=True):
    """Process feature classes, update status using the provided function, and optionally show a message box."""
    startTime = time.time()
    error_log_path = os.path.join(shared_data.directory, "error_log.csv")

    # Create and open the CSV file for error logging
    file_handler, csv_writer = create_csv_log_file(error_log_path)

    for mdb in shared_data.filtered_mdb_files:

        arcpy.env.workspace = mdb
        # Setting input and output
        inFeatures1 = ["Segments", "Parcel"]
        inFeatures2 = ["Construction", "Parcel"]
        intersectOutput1 = "Segments1"
        intersectOutput2 = "Construction1"

        if status_update:
            status_update("Checking for feature classes...")

        try:
            if arcpy.Exists("Segments") and arcpy.Exists("Construction") and arcpy.Exists("Parcel"):
                # Overwrite if feature exists
                arcpy.env.overwriteOutput = True

                if status_update:
                    status_update("Processing intersect analysis...")

                # Intersect Parcel and segment
                arcpy.Intersect_analysis(inFeatures1, intersectOutput1, "", "", "line")
                arcpy.Intersect_analysis(inFeatures2, intersectOutput2, "", "", "")

                if status_update:
                    status_update("Calculating ParFID...")

                # Calculate ParFID
                arcpy.CalculateField_management(intersectOutput1, "ParFID", "!FID_Parcel!", "PYTHON_9.3")
                arcpy.CalculateField_management(intersectOutput2, "ParFID", "!FID_Parcel!", "PYTHON_9.3")

                if status_update:
                    status_update("Deleting unnecessary fields...")

                # Delete unnecessary fields
                dropFields1 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote",
                               "FID_Segments", "FID_Parcel"]
                dropFields2 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote",
                               "FID_Construction", "FID_Parcel"]

                arcpy.DeleteField_management(intersectOutput1, dropFields1)
                arcpy.DeleteField_management(intersectOutput2, dropFields2)

                if status_update:
                    status_update("Deleting and renaming feature classes...")

                # Delete Feature Classes
                arcpy.Delete_management("Segments")
                arcpy.Delete_management("Construction")

                # Rename Feature Classes
                arcpy.Rename_management(intersectOutput1, "Segments")
                arcpy.Rename_management(intersectOutput2, "Construction")

                if status_update:
                    status_update("Processing complete.")

            else:
                if status_update:
                    status_update("Feature classes missing.")

        except Exception as e:
            # Log the error to the CSV file
            write_error_to_csv(csv_writer, os.path.basename(mdb), str(e))
            if status_update:
                status_update("Error during processing: {}".format(str(e)))
            if show_messagebox:
                tkMessageBox.showerror(title="Error", message="An error occurred: {}".format(str(e)))

    file_handler.close()
    print('The script took {0} seconds!'.format(time.time() - startTime))
