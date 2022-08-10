# -*- coding: utf-8 -*-
from Tkinter import *

version = "v2.1.8"

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

        self.Sheet = Label(self, text="Choose Central Meridian", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "Blank_87.mdb",
            "Blank_84.mdb",
            "Blank_81.mdb"
        ]

        self.variable = StringVar(self)
        self.variable.set(options[1]) #default value
        self.optionmenu = OptionMenu(self, self.variable, *options)
        self.optionmenu.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        #create calculate button
        self.button4=Button(self, text="Process", command=self.fixGapsAndOverlaps, width=30)
        self.button4.grid(row=2, column=1, sticky=E+W+N+S)

        self.Sheet = Label (self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid (row=3, column=0, padx=5, pady=5, sticky=E + W + N + S)

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
        reload(sys)
        sys.setdefaultencoding('utf-8')

        exception_list= open(path+"\\exception_list_gap_overlap.csv","a")
        exception_list.truncate(0)
        mdb_list = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))

        total_mdbs = len(mdb_list)
        count = 1
        import time

        startTime = time.time()

        for i in mdb_list:

            try:
                parcel_list = arcpy.GetCount_management(i + "\\Cadastre\\Parcel")
                no_of_attribute = int(parcel_list.getOutput(0))
                print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
                if (no_of_attribute == 0):
                    exception_list.write("Parcel layer has 0 Features for ," + i + "\n")
                    count += 1
                else:
                    # Local variables:
                    Folder_Location = "d:\\"
                    Data_Location = i
                    option_choosed = self.variable.get()
                    blank_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\" + option_choosed



                    if (os.path.exists(blank_data)):
                        BLANK84_Template = blank_data
                    else:
                        print("Blank Template database not found, install PE")
                        exit()

                    # Process: Create Temp Folder to strore all processing intermediaries
                    DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                    if (os.path.exists(DataCleanTemp)):  # delete folder if exits, otherwise it causes error
                        arcpy.Delete_management(DataCleanTemp, "Folder")
                    if (arcpy.Exists("selection_parcel")):
                        arcpy.Delete_management("selection_parcel")
                    arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
                    DataCleanTemp = Folder_Location + "\\DataCleanTemp"
                    test_data = DataCleanTemp+"\\test.mdb"
                    arcpy.Copy_management(BLANK84_Template, test_data)

                    arcpy.env.workspace = i
                    arcpy.env.overwriteOutput = True
                    count += 1

                    cadastre_dataset=os.path.join(i,"Cadastre")
                    construction_line_location=os.path.join(i,"Cadastre\\Construction_Line")
                    building_location=os.path.join(i,"Cadastre\\Building")
                    construction_polygon_location=os.path.join(i,"Cadastre\\Construction_Polygon")
                    parcel_location=os.path.join(i,"Cadastre\\Parcel")


                    Cadastre_Topology=os.path.join(i,"Cadastre\\Cadastre_Topology")
                    print i
                    print parcel_location


                    if (arcpy.Exists(Cadastre_Topology)):
                        # arcpy.management.RemoveFeatureClassFromTopology(Cadastre_Topology, "Parcel")
                        # arcpy.management.RemoveFeatureClassFromTopology(Cadastre_Topology, "Building")
                        # arcpy.management.RemoveFeatureClassFromTopology(Cadastre_Topology, "Construction_Line")
                        # arcpy.management.RemoveFeatureClassFromTopology(Cadastre_Topology, "Construction_Polygon")
                        arcpy.Delete_management(Cadastre_Topology)
                        arcpy.CreateTopology_management(cadastre_dataset,"Cadastre_Topology",0.00000001)
                    else:
                        print ("Create Topology layer")
                        arcpy.CreateTopology_management(cadastre_dataset,"Cadastre_Topology",0.00000001)

                    arcpy.FeatureClassToFeatureClass_conversion(Data_Location+"\\Cadastre\\Parcel", test_data+"\\Cadastre",
                                                                "Parcel2","", "Region \"अञ्चल\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Region,-1,-1;DistrictCode \"जिल्ला_कोड\" true true false 2 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,DistrictCode,-1,-1;District \"जिल्ला\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,District,-1,-1;VDCCode \"गाविस_कोड\" true true false 6 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,VDCCode,-1,-1;VDC \"गाविस\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,VDC,-1,-1;Ward \"वार्ड\" true true false 2 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Ward,-1,-1;MapSheetNumber \"नक्सा_सिट_नम्बर\" true true false 10 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,MapSheetNumber,-1,-1;ParcelNo \"जमिनको_कित्ता_नम्बर\" true true false 6 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelNo,-1,-1;ParcelNoEng \"ParcelNoEng\" true true false 4 Long 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelNoEng,-1,-1;ParcelKey \"कित्ता_संकेत_नम्बर\" true true false 26 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelKey,-1,-1;OwnerId \"जग्गाधनी_संकेत_नम्बर\" true true false 30 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,OwnerId,-1,-1;Tenant_id \"मोहीको_संकेत_नम्बर\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Tenant_id,-1,-1;ParcelClass \"किसिम\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelClass,-1,-1;ParcelType \"विरह\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelType,-1,-1;ParcelRegionClass \"जग्गाको_क्षेत्रीय_किसिम\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelRegionClass,-1,-1;ParcelClassValue \"किसिम_मान\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,ParcelClassValue,-1,-1;Proof \"प्रमाण_संकेत\" true true false 255 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Proof,-1,-1;Kaifiyet \"कैफियत\" true true false 255 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Kaifiyet,-1,-1;Registered \"दर्ता_भए_नभएको\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Registered,-1,-1;EastParcelNo \"पूर्व_कित्ता_नम्बर\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,EastParcelNo,-1,-1;WestParcelNo \"पश्चिम_कित्ता_नम्बर\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,WestParcelNo,-1,-1;NorthParcelNo \"उत्तर_कित्ता_नम्बर\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,NorthParcelNo,-1,-1;SouthParcelNo \"दक्षिण_कित्ता_नम्बर\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,SouthParcelNo,-1,-1;DateOfSurvey \"नापी_भएको_मिति\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,DateOfSurvey,-1,-1;User_ID \"कर्मचारी_संकेत_नम्बर\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,User_ID,-1,-1;RegisteredName \"दर्ता_गर्नेको_नाम\" true true false 255 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,RegisteredName,-1,-1;RegisteredDate \"दर्ता_भएको_मिति\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,RegisteredDate,-1,-1;SurveyTeamNo \"नापी_टोली_नम्बर\" true true false 4 Long 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,SurveyTeamNo,-1,-1;SurveyOfficeName \"नापी_कार्यालय\" true true false 50 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,SurveyOfficeName,-1,-1;LandPrice \"जग्गाको_मुल्य\" true true false 8 Double 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,LandPrice,-1,-1;SqFeet \"बर्गफिट\" true true false 8 Double 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,SqFeet,-1,-1;Bigha \"बिघा\" true true false 255 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Bigha,-1,-1;Ropani \"रोपनी\" true true false 255 Text 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,Ropani,-1,-1;SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,SHAPE_Length,-1,-1;SHAPE_Area \"SHAPE_Area\" false true true 8 Double 0 0 ,First,#,"
                                                                               + Data_Location + "\\Cadastre\\Parcel,SHAPE_Area,-1,-1", "")

                    # arcpy.EliminatePolygonPart_management(DataCleanTemp + "\\Parcel.shp", DataCleanTemp + "\\Parcel1.shp", "AREA", "0.005 SquareMeters", "0", "ANY")

                    # Repair Parcel Geometry
                    arcpy.RepairGeometry_management(test_data + "\\Cadastre\\Parcel2")

                    # Process: Feature To Point
                    arcpy.FeatureToPoint_management(test_data + "\\Cadastre\\Parcel2",
                                                    test_data + "\\Cadastre\\ParcelCentroid",
                                                    "INSIDE")


                    arcpy.Delete_management(parcel_location)


                    # Process: Copy Features
                    arcpy.CopyFeatures_management(BLANK84_Template + "\\Cadastre\\Parcel",
                                                  parcel_location, "", "0", "0",
                                                  "0")

                    # Process: Feature Class To Coverage
                    cov1 = DataCleanTemp + "\\cov1"
                    arcpy.FeatureclassToCoverage_conversion(test_data + "\\Cadastre\\Parcel2 REGION", cov1,"0.008 Meters","DOUBLE")

                    # Process: Copy Features
                    arcpy.CopyFeatures_management(cov1 + "\\polygon", test_data + "\\Cadastre\\CleanPoly", "",
                                                  "0",
                                                  "0", "0")

                    # Process: Spatial Join
                    arcpy.SpatialJoin_analysis(test_data + "\\Cadastre\\CleanPoly",
                                               test_data + "\\Cadastre\\ParcelCentroid",
                                               test_data + "\\Cadastre\\NewJoinedData", "JOIN_ONE_TO_ONE", "KEEP_ALL")

                    arcpy.MakeFeatureLayer_management(test_data + "\\Cadastre\\NewJoinedData", "selection_parcel")

                    arcpy.SelectLayerByAttribute_management("selection_parcel", "NEW_SELECTION", "[SHAPE_Area]<0.05")
                    arcpy.Eliminate_management("selection_parcel", test_data + "\\Cadastre\\Parcel1", "LENGTH")
                    arcpy.SelectLayerByAttribute_management("selection_parcel", "CLEAR_SELECTION")
                    if (arcpy.Exists("selection_parcel")):
                        arcpy.Delete_management("selection_parcel")

                    # Process: Append
                    arcpy.Append_management(test_data + "\\Cadastre\\Parcel1", parcel_location,
                                            "NO_TEST")

                    #Add Field for ParFID Later
                    arcpy.AddField_management(parcel_location, "Ids", "LONG", "", "", "", "", "NULLABLE",
                                              "NON_REQUIRED", "")
                    arcpy.CalculateField_management(parcel_location, "IDS", "[OBJECTID]", "VB", "")

                    ###########Construction_Polygon Intersect Parcels

                    arcpy.Intersect_analysis([construction_polygon_location, parcel_location],test_data + "\\Cadastre\\Const_Poly_ParcelIntersect", "", "0.00001", "INPUT")

                    if (arcpy.Exists("selection_const")):
                        arcpy.Delete_management("selection_const")

                    const_parcel_intersect = test_data + "\\Cadastre\\Const_Poly_ParcelIntersect"
                    arcpy.MakeFeatureLayer_management(const_parcel_intersect, "selection_const")
                    arcpy.SelectLayerByAttribute_management("selection_const", "NEW_SELECTION", "[SHAPE_Area]<0.05")
                    arcpy.management.DeleteFeatures("selection_const")



                    arcpy.AddField_management(test_data+"\\Cadastre\\Const_Poly_ParcelIntersect","ParFID","LONG")

                    arcpy.SpatialJoin_analysis(test_data + "\\Cadastre\\Const_Poly_ParcelIntersect",
                                               parcel_location,
                                               test_data+"\\Cadastre\\Const_Poly_WithParFID","JOIN_ONE_TO_ONE","KEEP_ALL")

                    # Process: Calculate Field (2)
                    arcpy.CalculateField_management(test_data+"\\Cadastre\\Const_Poly_WithParFID", "ParFID", "[ids]", "VB", "")

                    # Process: Delete Features
                    arcpy.Delete_management(construction_polygon_location)
                    arcpy.CopyFeatures_management(BLANK84_Template + "\\Cadastre\\Construction_Polygon", construction_polygon_location, "", "0","0","0")
                    # Process: Append
                    arcpy.Append_management(test_data + "\\Cadastre\\Const_Poly_WithParFID", construction_polygon_location, "NO_TEST")

                    ###########Construction_Polygon Intersect Parcels

                    arcpy.Intersect_analysis([construction_line_location, parcel_location],test_data + "\\Cadastre\\Const_Line_ParcelIntersect", "", "0.00005", "INPUT")
                    arcpy.AddField_management(test_data+"\\Cadastre\\Const_Line_ParcelIntersect","ParFID","LONG")

                    arcpy.SpatialJoin_analysis(test_data + "\\Cadastre\\Const_Line_ParcelIntersect",
                                               parcel_location,
                                               test_data+"\\Cadastre\\Const_Line_WithParFID","JOIN_ONE_TO_ONE","KEEP_ALL")

                    # Process: Calculate Field (2)
                    arcpy.CalculateField_management(test_data+"\\Cadastre\\Const_Line_WithParFID", "ParFID", "[ids]", "VB", "")

                    # Process: Delete Features
                    arcpy.Delete_management(construction_line_location)
                    arcpy.CopyFeatures_management(BLANK84_Template + "\\Cadastre\\Construction_Line", construction_line_location, "", "0","0","0")
                    # Process: Append
                    arcpy.Append_management(test_data + "\\Cadastre\\Const_Line_WithParFID", construction_line_location, "NO_TEST")

                    ##########Building Intersect Parcels
                    arcpy.Intersect_analysis([building_location, parcel_location],test_data + "\\Cadastre\\BuildingParcelIntersect", "", "", "INPUT")

                    if (arcpy.Exists("selection_build")):
                        arcpy.Delete_management("selection_build")

                    building_parcel_intersect = test_data + "\\Cadastre\\BuildingParcelIntersect"
                    arcpy.MakeFeatureLayer_management(building_parcel_intersect, "selection_build")
                    arcpy.SelectLayerByAttribute_management("selection_build", "NEW_SELECTION", "[SHAPE_Area]<0.05")
                    arcpy.management.DeleteFeatures("selection_build")

                    arcpy.AddField_management(test_data+"\\Cadastre\\BuildingParcelIntersect","ParFID","LONG")

                    arcpy.SpatialJoin_analysis(test_data + "\\Cadastre\\BuildingParcelIntersect",
                                               parcel_location,
                                               test_data+"\\Cadastre\\Building_WithParFID","JOIN_ONE_TO_ONE","KEEP_ALL")

                    # Process: Calculate Field (2)
                    arcpy.CalculateField_management(test_data+"\\Cadastre\\Building_WithParFID", "ParFID", "[ids]", "VB", "")

                    # Process: Delete Features
                    arcpy.Delete_management(building_location)
                    arcpy.CopyFeatures_management(BLANK84_Template + "\\Cadastre\\Building", building_location, "", "0","0","0")
                    # Process: Append
                    arcpy.Append_management(test_data + "\\Cadastre\\Building_WithParFID", building_location, "NO_TEST")



                    arcpy.Delete_management(DataCleanTemp, "Folder")

                    # try:
                    #     arcpy.CalculateField_management(parcel_location, "PARCELKEY",
                    #                                     "str(!GRIDS1!).ljust(9,'a') + str( !PARCELNO!).zfill(6) + str( !DISTRICT!).zfill(2) + str( !VDC! ).zfill(4) + str( !WARDNO!).zfill(2)",
                    #                                     "PYTHON_9.3", "")
                    # except:
                    #     exception_list.write("ParcelKey Error for ," + i + "\n")

                    # Add Fields
                    arcpy.AddField_management(parcel_location, "circularity", "FLOAT")
                    arcpy.AddField_management(parcel_location, "suspicious", "TEXT", field_length=5)

                    # Calculate Circularity
                    arcpy.CalculateField_management(parcel_location, "circularity",
                                                    "4 * math.pi * !SHAPE_Area!  / !SHAPE_Length!**2", "PYTHON")

                    # Calculate Suspicious
                    expression = "check(!Shape_Area!,!circularity!)"

                    codeblock = """def check(Shape_Area,circularity):
                                        if(Shape_Area < 5 and circularity < 0.2):
                                            return 'yes'
                                        else:
                                            return 'no'
                                            """
                    arcpy.CalculateField_management(parcel_location, "suspicious", expression,
                                                    "PYTHON",
                                                    codeblock)

                    #Topology
                    arcpy.AddFeatureClassToTopology_management(Cadastre_Topology, parcel_location)
                    arcpy.AddFeatureClassToTopology_management(Cadastre_Topology, construction_line_location)
                    arcpy.AddFeatureClassToTopology_management(Cadastre_Topology, construction_polygon_location)
                    arcpy.AddFeatureClassToTopology_management(Cadastre_Topology, building_location)

                    #Topology Rules
                    arcpy.AddRuleToTopology_management(Cadastre_Topology,"Must Not Overlap (Area)",parcel_location)
                    arcpy.AddRuleToTopology_management(Cadastre_Topology,"Must Not Have Gaps (Area)",parcel_location)
                    arcpy.AddRuleToTopology_management(Cadastre_Topology,"Must Be Covered By (Area-Area)",building_location,"",parcel_location)
                    arcpy.AddRuleToTopology_management(Cadastre_Topology,"Must Be Covered By Boundary Of (Line-Area)",construction_line_location,"",parcel_location)
                    arcpy.AddRuleToTopology_management(Cadastre_Topology,"Must Be Covered By (Area-Area)",construction_polygon_location,"",parcel_location)

                    #VAlidate Topology
                    arcpy.ValidateTopology_management(Cadastre_Topology)

                    arcpy.Compact_management(Data_Location)
                    print(Data_Location + " cleaning process complete")
            except Exception as e:
                exception_list.write("Gap Overlap Error for ," + i + "\n")
                print ("error = "+str(e))
            except SystemExit as x:
                print ("error = "+str(x))

        print ('The script took {0} second !'.format(time.time() - startTime))
        print("process complete")
        tkMessageBox.showinfo(title="Clean Saex Mdb files " + version, message="Done")

root = Tk()
root.title("Clean Saex Mdb files " + version)
myapp = App(root)
myapp.mainloop()




