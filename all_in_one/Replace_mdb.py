import shutil
import tkMessageBox
import arcpy
import os
import time
import shared_data
import requests


def replaceMDb(self, central_meridian, status_update=None, show_messagebox=True):
    """Replace MDB files with updated data from specified templates, with status updates and optional message box."""
    arcpy.env.overwriteOutput = True
    Folder_Location = "d:"
    DataCleanTemp = Folder_Location + "\\DataCleanTemp"
    if (os.path.exists(DataCleanTemp)):  # delete folder if exits, otherwise it causes error
        arcpy.Delete_management(DataCleanTemp, "Folder")
    if (arcpy.Exists("selection_parcel")):
        arcpy.Delete_management("selection_parcel")
    arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
    DataCleanTemp = Folder_Location + "\\DataCleanTemp"
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list = open(os.path.join(path, "exception_list_whole_mdb_replace.csv"), "a")
    exception_list.truncate(0)
    count = 0

    def download_file_from_github(url, save_path, retries=3, delay=5):
        attempt = 0
        while attempt < retries:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an exception for HTTP errors

                with open(save_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            out_file.write(chunk)
                print("File downloaded successfully and saved to {}".format(save_path))
                return
            except requests.exceptions.RequestException as e:
                print("Failed to download file. Error: {}".format(e))
                attempt += 1
                if attempt < retries:
                    print("Retrying in {} seconds...".format(delay))
                    time.sleep(delay)  # Wait before retrying
                else:
                    print("All retry attempts failed.")

    option_choosed = central_meridian
    local_cm_loc = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"
    blank_data = os.path.join(local_cm_loc, option_choosed)

    # if not os.path.exists(local_cm_loc):
    #     github_url = "https://github.com/neogeomat/SaexDataCleanUpScripts/blob/master/templates/" + option_choosed
    #     local_filename = github_url.split("/")[-1]
    #     local_path = os.path.join(os.path.dirname(__file__), local_filename)
    #     download_file_from_github(github_url, local_path)
    #     blank_data = "https://github.com/neogeomat/SaexDataCleanUpScripts/blob/master/templates/" + option_choosed
    # else:
    #     blank_data = os.path.join(local_cm_loc, option_choosed)

    print("Option chosen: " + blank_data)
    arcpy.env.workspace = blank_data

    feature_classes = arcpy.ListFeatureClasses()

    if feature_classes:
        for fc in feature_classes:
            print(fc)
    else:
        print("No feature classes found in the specified location.")

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

            arcpy.AddField_management(os.path.join(i, "Parcel"), "Ids", "LONG", "", "", "", "", "NULLABLE",
                                      "NON_REQUIRED", "")
            arcpy.CalculateField_management(os.path.join(i, "Parcel"), "Ids", "[OBJECTID]", "VB", "")

            arcpy.Intersect_analysis([os.path.join(i, "Segments"), os.path.join(i, "Parcel")],
                                     os.path.join(DataCleanTemp, "SegmentsParcelIntersect.shp"), "", "", "line")
            arcpy.SpatialJoin_analysis(os.path.join(DataCleanTemp, "SegmentsParcelIntersect.shp"),
                                       os.path.join(i, "Parcel"),
                                       os.path.join(DataCleanTemp, "SegWithParFid.shp"), "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       "SegNo \"SegNo\" true true false 2 Short 0 0 ,First,#," + os.path.join(i,
                                                                                                              "Segments") + ",SegNo,-1,-1;"
                                                                                                                            "Boundty \"Boundty\" true true false 2 Short 0 0 ,First,#," + os.path.join(
                                           i, "Segments") + ",Boundty,-1,-1;"
                                                            "ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#," + os.path.join(
                                           i, "Segments") + ",ParFID,-1,-1;"
                                                            "MBoundTy \"MBoundTy\" true true false 2 Short 0 0 ,First,#," + os.path.join(
                                           i, "Segments") + ",MBoundTy,-1,-1;"
                                                            "ABoundTy \"ABoundTy\" true true false 2 Short 0 0 ,First,#," + os.path.join(
                                           i, "Segments") + ",ABoundTy,-1,-1;"
                                                            "Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + os.path.join(
                                           i, "Segments") + ",Shape_Length,-1,-1;"
                                                            "MarginName \"MarginName\" true true false 50 Text 0 0 ,First,#," + os.path.join(
                                           i, "Segments") + ",MarginName,-1,-1;"
                                                            "Ids \"Ids\" true true false 0 Long 0 0 ,First,#," + os.path.join(
                                           i, "Parcel") + ",Ids,-1,-1", "INTERSECT", "", "")

            arcpy.CalculateField_management(os.path.join(DataCleanTemp, "SegWithParFid.shp"), "ParFID", "[ids]", "VB",
                                            "")

            arcpy.CopyFeatures_management(os.path.join(blank_data, "Segments"), os.path.join(i, "Segments"), "", "0",
                                          "0", "0")

            arcpy.Append_management(os.path.join(DataCleanTemp, "SegWithParFid.shp"), os.path.join(i, "Segments"),
                                    "NO_TEST")

            arcpy.Intersect_analysis([os.path.join(i, "Construction"), os.path.join(i, "Parcel")],
                                     os.path.join(DataCleanTemp, "ConstructionParcelIntersect.shp"), "", "", "")
            arcpy.SpatialJoin_analysis(os.path.join(DataCleanTemp, "ConstructionParcelIntersect.shp"),
                                       os.path.join(i, "Parcel"),
                                       os.path.join(DataCleanTemp, "ConsWithParFid.shp"), "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       "ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#," + os.path.join(
                                           DataCleanTemp, "ConstructionParcelIntersect.shp") + ",ParFID,-1,-1;"
                                                                                               "ConsTy \"ConsTy\" true true false 2 Short 0 0 ,First,#," + os.path.join(
                                           DataCleanTemp, "ConstructionParcelIntersect.shp") + ",ConsTy,-1,-1;"
                                                                                               "Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + os.path.join(
                                           DataCleanTemp, "ConstructionParcelIntersect.shp") + ",Shape_Length,-1,-1;"
                                                                                               "ids \"ids\" true true false 0 Long 0 0 ,First,#," + os.path.join(
                                           i, "Parcel") + ",ids,-1,-1", "INTERSECT", "", "")

            arcpy.CalculateField_management(os.path.join(DataCleanTemp, "ConsWithParFid.shp"), "ParFID", "[ids]", "VB",
                                            "")

            arcpy.CopyFeatures_management(os.path.join(blank_data, "Construction"), os.path.join(i, "Construction"), "",
                                          "0", "0", "0")
            arcpy.Append_management(os.path.join(DataCleanTemp, "ConsWithParFid.shp"), os.path.join(i, "Construction"),
                                    "NO_TEST")

            # Delete the folder and all its contents
            if os.path.exists(DataCleanTemp) and os.path.isdir(DataCleanTemp):
                shutil.rmtree(DataCleanTemp)

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
