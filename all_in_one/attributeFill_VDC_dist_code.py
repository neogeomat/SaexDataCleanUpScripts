import tkMessageBox
import arcpy
import os
import shared_data
import time

def Fill_VDC_Dist_Code(self, district_code='',vdc_code='',  status_update=None, show_messagebox=True, update_progress=None):
    """Fill VDC and District codes in the database, update status using the provided function, and optionally show a message box."""
    startTime = time.time()
    path = shared_data.directory
    exception_list = open(os.path.join(path, "exception_list_att_fill_vdc_dis_code.csv"), "a")
    allerror = open(os.path.join(path, "regex.csv"), "a")
    exception_list.truncate(0)
    allerror.truncate(0)

    # Update status to indicate the start of the process
    if status_update:
        status_update("Starting VDC and District code filling process...")

    mdb_list = shared_data.filtered_mdb_files
    for count, mdb_file in enumerate(mdb_list, start=1):
        parcelfile = os.path.join(mdb_file, "Parcel")
        print(parcelfile)

        filename = os.path.basename(mdb_file)
        try:
            arcpy.Compact_management(mdb_file)
        except Exception as e:
            exception_list.write("Compact Error for: " + filename + "\n")
            print("Compact error for " + filename)
            if status_update:
                status_update("Error compacting {}: {}".format(filename, str(e)))

        try:
            if district_code and int(district_code):
                arcpy.CalculateField_management(parcelfile, "DISTRICT", int(district_code), "PYTHON")
            if vdc_code and int(vdc_code):
                arcpy.CalculateField_management(parcelfile, "VDC", int(vdc_code), "PYTHON")
        except Exception as e:
            exception_list.write("Attribute fill Error for: " + filename + "\n")
            allerror.write(filename + ",error\n")
            if status_update:
                status_update("Error filling attributes for {}: {}".format(filename, str(e)))

        if status_update:
            status_update("Processed {} \n({}/{})".format(filename, count, len(mdb_list)))

        if update_progress:
            x= count/float(len(mdb_list))
            progress_value = (x) * 100
            update_progress(progress_value, len(mdb_list))
        self.master.update_idletasks()  # Ensure GUI updates

    exception_list.close()
    allerror.close()

    if show_messagebox:
        tkMessageBox.showinfo(title="Fix Attribute Errors", message="Done")

    if status_update:
        status_update("VDC and District code filling process complete.")

    print('The script took {0} seconds!'.format(time.time() - startTime))
