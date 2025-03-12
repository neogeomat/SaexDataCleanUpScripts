from Tkinter import *
import tkMessageBox
import arcpy
import os
import time
from arcpy import env
import shared_data


def attributeChecker(self,check_state, status_update=None, show_messagebox=True, update_progress=None):
    """Check attributes in the database files and optionally show a message box upon completion."""
    starttime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(path + "\\exception_list_check_attr.csv", "a")
    exception_list.truncate(0)

    layers = ["Parcel"]
    allerror = open(path + "\\ALL_ERROR.csv", "a")
    allerror.truncate(0)
    count = 0

    if status_update:
        status_update("Starting attribute checking process...")
    total = len(mdb_list)

    for progress, i in enumerate(shared_data.filtered_mdb_files, start=1):
        filename = os.path.basename(i)
        if status_update:
                status_update("Checking Attribute for {} \n({}/{})".format(filename, count, total))
        try:
            env.workspace = i
            f = open(i + "_error.csv", "a")
            f.truncate(0)
            count += 1
            print(env.workspace + " (" + str(count) + "/" + str(total) + ")")

            for l in layers:
                TheShapefile = os.path.join(i, l)
                if arcpy.Exists(TheShapefile):
                    TheRows = arcpy.SearchCursor(TheShapefile)

                    # Check if Columns exist and handle accordingly
                    column_checks = {
                        "DISTRICT": "District Column does not exist",
                        "VDC": "VDC Column does not exist",
                        "WARDNO": "Ward No Column does not exist",
                        "GRIDS1": "Grid Sheet Column does not exist",
                        "PARCELTY": "Parcel Type Column does not exist",
                        "PARCELNO": "Parcel No Column does not exist",
                        "suspicious": "Suspicious Column does not exist"
                    }

                    skips = {}
                    for column, error_message in column_checks.items():
                        if len(arcpy.ListFields(TheShapefile, column)) != 1:
                            f.write(error_message + "\n")
                            allerror.write(error_message + ",," + i + "\n")
                            skips[column] = True
                        else:
                            skips[column] = False

                    # Loop through each row in the attributes
                    for TheRow in TheRows:
                        # Perform attribute checks and write errors
                        checks = {
                            "DISTRICT": lambda val: (val is None or val in ["", " ", 0] or val > 75),
                            "VDC": lambda val: (val is None or val in ["", " ", 0] or val > 9999),
                            "WARDNO": lambda val: (
                                        val is None or val in ["", " ", 0] or not val.isdigit() or int(val) > 35),
                            "GRIDS1": lambda val: (val is None or len(val) < 7 or len(val) > 9),
                            "PARCELNO": lambda val: (val is None) if check_state else (val is None or val == 0),
                            "PARCELTY": lambda val: (val is None),
                            "suspicious": lambda val: (str(val).lower() == "yes")
                        }

                        for column, check in checks.items():
                            if not skips.get(column, False):
                                value = TheRow.getValue(column)
                                if check(value):
                                    f.write("{} Error at OBJECTID={}\n".format(column, TheRow.getValue("OBJECTID")))
                                    allerror.write(
                                        "{} Error at OBJECTID={},{}\n".format(column, TheRow.getValue("OBJECTID"), i))
                else:
                    f.write("Parcel Layer not found for\n" + i)
                    allerror.write("Parcel Layer not found for\n" + i)
        except Exception as e:
            exception_list.write("Attribute Check Error for," + i + "\n")
            print("Attribute Check Error for " + i + ": " + str(e))

        if update_progress:
            x= progress/float(total)
            progress_value = (x) * 100
            update_progress(progress_value, total)
        self.master.update_idletasks()  # Ensure GUI updates

    print("Process complete")
    endtime = time.time()
    print("Time taken: " + str(endtime - starttime))
    if status_update:
        status_update("Checking Attribute Completed.")

    exception_list.close()
    allerror.close()

    if show_messagebox:
        tkMessageBox.showinfo(title="Check Attribute Errors", message="Attribute checking process is complete.")
