# -*- coding: utf-8 -*-
import shared_data
import time
from csv_logging import create_csv_log_file, write_error_to_csv
import tkMessageBox
import arcpy
import os
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications


def Fix_Gap_Overlap(self,central_meridian,status_update=None, show_messagebox=True, update_progress=None):
    starttime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    allerror = open(os.path.join(path, "regex.csv"), "a")
    exception_list = open(os.path.join(path, "exception_list_fill_gap_overlap.csv"), "a")
    exception_list.truncate(0)

    error_log_path = os.path.join(shared_data.directory, "error_log.csv")

    # Create and open the CSV file for error logging
    file_handler, csv_writer = create_csv_log_file(error_log_path)
    arcpy.env.overwriteOutput = True
    count = 1
    total_mdbs = len(shared_data.filtered_mdb_files)


    option_choosed=central_meridian
    if status_update:
        status_update("Starting fix gap overlap process...")

    for progress, i in enumerate(mdb_list, start=1):
        filename = os.path.basename(i)
        if status_update:
                status_update("Checking Attribute for {} \n({}/{})".format(filename, count, total_mdbs))
        try:
            parcel_list=arcpy.GetCount_management(i+"\\Parcel")
            no_of_attribute=int(parcel_list.getOutput(0))
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
            if(no_of_attribute==0):
                exception_list.write("Parcel layer has 0 Features for ," + i + "\n")
                count+=1
                # Send Telegram notification for error
                error_message = "⚠️ Fix Gap Overlap Error!\n\n" \
                                "🗂 Path: {}\n" \
                                "📜 Script: Fix_Gap_Overlap\n" \
                                "🗂 File: {}\n" \
                                "❌ Error: {}".format(path, i, str("No Parcel Layer"))
                send_telegram_message(error_message)

            else:
                # Local variables:
                Folder_Location = "d:\\"
                # Data_Location = raw_input('location of mdb')
                # Data_Location = 'D:\SATUNGAL\Santungal_1Ka\Santungal_1Ka.mdb'
                Data_Location = i
                if (os.path.exists ("D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"+option_choosed)):
                    Blank_Template = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"+option_choosed
                else:
                    print("Blank Template database not found, install saex")
                    # Send Telegram notification for error
                    error_message = "⚠️ Fix Gap Overlap Error!\n\n" \
                                    "🗂 Path: {}\n" \
                                    "📜 Script: Fix_Gap_Overlap\n" \
                                    "🗂 File: {}\n" \
                                    "❌ Error: {}".format(path, i, str("Blank template not Found"))
                    send_telegram_message(error_message)

                    exit ()
                # Process: Create Temp Folder to strore all processing intermediaries
                DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                if (os.path.exists(DataCleanTemp)):  # delete folder if exits, otherwise it causes error
                    arcpy.Delete_management(DataCleanTemp, "Folder")
                if (arcpy.Exists("selection_parcel")):
                    arcpy.Delete_management("selection_parcel")
                arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
                DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                arcpy.env.workspace = DataCleanTemp
                arcpy.env.overwriteOutput = True
                count += 1

                arcpy.FeatureClassToFeatureClass_conversion(Data_Location + "\\Parcel", DataCleanTemp, "Parcel.shp", "",
                                                            "PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,PARCELKEY,-1,-1;PARCELNO \"PARCELNO\" true true false 4 Long 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 2 Short 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,DISTRICT,-1,-1;VDC \"VDC\" true true false 2 Short 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,GRIDS1,-1,-1;PARCELTY \"PARCELTY\" true true false 2 Short 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,PARCELTY,-1,-1;ParcelNote \"ParcelNote\" true false false 200 Text 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,ParcelNote,-1,-1;Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,"
                                                            + Data_Location + "\\Parcel,Shape_Area,-1,-1", "")

                # arcpy.EliminatePolygonPart_management(DataCleanTemp + "\\Parcel.shp", DataCleanTemp + "\\Parcel1.shp", "AREA", "0.005 SquareMeters", "0", "ANY")

                # Process: Feature To Point
                arcpy.FeatureToPoint_management(DataCleanTemp + "\\Parcel.shp", DataCleanTemp + "\\ParcelCentroid.shp",
                                                "INSIDE")
                arcpy.Delete_management(Data_Location + "\\Parcel")

                # Process: Copy Features
                arcpy.CopyFeatures_management(Blank_Template + "\\Parcel", Data_Location + "\\Parcel", "", "0", "0",
                                              "0")

                # Process: Feature Class To Coverage
                cov1 = DataCleanTemp + "\\cov1"
                arcpy.FeatureclassToCoverage_conversion(DataCleanTemp + "\\Parcel.shp REGION", cov1, "0.005 Meters",
                                                        "DOUBLE")

                # Process: Copy Features
                arcpy.CopyFeatures_management(DataCleanTemp + "\\cov1\\polygon", DataCleanTemp + "\\CleanPoly.shp", "",
                                              "0",
                                              "0", "0")

                # Process: Spatial Join
                arcpy.SpatialJoin_analysis(DataCleanTemp + "\\CleanPoly.shp", DataCleanTemp + "\\ParcelCentroid.shp",
                                           DataCleanTemp + "\\NewJoinedData.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                           "AREA \"AREA\" true true false 19 Double 0 0 ,First,#,"
                                           + DataCleanTemp + "\\CleanPoly.shp,AREA,-1,-1;PERIMETER \"PERIMETER\" true true false 19 Double 0 0 ,First,#,"
                                           + DataCleanTemp + "\\CleanPoly.shp,PERIMETER,-1,-1;COV1_ \"COV1_\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\CleanPoly.shp,COV1_,-1,-1;COV1_ID \"COV1_ID\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\CleanPoly.shp,COV1_ID,-1,-1;PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,PARCELKEY,-1,-1;PARCELNO \"PARCELNO\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,DISTRICT,-1,-1;VDC \"VDC\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,GRIDS1,-1,-1;PARCELTY \"PARCELTY\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,PARCELTY,-1,-1;Shape_Leng \"Shape_Leng\" true true false 19 Double 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,Shape_Leng,-1,-1;Shape_Area \"Shape_Area\" true true false 19 Double 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,Shape_Area,-1,-1;ParcelNote \"ParcelNote\" true true false 200 Text 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,ParcelNote,-1,-1;remarks \"remarks\" true true false 10 Text 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,remarks,-1,-1;ORIG_FID \"ORIG_FID\" true true false 10 Long 0 10 ,First,#,"
                                           + DataCleanTemp + "\\ParcelCentroid.shp,ORIG_FID,-1,-1", "CONTAINS", "", "")

                arcpy.MakeFeatureLayer_management(DataCleanTemp + "\\NewJoinedData.shp", "selection_parcel")
                arcpy.SelectLayerByAttribute_management("selection_parcel", "NEW_SELECTION", '"Area"<0.05')
                arcpy.Eliminate_management("selection_parcel", DataCleanTemp + "\\Parcel1.shp", "LENGTH")
                arcpy.SelectLayerByAttribute_management("selection_parcel", "CLEAR_SELECTION")
                if (arcpy.Exists("selection_parcel")):
                    arcpy.Delete_management("selection_parcel")

                # Process: Append
                arcpy.Append_management(DataCleanTemp + "\\Parcel1.shp", Data_Location + "\\Parcel", "NO_TEST")

                # Copu objectids to Ids field for parfid matching
                # Process: Add Field (3)
                arcpy.AddField_management(Data_Location + "\\Parcel", "Ids", "LONG", "", "", "", "", "NULLABLE",
                                          "NON_REQUIRED", "")

                # Process: Calculate Field (3)
                arcpy.CalculateField_management(Data_Location + "\\Parcel", "IDS", "[OBJECTID]", "VB", "")

                ## parfid in segments
                # Process: Spatial Join
                arcpy.Intersect_analysis([Data_Location + "\\Segments", Data_Location + "\\Parcel"],
                                         DataCleanTemp + "\\SegmentsParcelIntersect.shp", "", "", "line")
                arcpy.SpatialJoin_analysis(DataCleanTemp + "\\SegmentsParcelIntersect.shp", Data_Location + "\\Parcel",
                                           DataCleanTemp + "\\SegWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                           "SegNo \"SegNo\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,SegNo,-1,-1;Boundty \"Boundty\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,Boundty,-1,-1;ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,ParFID,-1,-1;MBoundTy \"MBoundTy\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,MBoundTy,-1,-1;ABoundTy \"ABoundTy\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,ABoundTy,-1,-1;Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,Shape_Length,-1,-1;MarginName \"MarginName\" true true false 50 Text 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,MarginName,-1,-1;Ids \"Ids\" true true false 0 Long 0 0 ,First,#,"
                                           + Data_Location + "\\Parcel,Ids,-1,-1", "INTERSECT", "", "")

                # Process: Calculate Field (2)
                arcpy.CalculateField_management(DataCleanTemp + "\\SegWithParFid.shp", "ParFID", "[ids]", "VB", "")

                # Process: Delete Features
                arcpy.Delete_management(Data_Location + "\\Segments")
                arcpy.CopyFeatures_management(Blank_Template + "\\Segments", Data_Location + "\\Segments", "", "0",
                                              "0",
                                              "0")

                # Process: Append
                arcpy.Append_management(DataCleanTemp + "\\SegWithParFid.shp", Data_Location + "\\Segments", "NO_TEST")

                ## parfid in construction
                # Process: Spatial Join

                arcpy.Intersect_analysis([Data_Location + "\\Construction", Data_Location + "\\Parcel"],
                                         DataCleanTemp + "\\ConstructionParcelIntersect.shp", "", "", "")
                arcpy.SpatialJoin_analysis(DataCleanTemp + "\\ConstructionParcelIntersect.shp",
                                           Data_Location + "\\Parcel",
                                           DataCleanTemp + "\\ConsWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                           "ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ConstructionParcelIntersect.shp,ParFID,-1,-1;ConsTy \"ConsTy\" true true false 2 Short 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ConstructionParcelIntersect.shp,ConsTy,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ConstructionParcelIntersect.shp,Shape_Length,-1,-1;ids \"ids\" true true false 0 Long 0 0 ,First,#,"
                                           + Data_Location + "\\Parcel,ids,-1,-1", "INTERSECT", "", "")

                # Process: Calculate Field (2)
                arcpy.CalculateField_management(DataCleanTemp + "\\ConsWithParFid.shp", "ParFID", "[ids]", "VB", "")

                arcpy.Delete_management(Data_Location + "\\Construction")
                arcpy.CopyFeatures_management(Blank_Template + "\\Construction", Data_Location + "\\Construction", "",
                                              "0", "0", "0")
                arcpy.Append_management(DataCleanTemp + "\\ConsWithParFid.shp", Data_Location + "\\Construction",
                                        "NO_TEST")

                # Delete Construction features with area < 1
                arcpy.MakeFeatureLayer_management(Data_Location + "\\Construction", "cons_layer")
                arcpy.SelectLayerByAttribute_management("cons_layer", "NEW_SELECTION", "[Shape_Area] < 1")
                arcpy.DeleteFeatures_management("cons_layer")
                arcpy.Delete_management("cons_layer")



                ## remove processing folder
                # Process: Delete
                arcpy.Delete_management(DataCleanTemp, "Folder")

                calculate_suspicious_and_circularity(Data_Location + "\\Parcel")

                ## Finalizing data
                # Process: Delete Field
                arcpy.DeleteField_management(Data_Location + "\\Parcel", "IDS")
                try:
                    arcpy.CalculateField_management(Data_Location + "\\Parcel", "PARCELKEY",
                                                "str( !GRIDS1!).ljust(9,'a') + str( !PARCELNO!).zfill(6) + str( !DISTRICT!).zfill(2) + str( !VDC! ).zfill(4) + str( !WARDNO!).zfill(2)",
                                                "PYTHON_9.3", "")
                except:
                    exception_list.write("ParcelKey Error for ,"+i+"\n")

                parcel_path = Data_Location + "\\Parcel"

                arcpy.Compact_management(Data_Location)
                print(Data_Location + " cleaning process complete")
        except Exception as e:
            exception_list.write("Gap Overlap Error for ," + i + "\n")
            write_error_to_csv(csv_writer, os.path.basename(i), str(e))
            print ("error for "+i)
            if status_update:
                status_update("Error during processing: {}".format(str(e)))
            # if show_messagebox:
            #     tkMessageBox.showerror(title="Error", message="An error occurred: {}".format(str(e)))
                # Send Telegram notification for error
                error_message = "⚠️ Fix Gap Overlap Error!\n\n" \
                                "🗂 Path: {}\n" \
                                "📜 Script: Fix_Gap_Overlap\n" \
                                "🗂 File: {}\n" \
                                "❌ Error: {}".format(path, i, str(e))
                send_telegram_message(error_message)

        if update_progress:
            x= progress/float(total_mdbs)
            progress_value = (x) * 100
            update_progress(progress_value, total_mdbs)
        self.master.update_idletasks()  # Ensure GUI updates

    print("Fix Gap and Overlap Process complete")
    endtime = time.time()
    print("Time taken: " + str(endtime - starttime))
    if status_update:
        status_update("Fix Gap and Overlap Completed.")

    exception_list.close()
    allerror.close()

    if show_messagebox:
        tkMessageBox.showinfo(title="Check Attribute Errors", message="Fix gap and overlap process is complete.")
    # Send Telegram notification for successful processing
    success_message = "✅ Fix Gap Overlap Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: Fix_Gap_Overlap\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - starttime)
    send_telegram_message(success_message)


def calculate_suspicious_and_circularity(parcel_path):

    import math

    def add_field_if_not_exists(field_name, field_type, field_length=None):
        fields = arcpy.ListFields(parcel_path, field_name)
        if not fields:
            arcpy.AddField_management(parcel_path, field_name, field_type, field_length=field_length)
        else:
            print("Field '{}' already exists.".format(field_name))

    # Check and add fields if they don't exist
    add_field_if_not_exists("suspicious", "TEXT", field_length=5)
    add_field_if_not_exists("circularity", "FLOAT")

    # Calculate Circularity
    arcpy.CalculateField_management(parcel_path, "circularity",
                                    "4 * 3.14159265 * !SHAPE_Area!  / !SHAPE_Length!**2", "PYTHON")

    # Calculate Suspicious
    expression = "check(!Shape_Area!,!circularity!)"
    codeblock = """def check(Shape_Area,circularity):
    if(Shape_Area < 5 and circularity < 0.2):
        return 'yes'
    else:
        return 'no'
    """
    arcpy.CalculateField_management(parcel_path, "suspicious", expression, "PYTHON", codeblock)



