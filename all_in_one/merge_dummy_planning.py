import tkMessageBox
import arcpy
import shared_data
import os as os

def merge_dummy_planning(self,choosen_meridian):
    path = shared_data.directory
    exception_file_path = os.path.join(path, "exception_list_dummy.csv")
    merged_file_name = "{}_merged.mdb".format(os.path.basename(path))
    merged_file_path = os.path.join(path, merged_file_name)
    blank_mdb_path = r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates'
    blank_mdb =os.path.join(blank_mdb_path,choosen_meridian)
    try:
        with open(exception_file_path, "a") as exception_list:
            if os.path.exists(merged_file_path):
                os.remove(merged_file_path)
                print("Old merged file deleted")

            mdb_list = shared_data.filtered_mdb_files
            total_mdbs = len(mdb_list)

            for i in mdb_list:
                arcpy.env.workspace = i

                Folder_Location = "d:"
                # Parcel = "Parcel"
                # Data_Location = "D:\\DissolveByParcelKey\\Dahachowk_1Kha.mdb"
                Data_Location = i

                if (os.path.exists(blank_mdb)):
                    BLANK84_Template = blank_mdb
                else:
                    print("Blank Template database not found, install saex")
                    exit()
                # Process: Create Temp Folder to strore all processing intermediaries
                DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                if (os.path.exists(DataCleanTemp)): # delete folder if exits, otherwise it causes error
                    arcpy.Delete_management(DataCleanTemp, "Folder")
                arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
                DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                file_id = i[-12:-4]
                arcpy.CreateFolder_management(DataCleanTemp, file_id)
                DataCleanTemp = DataCleanTemp + "\\" + file_id
                arcpy.env.workspace = DataCleanTemp

                # Generate parcelkey in mdb
                arcpy.CalculateField_management(Data_Location + "\\Parcel", "PARCELKEY","str( !GRIDS1!).ljust(9,'a') + str( !PARCELNO!).zfill(6) + str( !DISTRICT!).zfill(2) + str( !VDC! ).zfill(4) + str( !WARDNO!).zfill(2)","PYTHON_9.3", "")

                arcpy.FeatureClassToFeatureClass_conversion(Data_Location + "\\Parcel", DataCleanTemp, "Parcel.shp", "", "PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#," + Data_Location + "\\Parcel,PARCELKEY,-1,-1;PARCELNO \"PARCELNO\" true true false 4 Long 0 0 ,First,#," + Data_Location + "\\Parcel,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Parcel,DISTRICT,-1,-1;VDC \"VDC\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Parcel,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#," + Data_Location + "\\Parcel,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#," + Data_Location + "\\Parcel,GRIDS1,-1,-1;PARCELTY \"PARCELTY\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Parcel,PARCELTY,-1,-1;ParcelNote \"ParcelNote\" true false false 200 Text 0 0 ,First,#," + Data_Location + "\\Parcel,ParcelNote,-1,-1;Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + Data_Location + "\\Parcel,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#," + Data_Location + "\\Parcel,Shape_Area,-1,-1", "")

                Parcel = DataCleanTemp + "\\Parcel.shp"
                # Process: Feature To Point
                arcpy.FeatureToPoint_management(Parcel, DataCleanTemp + "\\ParcelCentroid.shp", "INSIDE")

                # Process: Select Layer By Attribute
                temp = "temp" + file_id
                arcpy.MakeFeatureLayer_management(Parcel, temp)
                arcpy.SelectLayerByAttribute_management(temp, 'NEW_SELECTION', 'PARCELNO < 9000 AND PARCELNO <> 0')

                # arcpy.SelectLayerByAttribute_management("tempInvert", "SWITCH_SELECTION")
                # Process: Dissolve
                arcpy.Dissolve_management(temp, DataCleanTemp + "\\ParcelDissolve.shp", "PARCELNO;DISTRICT;VDC;WARDNO;GRIDS1", "", "SINGLE_PART", "DISSOLVE_LINES")
                arcpy.MakeFeatureLayer_management(Parcel, temp +"invert","PARCELNO >= 9000 OR PARCELNO = 0")
                arcpy.SelectLayerByAttribute_management(temp + "invert", "NEW_SELECTION", "PARCELNO >= 9000 OR PARCELNO = 0")
                arcpy.CopyFeatures_management(temp + "invert", DataCleanTemp + "\\ParcelRemain.shp")

                # Join management
                arcpy.SpatialJoin_analysis(DataCleanTemp + "\\ParcelDissolve.shp", DataCleanTemp + "\\ParcelCentroid.shp", DataCleanTemp + "\\NewJoinedData.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL","PARCELNO \"PARCELNO\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,DISTRICT,-1,-1;VDC \"VDC\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelDissolve.shp,GRIDS1,-1,-1;PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelCentroid.shp,PARCELKEY,-1,-1;PARCELTY \"PARCELTY\" true true false 10 Long 0 10 ,First,#," + DataCleanTemp + "\\ParcelCentroid,shp,PARCELTY,-1,-1;ParcelNote \"ParcelNote\" true true false 200 Text 0 0 ,First,#," + DataCleanTemp + "\\ParcelCentroid.shp,ParcelNote,-1,-1", "CONTAINS", "", "")

                arcpy.Delete_management(Data_Location + "\\Parcel")
                # Process: Copy Features
                arcpy.CopyFeatures_management(BLANK84_Template + "\\Parcel", Data_Location + "\\Parcel", "", "0", "0", "0")
                arcpy.Append_management(DataCleanTemp + "\\NewJoinedData.shp", Data_Location + "\\Parcel", "NO_TEST")
                arcpy.Append_management(DataCleanTemp + "\\ParcelRemain.shp", Data_Location + "\\Parcel", "NO_TEST")

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
                arcpy.CopyFeatures_management(BLANK84_Template + "\\Segments", Data_Location + "\\Segments", "", "0",
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
                arcpy.CopyFeatures_management(BLANK84_Template + "\\Construction", Data_Location + "\\Construction", "",
                                              "0", "0", "0")
                arcpy.Append_management(DataCleanTemp + "\\ConsWithParFid.shp", Data_Location + "\\Construction",
                                        "NO_TEST")
    except Exception as e:
        print("Failed to write to exception file: {}".format(e))

    print("process complete")
    tkMessageBox.showinfo(title="Merge DUmmy Parcels Saex Mdb files " , message="Done")
