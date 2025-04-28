# -*- coding: utf-8 -*-
import tkMessageBox
import arcpy
import shared_data
import time
import os
from csv_logging import create_csv_log_file, write_error_to_csv
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

def Correct_FID(self, status_update=None, show_messagebox=True, update_progress=None):
    """Process feature classes, update status using the provided function, and optionally show a message box."""
    startTime = time.time()
    error_log_path = os.path.join(shared_data.directory, "error_log.csv")
    count = 0
    total = len(shared_data.filtered_mdb_files)
    path = shared_data.directory

    # Create and open the CSV file for error logging
    file_handler, csv_writer = create_csv_log_file(error_log_path)
    arcpy.env.overwriteOutput = True

    # Dictionary to hold time taken for each step


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

                # Intersect Parcel and segment
                intersect_start_time = time.time()
                arcpy.Intersect_analysis(["Segments", "Parcel"], "Segments1", "", "", "line")
                arcpy.Intersect_analysis(["Construction", "Parcel"], "Construction1", "", "", "")
                intersect_end_time = time.time()

                # Calculate ParFID
                calculate_start_time = time.time()
                arcpy.CalculateField_management("Segments1", "ParFID", "!FID_Parcel!", "PYTHON_9.3")
                arcpy.CalculateField_management("Construction1", "ParFID", "!FID_Parcel!", "PYTHON_9.3")
                calculate_end_time = time.time()

                # Delete unnecessary fields
                delete_fields_start_time = time.time()
                dropFields1 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote", "FID_Segments", "FID_Parcel"]
                dropFields2 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote", "FID_Construction", "FID_Parcel"]

                arcpy.DeleteField_management("Segments1", dropFields1)
                arcpy.DeleteField_management("Construction1", dropFields2)
                delete_fields_end_time = time.time()

                # Delete Feature Classes
                delete_fc_start_time = time.time()
                arcpy.Delete_management("Segments")
                arcpy.Delete_management("Construction")
                delete_fc_end_time = time.time()

                # Rename Feature Classes
                rename_start_time = time.time()
                arcpy.Rename_management("Segments1", "Segments")
                arcpy.Rename_management("Construction1", "Construction")
                rename_end_time = time.time()

                if status_update:
                    status_update("Processing complete{} \n({}/{})".format(mdb, count, total))

            else:
                if status_update:
                    status_update("Feature classes missing.")

        except Exception as e:
            # Log the error to the CSV file
            write_error_to_csv(csv_writer, os.path.basename(mdb), str(e))
            # Send Telegram notification for error
            error_message = "⚠️ Correct ParcelID Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Correct_ParcelID\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, mdb, str(e))
            send_telegram_message(error_message)

            if status_update:
                status_update("Error during processing: {}".format(str(e)))
            if show_messagebox:
                tkMessageBox.showerror(title="Error", message="An error occurred: {}".format(str(e)))

        iteration_end_time = time.time()

        if update_progress:
            x= count/float(total)
            progress_value = (x) * 100
            update_progress(progress_value, total)
        self.master.update_idletasks()  # Ensure GUI updates

    file_handler.close()

    # Send Telegram notification for successful processing
    success_message = "✅ Correct Parcel ID Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Correct_ParcelID\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    print 'The script took {0} seconds!'.format(time.time() - startTime)
    print("Fill Parcel FID complete")

# def Correct_FID(self, status_update=None, show_messagebox=True, update_progress=None):
#     startTime = time.time()
#     error_log_path = os.path.join(shared_data.directory, "error_log.csv")
#     count = 0
#     total = len(shared_data.filtered_mdb_files)
#
#     file_handler, csv_writer = create_csv_log_file(error_log_path)
#     arcpy.env.overwriteOutput = True
#
#     # Define temporary folder
#     temp_folder = r"D:\DataCleanTemp"
#
#     # Ensure the folder exists
#     if not os.path.exists(temp_folder):
#         os.makedirs(temp_folder)
#
#     if status_update:
#         status_update("Starting Correcting Parcel ID Process...")
#
#     for mdb in shared_data.filtered_mdb_files:
#         count += 1
#         filename = os.path.basename(mdb)
#         print("Correcting PID in {} \n({}/{})".format(filename, count, total))
#         if status_update:
#             status_update("Correcting PID in {} \n({}/{})".format(filename, count, total))
#
#         arcpy.env.workspace = mdb
#
#         try:
#             # Define input feature classes
#             parcel_layer = mdb + "\\Parcel"
#             construction_layer = mdb + "\\Construction"
#             segment_layer = mdb + "\\Segments"
#
#             # Define file paths for spatial join outputs
#             spatial_join_output = os.path.join(temp_folder, "Construction_Join.shp")
#             spatial_join_segment = os.path.join(temp_folder, "Segment_Join_Segment.shp")
#
#             # Remove previous spatial join results if they exist
#             for temp_file in [spatial_join_output, spatial_join_segment]:
#                 if arcpy.Exists(temp_file):
#                     arcpy.Delete_management(temp_file)
#
#             parcel_id_field = "ParcelID"
#
#             # Ensure ParcelID field is fresh (remove if exists)
#             existing_fields = [f.name for f in arcpy.ListFields(parcel_layer)]
#             if parcel_id_field in existing_fields:
#                 arcpy.DeleteField_management(parcel_layer, parcel_id_field)
#
#             arcpy.AddField_management(parcel_layer, parcel_id_field, "LONG")
#             print("Added new field:", parcel_id_field)
#
#             # Copy Parcel OBJECTID to ParcelID field
#             with arcpy.da.UpdateCursor(parcel_layer, ["OBJECTID", parcel_id_field]) as cursor:
#                 for row in cursor:
#                     row[1] = row[0]
#                     cursor.updateRow(row)
#             print("Parcel OBJECTID copied to", parcel_id_field)
#
#             # Spatial Join for Construction Layer
#             arcpy.SpatialJoin_analysis(target_features=construction_layer,
#                                        join_features=parcel_layer,
#                                        out_feature_class=spatial_join_output,
#                                        join_operation="JOIN_ONE_TO_ONE",
#                                        match_option="INTERSECT")
#
#             # Build dictionary for Construction Layer
#             join_dict = {}
#             with arcpy.da.SearchCursor(spatial_join_output, ["TARGET_FID", parcel_id_field]) as search_cursor:
#                 for row in search_cursor:
#                     join_dict[row[0]] = row[1]
#
#             # Update Construction Layer
#             with arcpy.da.UpdateCursor(construction_layer, ["OBJECTID", "ParFID"]) as update_cursor:
#                 for row in update_cursor:
#                     if row[0] in join_dict:
#                         row[1] = join_dict[row[0]]
#                         update_cursor.updateRow(row)
#             print("ParFID field updated successfully.")
#
#             # Clean up after first join
#             if arcpy.Exists(spatial_join_output):
#                 arcpy.Delete_management(spatial_join_output)
#
#             # Spatial Join for Segments (Handles "WITHIN" + "INTERSECT")
#             arcpy.SpatialJoin_analysis(target_features=segment_layer,
#                                        join_features=parcel_layer,
#                                        out_feature_class=spatial_join_segment,
#                                        join_operation="JOIN_ONE_TO_ONE",
#                                        match_option="INTERSECT")  # INTERSECT handles both within & touches
#
#             # Build dictionary for Segments
#             join_dict_segment = {}
#             with arcpy.da.SearchCursor(spatial_join_segment, ["TARGET_FID", parcel_id_field]) as search_cursor:
#                 for row in search_cursor:
#                     join_dict_segment[row[0]] = row[1]
#
#             # Update Segments Layer
#             with arcpy.da.UpdateCursor(segment_layer, ["OBJECTID", "ParFID"]) as update_cursor:
#                 for row in update_cursor:
#                     if row[0] in join_dict_segment:
#                         row[1] = join_dict_segment[row[0]]
#                         update_cursor.updateRow(row)
#             print("SegFID field updated successfully.")
#
#             # Cleanup: Delete temporary ParcelID field
#             arcpy.DeleteField_management(parcel_layer, parcel_id_field)
#             print("Deleted temporary field:", parcel_id_field)
#
#         except Exception as e:
#             write_error_to_csv(csv_writer, os.path.basename(mdb), str(e))
#             if status_update:
#                 status_update("Error during processing: {}".format(str(e)))
#             if show_messagebox:
#                 tkMessageBox.showerror(title="Error", message="An error occurred: {}".format(str(e)))
#
#         if update_progress:
#             progress_value = (count / float(total)) * 100
#             update_progress(progress_value, total)
#         self.master.update_idletasks()
#
#     file_handler.close()
#     print('The script took {} seconds!'.format(time.time() - startTime))
#     print("Fill Parcel FID complete")
#
#
