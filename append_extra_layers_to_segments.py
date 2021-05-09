from Tkinter import *

version = "v1.0.0"


class App (Frame):
    global version

    def __init__(self, master):
        Frame.__init__ (self, master)
        self.pack ()

        self.grid ()
        self.create_widgets ()

    def create_widgets(self):
        """Create buttons that do nothing"""

        # create label for sheet
        self.Sheet = Label (self, text="Enter path to the main folder", width=30)
        self.Sheet.grid (row=0, column=0, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry (self, width=30)
        self.sheetentry1.grid (row=0, column=1, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button (self, text="Process", command=self.append_extra_layers_to_segments, width=30)
        self.button4.grid (row=1, column=1, sticky=E + W + N + S)

        self.Sheet = Label (self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid (row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n 
        """
        self.Sheet = Label (self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid (row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def append_extra_layers_to_segments(self):
        import tkMessageBox
        import arcpy
        import glob
        import os
        import shutil
        from arcpy import env
        path = self.sheetentry1.get ()
        # print(path)
        exception_list = open (path + "\\exception_list_append_extra_layers_to_segments.csv", "a")

        mdb_list = []
        for root, dirnames, filenames in os.walk (path):
            for filename in filenames:
                if filename.endswith ('.mdb'):
                    mdb_list.append (os.path.join (root, filename))

        # print(mdb_list)
        total_mdbs = len (mdb_list)

        # Local variables:
        Folder_Location = "d:\\"
        # Data_Location = raw_input('location of mdb')
        # Data_Location = 'D:\SATUNGAL\Santungal_1Ka\Santungal_1Ka.mdb'
        if (os.path.exists ("D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb")):
            BLANK84_Template = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb"
        else:
            print("Blank Template database not found, install saex")
            exit ()
        # Process: Create Temp Folder to strore all processing intermediaries
        DataCleanTemp = Folder_Location + "\\DataCleanTemp"
        if (os.path.exists (DataCleanTemp)):  # delete folder if exits, otherwise it causes error
            arcpy.Delete_management (DataCleanTemp, "Folder")
        if (arcpy.Exists ("selection_parcel")):
            arcpy.Delete_management ("selection_parcel")
        arcpy.CreateFolder_management (Folder_Location, "DataCleanTemp")
        DataCleanTemp = Folder_Location + "\\DataCleanTemp"
        arcpy.env.workspace = DataCleanTemp
        arcpy.env.overwriteOutput = True
        # start geoprocess
        extra_layers = ["foottrack"] # list of layers to be appended to segments
        count = 0
        for i in mdb_list:
            env.workspace = i
            count += 1
            print (env.workspace + " (" + str (count) + "/" + str (total_mdbs) + ")")
            Data_Location = i
            for l in extra_layers:
                try:
                    # Process: Add Field
                    arcpy.AddField_management (Data_Location + "\\" + l, "Boundty", "SHORT", "", "", "", "", "NULLABLE",
                                               "NON_REQUIRED", "")

                    # Process: Calculate Field
                    arcpy.CalculateField_management (Data_Location + "\\" + l, "Boundty", "Fix ( 1 )", "VB", "")

                    # Process: Merge
                    arcpy.Merge_management (
                        Data_Location + "\\" + l + ";" + Data_Location + "\\Segments", Data_Location + "\\Track_Seg",
                        "SHAPE_Length \"SHAPE_Length\" false true true 8 Double 0 0 ,First,#,"+Data_Location + "\\" + l +",SHAPE_Length,-1,-1,"+Data_Location + "\\Segments,Shape_Length,-1,-1;Boundty \"Boundty\" true true false 2 Short 0 0 ,First,#,"+Data_Location + "\\" + l +",Boundty,-1,-1,"+Data_Location + "\\Segments,Boundty,-1,-1;SegNo \"SegNo\" true true false 2 Short 0 0 ,First,#,"+Data_Location + "\\Segments,SegNo,-1,-1;ParFID \"ParFID\" true true false 4 Long 0 0 ,First,#,"+Data_Location + "\\Segments,ParFID,-1,-1;MBoundTy \"MBoundTy\" true true false 2 Short 0 0 ,First,#,"+Data_Location + "\\Segments,MBoundTy,-1,-1;ABoundTy \"ABoundTy\" true true false 2 Short 0 0 ,First,#,"+Data_Location + "\\Segments,ABoundTy,-1,-1")

                    # Process: Intersect
                    arcpy.Intersect_analysis (
                        [Data_Location + "\\Track_Seg", Data_Location + "\\Parcel"],
                        Data_Location + "\\Segments1", "", "", "line")

                    # Process: Calculate Field (2)
                    arcpy.CalculateField_management (Data_Location + "\\Segments1", "ParFID", "[FID_Parcel]", "VB", "")

                    # Process: Delete Field
                    arcpy.DeleteField_management (Data_Location + "\\Segments1","FID_Track_Seg;FID_Parcel;PARCELKEY;PARCELNO;DISTRICT;VDC;WARDNO;GRIDS1;PARCELTY;ParcelNote;circularity;suspicious")

                    # print(merged + l)
                    # arcpy.Merge_management(l, merged)
                except:
                    exception_list.write ("append_extra_layers_to_segments Error for ," + i + "\n")
        print("process complete")
        tkMessageBox.showinfo (title="append_extra_layers_to_segments " + version, message="Done")


root = Tk ()
root.title ("append_extra_layers_to_segments " + version)
myapp = App (root)
myapp.mainloop ()




