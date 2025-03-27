import tkMessageBox
import arcpy
import shared_data
import time
import os
from csv_logging import create_csv_log_file, write_error_to_csv

def Correct_FID(self, status_update=None, show_messagebox=True, update_progress=None):
    """Process feature classes, update status using the provided function, and optionally show a message box."""
    startTime = time.time()
    error_log_path = os.path.join(shared_data.directory, "error_log.csv")
    count = 0
    total = len(shared_data.filtered_mdb_files)

    # Create and open the CSV file for error logging
    file_handler, csv_writer = create_csv_log_file(error_log_path)
    arcpy.env.overwriteOutput = True

    # Dictionary to hold time taken for each step
    step_times = {
        "Check Feature Classes": 0,
        "Intersect Analysis": 0,
        "Calculate ParFID": 0,
        "Delete Fields": 0,
        "Delete Feature Classes": 0,
        "Rename Feature Classes": 0,
        "Total Iteration Time": 0
    }

    if status_update:
        status_update("Starting Correcting Parcel ID Process...")

    for mdb in shared_data.filtered_mdb_files:
        count += 1
        filename = os.path.basename(mdb)
        print ("Correcting PID in {} \n({}/{})".format(filename, count, total))
        if status_update:  # Update status every 10 iterations
            status_update("Correcting PID in {} \n({}/{})".format(filename, count, total))

        arcpy.env.workspace = mdb
        step_start_time = time.time()  # Record start time for this iteration

        try:
            # Check if feature classes exist
            check_start_time = time.time()
            if all(arcpy.Exists(fc) for fc in ["Segments", "Construction", "Parcel"]):
                check_end_time = time.time()
                step_times["Check Feature Classes"] += (check_end_time - check_start_time)

                # Intersect Parcel and segment
                intersect_start_time = time.time()
                arcpy.Intersect_analysis(["Segments", "Parcel"], "Segments1", "", "", "line")
                arcpy.Intersect_analysis(["Construction", "Parcel"], "Construction1", "", "", "")
                intersect_end_time = time.time()
                step_times["Intersect Analysis"] += (intersect_end_time - intersect_start_time)

                # Calculate ParFID
                calculate_start_time = time.time()
                arcpy.CalculateField_management("Segments1", "ParFID", "!FID_Parcel!", "PYTHON_9.3")
                arcpy.CalculateField_management("Construction1", "ParFID", "!FID_Parcel!", "PYTHON_9.3")
                calculate_end_time = time.time()
                step_times["Calculate ParFID"] += (calculate_end_time - calculate_start_time)

                # Delete unnecessary fields
                delete_fields_start_time = time.time()
                dropFields1 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote", "FID_Segments", "FID_Parcel"]
                dropFields2 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote", "FID_Construction", "FID_Parcel"]

                arcpy.DeleteField_management("Segments1", dropFields1)
                arcpy.DeleteField_management("Construction1", dropFields2)
                delete_fields_end_time = time.time()
                step_times["Delete Fields"] += (delete_fields_end_time - delete_fields_start_time)

                # Delete Feature Classes
                delete_fc_start_time = time.time()
                arcpy.Delete_management("Segments")
                arcpy.Delete_management("Construction")
                delete_fc_end_time = time.time()
                step_times["Delete Feature Classes"] += (delete_fc_end_time - delete_fc_start_time)

                # Rename Feature Classes
                rename_start_time = time.time()
                arcpy.Rename_management("Segments1", "Segments")
                arcpy.Rename_management("Construction1", "Construction")
                rename_end_time = time.time()
                step_times["Rename Feature Classes"] += (rename_end_time - rename_start_time)

                if status_update:
                    status_update("Processing complete{} \n({}/{})".format(mdb, count, total))

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

        iteration_end_time = time.time()
        step_times["Total Iteration Time"] += (iteration_end_time - step_start_time)

        if update_progress:
            x= count/float(total)
            progress_value = (x) * 100
            update_progress(progress_value, total)
        self.master.update_idletasks()  # Ensure GUI updates

    file_handler.close()

    # Print total times for each step
    print "Time taken for each step:"
    for step, duration in step_times.items():
        print "{}: {:.2f} seconds".format(step, duration)

    print 'The script took {0} seconds!'.format(time.time() - startTime)
    print("Fill Parcel FID complete")
