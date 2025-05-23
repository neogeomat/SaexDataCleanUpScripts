# -*- coding: utf-8 -*-
import csv
import tkMessageBox
import arcpy
import shared_data
import tkinter as tk
from tkinter import scrolledtext
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications
import time

def Find_Identical_Feature(self, status_update=None, show_messagebox=True):
    """Find and report identical features in the provided .mdb files, with status updates and optional message box."""
    startTime = time.time()
    path = shared_data.directory
    results = {}
    fields = ['DISTRICT', 'VDC', 'WARDNO', 'GRIDS1', 'PARCELNO', 'OBJECTID']

    mdb_files = shared_data.filtered_mdb_files
    total_files = len(mdb_files)

    if status_update:
        status_update("Starting to find identical features...")

    for count, mdb in enumerate(mdb_files, start=1):
        try:
            if status_update:
                status_update("Processing file {0} ({1}/{2})".format(mdb, count, total_files))

            arcpy.env.workspace = mdb
            parcel_layer = None  # Initialize to None
            feature_classes = arcpy.ListFeatureClasses()

            if not feature_classes:
                results[mdb] = "No feature classes found in this .mdb file."
                continue

            print "Feature classes in %s: %s" % (mdb, feature_classes)  # Debugging output

            for feature_class in feature_classes:
                if feature_class.lower() == "parcel":
                    parcel_layer = feature_class
                    break

            if not parcel_layer:
                results[mdb] = "Parcel layer not found."
                continue

            parcel_dict = {}
            with arcpy.da.SearchCursor(parcel_layer, fields) as cursor:
                for row in cursor:
                    key = tuple(row[:-1])  # Exclude the OID field from the key
                    oid = row[-1]  # OID is the last item in the row
                    if key in parcel_dict:
                        parcel_dict[key].append(oid)  # Store the OID as the position
                    else:
                        parcel_dict[key] = [oid]

            identical_parcels = {k: v for k, v in parcel_dict.iteritems() if len(v) > 1}

            if identical_parcels:
                results[mdb] = identical_parcels
            else:
                results[mdb] = "No identical parcels found."

        except Exception as e:
            results[mdb] = "Error processing file: {}".format(str(e))
            if status_update:
                status_update("Error processing {}: {}".format(mdb, str(e)))
            # Send Telegram notification for error
            error_message = "⚠️ Remove Identical Parcels Error!\n\n" \
                            "🗂 Path: {}\n" \
                            "📜 Script: Remove_Identical_Parcels\n" \
                            "🗂 File: {}\n" \
                            "❌ Error: {}".format(path, mdb, str(e))
            send_telegram_message(error_message)

    if status_update:
        status_update("Finding identical features complete. Check the results.")

    # Save the results to CSV
    output_file_path = shared_data.directory + "\\identical_parcels_list.csv"
    with open(output_file_path, 'wb') as output_file:
        save_results_to_csv(results, output_file)

    # Display results in a Tkinter window
    result_window = tk.Toplevel()
    result_window.title("Identical Parcels Report")
    result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=100, height=30)
    result_text.pack(fill=tk.BOTH, expand=True)

    if results:
        for mdb, duplicates in results.items():
            result_text.insert(tk.END, "File: %s\n" % mdb)
            if isinstance(duplicates, str):  # If the result is a string, it means no parcel layer was found
                result_text.insert(tk.END, "%s\n\n" % duplicates)
            else:
                # Insert field names as the title
                result_text.insert(tk.END, "Fields: District, Ward, VDC, GridSheet, ParcelNo\n")
                total_identical = len(duplicates)
                result_text.insert(tk.END, "Total Identical Parcels Found: %d\n\n" % total_identical)

                for key, oids in duplicates.iteritems():
                    result_text.insert(tk.END, "Parcel %s has duplicates at ObjectID(s): %s\n" % (
                        key, " ".join(map(str, oids))))
                result_text.insert(tk.END, "\n")
    else:
        result_text.insert(tk.END, "No identical parcels found.")

    result_text.config(state=tk.DISABLED)
    print("Identical Parcels Removal Process complete")
    # Send Telegram notification for successful processing
    success_message = "✅ Remove Identical Parcels Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Remove_Identical_Parcels\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    if show_messagebox:
        tkMessageBox.showinfo(title="Identical Parcels Report", message="Process is complete. Check the results.")

def save_results_to_csv(results, output_file):
    """Save the results to a CSV file."""
    writer = csv.writer(output_file)
    writer.writerow(['MDB File', 'ParcelNo', 'Ward', 'VDC', 'GridSheet', 'Duplicate ObjectIDs'])

    for mdb, duplicates in results.items():
        if isinstance(duplicates, str):  # If the result is a string, it means no parcel layer was found
            writer.writerow([mdb, duplicates])
        else:
            for key, oids in duplicates.iteritems():
                # Join ObjectID values with a space instead of a comma
                writer.writerow([mdb] + list(key) + [" ".join(map(str, oids))])
