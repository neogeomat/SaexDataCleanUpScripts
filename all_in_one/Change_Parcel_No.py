from Tkinter import *
import tkMessageBox
import arcpy
import os
import shared_data

version = "v2.1.6"

def Change_parcel_no(self, max_parcel_no):
    path = shared_data.directory
    exception_file_path = open(path + "\\exception_list_max_parcel_no.csv", "a")
    mdb_list = shared_data.filtered_mdb_files
    exception_file_path.truncate(0)

    for count, mdb_file in enumerate(mdb_list, start=1):
        parcelfile = os.path.join(mdb_file, "Parcel")
        filename = os.path.basename(mdb_file)
        try:
            update_parcelno(mdb_file,max_parcel_no)
        except Exception as e:
            exception_file_path.write("Compact Error for: " + filename + "\n")


def update_parcelno(mdb, max_parcelno):
    """Update ParcelNo values"""
    try:
        query = "[PARCELNO] >= {}".format(max_parcelno)
        arcpy.MakeFeatureLayer_management("{}\\Parcel".format(mdb), "parcel_layer")

        # Validate field existence
        fields = [f.name for f in arcpy.ListFields("parcel_layer")]
        if "PARCELNO" not in fields:
            raise Exception("Field 'PARCELNO' not found in the Parcel layer.")

        # Apply selection
        arcpy.SelectLayerByAttribute_management("parcel_layer", "NEW_SELECTION", query)

        selected_count = int(arcpy.GetCount_management("parcel_layer").getOutput(0))

        if selected_count > 0:
            arcpy.CalculateField_management("parcel_layer", "PARCELNO", "0", "PYTHON_9.3")
            print "Updated {} parcels with PARCELNO > {}".format(selected_count, max_parcelno)
        else:
            print "No parcels found with PARCELNO > {}".format(max_parcelno)

    except Exception as e:
        print "Error processing {}: {}".format(mdb, str(e))
        raise  # Re-raise the error so it can be caught in fix_gaps_and_overlaps

    finally:
        if arcpy.Exists("parcel_layer"):
            arcpy.Delete_management("parcel_layer")

        # Compact the database after processing
        arcpy.Compact_management(mdb)

