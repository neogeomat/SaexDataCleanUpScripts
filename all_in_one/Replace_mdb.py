import urllib2

import requests

import shared_data
def replaceMDb(self,central_meridian):  # sourcery skip
    import tkMessageBox
    import arcpy
    import os
    import time
    arcpy.env.overwriteOutput = True
    Folder_Location = "d:"
    DataCleanTemp = Folder_Location + "\\DataCleanTemp"
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_whole_mdb_replace.csv","a")
    exception_list.truncate(0)
    count = 0

    option_choosed=central_meridian
    import os
    import urllib2

    def download_file_from_github(url, save_path, retries=3, delay=5):
        attempt = 0
        while attempt < retries:
            try:
                # Send a GET request to the URL
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Write the content to a file
                with open(save_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            out_file.write(chunk)
                print("File downloaded successfully and saved to {}".format(save_path))
                return  # Exit the function if download is successful
            except requests.exceptions.RequestException as e:
                print("Failed to download file. Error: {}".format(e))
                attempt += 1
                if attempt < retries:
                    print("Retrying in {} seconds...".format(delay))
                    time.sleep(delay)  # Wait before retrying
                else:
                    print("All retry attempts failed.")

    local_cm_loc = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"
    if not os.path.exists(local_cm_loc):
        github_url = "https://github.com/neogeomat/SaexDataCleanUpScripts/blob/master/templates/" + option_choosed
        # Derive the filename from the URL
        local_filename = github_url.split("/")[-1]

        # Define the local path to save the file
        local_path = os.path.join(os.path.dirname(__file__), local_filename)

        download_file_from_github(github_url,local_path)
        blank_data = "https://github.com/neogeomat/SaexDataCleanUpScripts/blob/master/templates/" + option_choosed
    else:
        blank_data="D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"+option_choosed

    print ("option choosed " + blank_data)
    feature_classes = arcpy.ListFeatureClasses(blank_data)
    if feature_classes:
        for fc in feature_classes:
            print(fc)
    else:
        print("No feature classes found in the specified location.")

    for i in mdb_list:
        try:
            count +=1
            out_data="D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\test.mdb"
            arcpy.Copy_management(blank_data,out_data)
            if arcpy.Exists(i+"\\Parcel"):
                arcpy.Append_management(i+"\\Parcel",out_data+"\\Parcel","NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(i+"\\Parcel")
            else:
                print("Parcel Layer not found for, "+i)
            if arcpy.Exists(i+"\\Construction"):
                arcpy.Append_management(i+"\\Construction",out_data+"\\Construction","NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(i+"\\Construction")
            else:
                print("Construction Layer not found for, " + i)
            if arcpy.Exists(i + "\\Parcel_History"):
                arcpy.Append_management(i+"\\Parcel_History",out_data+"\\Parcel_History","NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(i + "\\Parcel_History")
            else:
                print("Parcel_History Layer not found for, " + i)
            if arcpy.Exists(i + "\\Segments"):
                arcpy.Append_management(i+"\\Segments",out_data+"\\Segments","NO_TEST")
                arcpy.RecalculateFeatureClassExtent_management(i + "\\Segments")
            else:
                print("Segments Layer not found for, " + i)
            arcpy.env.workspace=i;
            point_features_list=arcpy.ListFeatureClasses("*","Point")
            for pt_feature in point_features_list:
                arcpy.AddField_management(pt_feature,"Symbol_Type", "TEXT")
                layer_name = os.path.basename(pt_feature)
                expression=layer_name
                arcpy.CalculateField_management(pt_feature, "Symbol_Type", '"'+expression+'"', "PYTHON")
                arcpy.Append_management(pt_feature, out_data + "\\Other_Symbols", "NO_TEST")
            arcpy.Copy_management(out_data,i)
            arcpy.Delete_management(out_data)

            # Copu objectids to Ids field for parfid matching
            # Process: Add Field (3)
            arcpy.AddField_management (i  + "\\Parcel", "Ids", "LONG", "", "", "", "", "NULLABLE",
                                       "NON_REQUIRED", "")
            # Process: Calculate Field (3)
            arcpy.CalculateField_management (i + "\\Parcel", "IDS", "[OBJECTID]", "VB", "")

            ## parfid in segments
            # Process: Spatial Join
            arcpy.Intersect_analysis ([i + "\\Segments", i + "\\Parcel"],
                                      DataCleanTemp + "\\SegmentsParcelIntersect.shp", "", "", "line")
            arcpy.SpatialJoin_analysis (DataCleanTemp + "\\SegmentsParcelIntersect.shp", i + "\\Parcel",
                                        DataCleanTemp + "\\SegWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                        "SegNo \"SegNo\" true true false 2 Short 0 0 ,First,#,"
                                        + i + "\\Segments,SegNo,-1,-1;Boundty \"Boundty\" true true false 2 Short 0 0 ,First,#,"
                                        + i + "\\Segments,Boundty,-1,-1;ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"
                                        + i + "\\Segments,ParFID,-1,-1;MBoundTy \"MBoundTy\" true true false 2 Short 0 0 ,First,#,"
                                        + i + "\\Segments,MBoundTy,-1,-1;ABoundTy \"ABoundTy\" true true false 2 Short 0 0 ,First,#,"
                                        + i + "\\Segments,ABoundTy,-1,-1;Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                        + i + "\\Segments,Shape_Length,-1,-1;MarginName \"MarginName\" true true false 50 Text 0 0 ,First,#,"
                                        + i + "\\Segments,MarginName,-1,-1;Ids \"Ids\" true true false 0 Long 0 0 ,First,#,"
                                        + i + "\\Parcel,Ids,-1,-1", "INTERSECT", "", "")

            # Process: Calculate Field (2)
            arcpy.CalculateField_management (DataCleanTemp + "\\SegWithParFid.shp", "ParFID", "[ids]", "VB", "")

            # Process: Delete Features
            arcpy.CopyFeatures_management (blank_data + "\\Segments", i + "\\Segments", "", "0",
                                           "0",
                                           "0")

            # Process: Append
            arcpy.Append_management (DataCleanTemp + "\\SegWithParFid.shp", i + "\\Segments", "NO_TEST")

            ## parfid in construction
            # Process: Spatial Join

            arcpy.Intersect_analysis ([i + "\\Construction", i + "\\Parcel"],
                                      DataCleanTemp + "\\ConstructionParcelIntersect.shp", "", "", "")
            arcpy.SpatialJoin_analysis (DataCleanTemp + "\\ConstructionParcelIntersect.shp",
                                        i + "\\Parcel",
                                        DataCleanTemp + "\\ConsWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                        "ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"
                                        + DataCleanTemp + "\\ConstructionParcelIntersect.shp,ParFID,-1,-1;ConsTy \"ConsTy\" true true false 2 Short 0 0 ,First,#,"
                                        + DataCleanTemp + "\\ConstructionParcelIntersect.shp,ConsTy,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                        + DataCleanTemp + "\\ConstructionParcelIntersect.shp,Shape_Length,-1,-1;ids \"ids\" true true false 0 Long 0 0 ,First,#,"
                                        + i + "\\Parcel,ids,-1,-1", "INTERSECT", "", "")

            # Process: Calculate Field (2)
            arcpy.CalculateField_management (DataCleanTemp + "\\ConsWithParFid.shp", "ParFID", "[ids]", "VB", "")

            # arcpy.Delete_management (i + "\\Construction")
            arcpy.CopyFeatures_management (blank_data + "\\Construction", i + "\\Construction",
                                           "",
                                           "0", "0", "0")
            arcpy.Append_management (DataCleanTemp + "\\ConsWithParFid.shp", i + "\\Construction",
                                     "NO_TEST")

        except:
            exception_list.write("Replace Whole Mdb Error for ," + i + "\n")
        print (i + " (" + str(count) + "/" + str(len(mdb_list)) + ")")

    print("Replace Whole Mdb complete")
    exception_list.close()
    print ('The script took {0} second !'.format(time.time() - startTime))
    tkMessageBox.showinfo(title="Extent ReCalculation database", message="Done")