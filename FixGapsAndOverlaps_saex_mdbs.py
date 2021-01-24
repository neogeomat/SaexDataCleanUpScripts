from Tkinter import *

version = "v2.1.3"

class App(Frame):
    global version
    def __init__(self, master):
        Frame.__init__(self ,master)
        self.pack()
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create buttons that do nothing"""

        #create label for sheet
        self.Sheet=Label(self, text="Enter path to the main folder",width=30)
        self.Sheet.grid(row=0, column=0,sticky=E+W+N+S)

        #create entry.
        self.sheetentry1= Entry(self,width=30)
        self.sheetentry1.grid(row=0, column =1, sticky=E+W+N+S)

        #create calculate button
        self.button4=Button(self, text="Process", command=self.fixGapsAndOverlaps, width=30)
        self.button4.grid(row=1, column=1, sticky=E+W+N+S)

        self.Sheet = Label (self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid (row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n Removes gaps and overlaps in parcel layer of mdb files. Circularuty and suspiciousness of the cleaned features ae calculated. This is to detect sliver polygons which needs to be merged to adjacent parcels. The segments and construction layer are populated with the corresponding parcelid. The mdb is compacted (compressed) to reduce file size.

Requires arcpy (available through arcgis 10.x) and saex. Python executable must be from the arcgis installation.

Input: Folder path

Process: This scripts loops though each mdb file in the path recursively and fixes any gaps or overlaps in the parcel layer. BLANK84 template is used in processing so the final output is in this template. D:\\DataCleanTemp is created as temporary workspace and deleted at the end. If due to error this folder is not deleted, then it may have to be deleted manually.

Output: mdbs in the folder do not have gaps or overlap in parcel layer. The mdbs then need to be processed for sliver polygons.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts
        """
        self.Sheet = Label (self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid (row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def fixGapsAndOverlaps (self):
        import tkMessageBox
        import arcpy
        import os
        # from arcpy import env
        path = self.sheetentry1.get()
        #print(path)
        # if os.path.exists(path+"\\"+path.split("\\")[-1]+"_merged.mdb"):
        #     os.remove(path+"\\"+path.split("\\")[-1]+"_merged.mdb")
        #     print("old merged file deleted")
        # # mdb_list = glob.glob(path+"\**\*.mdb")
        # mdb_list.extend(glob.glob(path+"\*.mdb"))

        exception_list= open(path+"\\exception_list_gap_overlap.csv","a")

        mdb_list = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))

        # print(mdb_list)
        total_mdbs = len(mdb_list)
        # merged = "D:\\LIS_SYSTEM\\LIS_Spatial_Data\\merged.mdb"
        count = 0
        import time

        startTime = time.time()

        for i in mdb_list:
            # import arcpy
            # import os

            # Local variables:
            Folder_Location = "d:\\"
            # Data_Location = raw_input('location of mdb')
            # Data_Location = 'D:\SATUNGAL\Santungal_1Ka\Santungal_1Ka.mdb'
            Data_Location = i
            if (os.path.exists ("D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb")):
                BLANK84_Template = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb"
            else:
                print("Blank Template database not found, install saex")
                exit ()

            # Process: Create Temp Folder to strore all processing intermediaries
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            try:
                if (os.path.exists(DataCleanTemp)): # delete folder if exits, otherwise it causes error
                    arcpy.Delete_management(DataCleanTemp, "Folder")
                arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
                DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                arcpy.env.workspace = DataCleanTemp
                count += 1
                print (Data_Location + " (" + str (count) + "/" + str (total_mdbs) + ")")

                arcpy.FeatureClassToFeatureClass_conversion(Data_Location + "\\Parcel", DataCleanTemp, "Parcel.shp", "", "PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#,"
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

                arcpy.MakeFeatureLayer_management(DataCleanTemp + "\\Parcel.shp", "selection_parcel")
                arcpy.SelectLayerByAttribute_management("selection_parcel","NEW_SELECTION",'"Shape_Area"<0.05')
                arcpy.Eliminate_management("selection_parcel",DataCleanTemp + "\\Parcel1.shp","AREA")
                arcpy.SelectLayerByAttribute_management("selection_parcel","CLEAR_SELECTION")
                #arcpy.EliminatePolygonPart_management(DataCleanTemp + "\\Parcel.shp", DataCleanTemp + "\\Parcel1.shp", "AREA", "0.005 SquareMeters", "0", "ANY")

                # Process: Feature To Point
                arcpy.FeatureToPoint_management(DataCleanTemp + "\\Parcel1.shp", DataCleanTemp + "\\ParcelCentroid.shp", "INSIDE")
                arcpy.Delete_management(Data_Location + "\\Parcel")

                # Process: Copy Features
                arcpy.CopyFeatures_management(BLANK84_Template + "\\Parcel", Data_Location + "\\Parcel", "", "0", "0", "0")

                # Process: Feature Class To Coverage
                cov1 = DataCleanTemp + "\\cov1"
                arcpy.FeatureclassToCoverage_conversion(DataCleanTemp + "\\Parcel1.shp REGION", cov1, "0.005 Meters", "DOUBLE")

                # Process: Copy Features
                arcpy.CopyFeatures_management(DataCleanTemp + "\\cov1\\polygon", DataCleanTemp + "\\CleanPoly.shp", "", "0", "0", "0")

                # Process: Spatial Join
                arcpy.SpatialJoin_analysis(DataCleanTemp + "\\CleanPoly.shp", DataCleanTemp + "\\ParcelCentroid.shp",
                                           DataCleanTemp + "\\NewJoinedData.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL","AREA \"AREA\" true true false 19 Double 0 0 ,First,#,"
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

                # Process: Append
                arcpy.Append_management(DataCleanTemp + "\\NewJoinedData.shp", Data_Location + "\\Parcel", "NO_TEST")

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
                                           DataCleanTemp + "\\SegWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL","SegNo \"SegNo\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,SegNo,-1,-1;Boundty \"Boundty\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,Boundty,-1,-1;ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,ParFID,-1,-1;MBoundTy \"MBoundTy\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,MBoundTy,-1,-1;ABoundTy \"ABoundTy\" true true false 2 Short 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,ABoundTy,-1,-1;Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,Shape_Length,-1,-1;MarginName \"MarginName\" true true false 50 Text 0 0 ,First,#,"
                                           + Data_Location + "\\Segments,MarginName,-1,-1;Ids \"Ids\" true true false 0 Long 0 0 ,First,#,"
                                           + Data_Location + "\\Parcel,Ids,-1,-1","INTERSECT", "", "")

                # Process: Calculate Field (2)
                arcpy.CalculateField_management(DataCleanTemp + "\\SegWithParFid.shp", "ParFID", "[ids]", "VB", "")

                # Process: Delete Features
                arcpy.Delete_management(Data_Location + "\\Segments")
                arcpy.CopyFeatures_management(BLANK84_Template + "\\Segments", Data_Location + "\\Segments", "", "0", "0",
                                              "0")

                # Process: Append
                arcpy.Append_management(DataCleanTemp + "\\SegWithParFid.shp", Data_Location + "\\Segments", "NO_TEST")

                ## parfid in construction
                # Process: Spatial Join

                arcpy.Intersect_analysis([Data_Location + "\\Construction", Data_Location + "\\Parcel"], DataCleanTemp + "\\ConstructionParcelIntersect.shp", "", "", "")
                arcpy.SpatialJoin_analysis(DataCleanTemp + "\\ConstructionParcelIntersect.shp", Data_Location + "\\Parcel",
                                           DataCleanTemp + "\\ConsWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                           "ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ConstructionParcelIntersect.shp,ParFID,-1,-1;ConsTy \"ConsTy\" true true false 2 Short 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ConstructionParcelIntersect.shp,ConsTy,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"
                                           + DataCleanTemp + "\\ConstructionParcelIntersect.shp,Shape_Length,-1,-1;ids \"ids\" true true false 0 Long 0 0 ,First,#,"
                                           + Data_Location + "\\Parcel,ids,-1,-1","INTERSECT", "", "")

                # Process: Calculate Field (2)
                arcpy.CalculateField_management(DataCleanTemp + "\\ConsWithParFid.shp", "ParFID", "[ids]", "VB", "")

                arcpy.Delete_management(Data_Location + "\\Construction")
                arcpy.CopyFeatures_management(BLANK84_Template + "\\Construction", Data_Location + "\\Construction", "",
                                              "0", "0", "0")
                arcpy.Append_management(DataCleanTemp + "\\ConsWithParFid.shp", Data_Location + "\\Construction", "NO_TEST")

                ## remove processing folder
                # Process: Delete
                arcpy.Delete_management(DataCleanTemp, "Folder")

                ## Finalizing data
                # Process: Delete Field
                arcpy.DeleteField_management(Data_Location + "\\Parcel", "IDS")
                arcpy.CalculateField_management(Data_Location + "\\Parcel", "PARCELKEY","str( !GRIDS1!).ljust(9,'a') + str( !PARCELNO!).zfill(6) + str( !DISTRICT!).zfill(2) + str( !VDC! ).zfill(4) + str( !WARDNO!).zfill(2)","PYTHON_9.3", "")

                # Add Fields
                arcpy.AddField_management (Data_Location + "\\Parcel", "circularity", "FLOAT")
                arcpy.AddField_management (Data_Location + "\\Parcel", "suspicious", "TEXT", field_length=5)

                # Calculate Circularity
                arcpy.CalculateField_management (Data_Location + "\\Parcel", "circularity",
                                                 "4 * math.pi * !SHAPE_Area!  / !SHAPE_Length!**2", "PYTHON")

                # Calculate Suspicious
                expression = "check(!Shape_Area!,!circularity!)"

                codeblock = """def check(Shape_Area,circularity):
                    if(Shape_Area < 5 and circularity < 0.2):
                        return 'yes'
                    else:
                        return 'no'
                        """
                arcpy.CalculateField_management (Data_Location + "\\Parcel", "suspicious", expression, "PYTHON", codeblock)

                arcpy.Compact_management(Data_Location)
                print(Data_Location + " cleaning process complete")
                ## genereate parcel key
            except:
                exception_list.write("Gap Overlap Error for ," + i + "\n")
                print ("error for "+i)
        print ('The script took {0} second !'.format(time.time() - startTime))
        print("process complete")
        tkMessageBox.showinfo(title="Clean Saex Mdb files" + version, message="Done")

root = Tk()
root.title("Clean Saex Mdb files"  + version)
myapp = App(root)
myapp.mainloop()




