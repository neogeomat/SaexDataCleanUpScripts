import csv
import arcpy
import shared_data
import tkinter as tk
from tkinter import scrolledtext


def Find_Identical_Feature(self):
    results = {}
    fields = ['DISTRICT', 'VDC', 'WARDNO', 'GRIDS1', 'PARCELNO', 'OBJECTID']

    mdb_files = shared_data.filtered_mdb_files

    for mdb in mdb_files:
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

    return results


def display_results(results):
    output_file_path = shared_data.directory + "\\identical_parcels_list.csv"

    # Open file in binary write mode for Python 2.7
    with open(output_file_path, 'wb') as output_file:
        save_results_to_csv(results, output_file)

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
                    key, ", ".join(map(str, oids))))
                result_text.insert(tk.END, "\n")
    else:
        result_text.insert(tk.END, "No identical parcels found.")

    result_text.config(state=tk.DISABLED)


def save_results_to_csv(results, output_file):
    writer = csv.writer(output_file)
    writer.writerow(['MDB File', 'ParcelNo', 'Ward', 'VDC', 'GridSheet', 'Duplicate ObjectIDs'])

    for mdb, duplicates in results.items():
        if isinstance(duplicates, str):  # If the result is a string, it means no parcel layer was found
            writer.writerow([mdb, duplicates])
        else:
            for key, oids in duplicates.iteritems():
                # Join ObjectID values with a space instead of a comma
                writer.writerow([mdb] + list(key) + [" ".join(map(str, oids))])
