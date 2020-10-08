from Tkinter import *
from tkMessageBox import showerror

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self,master)
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
        self.button4=Button(self, text="Process", command=self.parcelIDcreator, width=30)
        self.button4.grid(row=1, column=1, sticky=E+W+N+S)

    def parcelIDcreator (self):   
        import tkMessageBox
        import arcpy
        import glob
        import os
        import shutil
        from arcpy import env
        path = self.sheetentry1.get()
        #print(path)
        if os.path.exists(path+"\\"+path.split("\\")[-1]+"_merged.mdb"):
            os.remove(path+"\\"+path.split("\\")[-1]+"_merged.mdb")
            print("old merged file deleted")
        # mdb_list = glob.glob(path+"\**\*.mdb")
        # mdb_list.extend(glob.glob(path+"\*.mdb"))

        mdb_list = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
        
        print(mdb_list)
        # merged = "D:\\LIS_SYSTEM\\LIS_Spatial_Data\\merged.mdb"

        # copy first file
        try:
            # shutil.copy(r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\BLANK84.mdb', path+"\\"+path.split("\\")[-1]+"_merged.mdb")
            print("D:\\LIS_SYSTEM\\LIS_Spatial_Templates\\BLANK84.mdb copied as "+path.split("\\")[-1]+"_merged.mdb")
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", sys.exc_info())

        for i in mdb_list:
            import arcpy
            import os

            # Local variables:
            Folder_Location = "d:\\"
            # Data_Location = raw_input('location of mdb')
            # Data_Location = 'D:\\Gdrive\\dosamritkarma\\CAS\\DataCleanUpScripts\\Dadapauwa_2ka1.mdb'
            Data_Location = i
            if (os.path.exists("D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb")):
                BLANK84_Template = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb"
            else:
                print("Blank Template database not found, install saex")
                exit()

            # Process: Create Temp Folder to strore all processing intermediaries
            arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            arcpy.env.workspace = DataCleanTemp

            # Process: Feature Class to Feature Class
            arcpy.FeatureClassToFeatureClass_conversion(Data_Location + "\\Parcel", DataCleanTemp, "Parcel1.shp")
            arcpy.Delete_management(Data_Location + "\\Parcel")

            # Process: Copy Features
            arcpy.CopyFeatures_management(BLANK84_Template + "\\Parcel", Data_Location + "\\Parcel", "", "0", "0", "0")

            # Process: Feature Class To Coverage
            cov1 = DataCleanTemp + "\\cov1"
            arcpy.FeatureclassToCoverage_conversion(DataCleanTemp + "\\Parcel1.shp REGION", cov1, "0.005 Meters",
                                                    "DOUBLE")

            # Process: Copy Features
            arcpy.CopyFeatures_management(DataCleanTemp + "\\cov1\\polygon", DataCleanTemp + "\\CleanPoly.shp", "", "0",
                                          "0", "0")

            # Process: Spatial Join
            arcpy.SpatialJoin_analysis(DataCleanTemp + "\\CleanPoly.shp", DataCleanTemp + "\\Parcel1.shp",
                                       DataCleanTemp + "\\NewJoinedData.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL")

            # Process: Append
            arcpy.Append_management(DataCleanTemp + "\\NewJoinedData.shp", Data_Location + "\\Parcel", "NO_TEST")

            # Process: Add Field (3)
            arcpy.AddField_management(Data_Location + "\\Parcel", "Ids", "LONG", "", "", "", "", "NULLABLE",
                                      "NON_REQUIRED", "")

            # Process: Calculate Field (3)
            arcpy.CalculateField_management(Data_Location + "\\Parcel", "IDS", "[OBJECTID]", "VB", "")

            ## parfid in segments
            # Process: Spatial Join
            arcpy.SpatialJoin_analysis(Data_Location + "\\Segments", Data_Location + "\\Parcel",
                                       DataCleanTemp + "\\SegWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       "SegNo \"SegNo\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Segments,SegNo,-1,-1;Boundty \"Boundty\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Segments,Boundty,-1,-1;ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#," + Data_Location + "\\Segments,ParFID,-1,-1;MBoundTy \"MBoundTy\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Segments,MBoundTy,-1,-1;ABoundTy \"ABoundTy\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Segments,ABoundTy,-1,-1;Shape_Leng \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + Data_Location + "\\Segments,Shape_Length,-1,-1;MarginName \"MarginName\" true true false 50 Text 0 0 ,First,#," + Data_Location + "\\Segments,MarginName,-1,-1;Ids \"Ids\" true true false 0 Long 0 0 ,First,#," + Data_Location + "\\Parcel,Ids,-1,-1",
                                       "INTERSECT", "", "")

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
            arcpy.SpatialJoin_analysis(Data_Location + "\\Construction", Data_Location + "\\Parcel",
                                       DataCleanTemp + "\\ConsWithParFid.shp", "JOIN_ONE_TO_ONE", "KEEP_ALL",
                                       "ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#," + Data_Location + "\\Construction,ParFID,-1,-1;ConsTy \"ConsTy\" true true false 2 Short 0 0 ,First,#," + Data_Location + "\\Construction,ConsTy,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + Data_Location + "\\Construction,Shape_Length,-1,-1;ids \"ids\" true true false 0 Long 0 0 ,First,#," + Data_Location + "\\Parcel,ids,-1,-1",
                                       "INTERSECT", "", "")

            # Process: Calculate Field (2)
            arcpy.CalculateField_management(DataCleanTemp + "\\ConsWithParFid.shp", "ParFID", "[ids]", "VB", "")

            arcpy.Delete_management(Data_Location + "\\Construction")
            arcpy.CopyFeatures_management(BLANK84_Template + "\\Construction", Data_Location + "\\Construction", "",
                                          "0", "0", "0")
            arcpy.Append_management(DataCleanTemp + "\\ConsWithParFid.shp", Data_Location + "\\Construction", "NO_TEST")

            ## remove processing folder
            # Process: Delete
            arcpy.Delete_management(DataCleanTemp, "Folder")
            print(Data_Location + " cleaning process complete")
        print("process complete")
        tkMessageBox.showinfo(title="Clean Saex Mdb files", message="Done")
            
root = Tk()
root.title("Clean Saex Mdb files")
myapp = App(root)
myapp.mainloop()




