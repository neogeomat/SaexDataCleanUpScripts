import tkMessageBox
import arcpy
import os
import time
import shared_data

def replaceMDb(self, central_meridian, status_update=None, show_messagebox=True):
    """Replace MDB files with updated data from specified templates, with status updates and optional message box."""
    arcpy.env.overwriteOutput = True
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(os.path.join(path, "exception_list_whole_mdb_replace.csv"), "a")
    exception_list.truncate(0)
    count = 0


    option_choosed = central_meridian
    local_cm_loc = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"
    blank_data = os.path.join(local_cm_loc, option_choosed)

    print("Option chosen: " + blank_data)
    arcpy.env.workspace = blank_data

    for count, i in enumerate(mdb_list, start=1):
        try:
            out_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\test.mdb"
            arcpy.Copy_management(blank_data, out_data)

            if arcpy.Exists(os.path.join(i, "Parcel")):
                arcpy.Append_management(os.path.join(i, "Parcel"), os.path.join(out_data, "Parcel"), "NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(os.path.join(i, "Parcel"))
            else:
                print("Parcel Layer not found for " + i)

            if arcpy.Exists(os.path.join(i, "Construction")):
                arcpy.Append_management(os.path.join(i, "Construction"), os.path.join(out_data, "Construction"),
                                        "NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(os.path.join(i, "Construction"))
            else:
                print("Construction Layer not found for " + i)

            if arcpy.Exists(os.path.join(i, "Parcel_History")):
                arcpy.Append_management(os.path.join(i, "Parcel_History"), os.path.join(out_data, "Parcel_History"),
                                        "NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(os.path.join(i, "Parcel_History"))
            else:
                print("Parcel_History Layer not found for " + i)

            if arcpy.Exists(os.path.join(i, "Segments")):
                arcpy.Append_management(os.path.join(i, "Segments"), os.path.join(out_data, "Segments"), "NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(os.path.join(i, "Segments"))
            else:
                print("Segments Layer not found for " + i)

            arcpy.env.workspace = i
            point_features_list = arcpy.ListFeatureClasses("*", "Point")

            for pt_feature in point_features_list:
                arcpy.AddField_management(pt_feature, "Symbol_Type", "TEXT")
                layer_name = os.path.basename(pt_feature)
                expression = layer_name
                arcpy.CalculateField_management(pt_feature, "Symbol_Type", '"' + expression + '"', "PYTHON")
                arcpy.Append_management(pt_feature, os.path.join(out_data, "Other_Symbols"), "NO_TEST")

            arcpy.Copy_management(out_data, i)
            arcpy.Delete_management(out_data)


            if status_update:
                status_update("Processed {} ({}/{})".format(i, count, len(mdb_list)))

        except Exception as e:
            exception_list.write("Replace Whole Mdb Error for: " + i + "\n")
            print("Error replacing whole MDB for " + i + "\nError: ", e)

    exception_list.close()
    print("Replace Whole Mdb process complete")
    print('The script took {0} seconds!'.format(time.time() - startTime))

    if show_messagebox:
        tkMessageBox.showinfo(title="Extent ReCalculation database", message="Done")
