from Tkinter import *

version = "v1.0.1"

class App(Frame):
    global version

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create buttons that do nothing"""

        # create label for sheet
        self.Sheet = Label(self, text="Enter path to the main folder", width=30)
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.compactDB, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
        Input: Folder path
        
        Process:Input the folder location 
        Output: Append Ward Boundary.
        
        For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def compactDB(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        import time
        Folder_Location = "d:\\"
        startTime = time.time ()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_boundary.csv","a")
        blank_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb"
        out_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\test_out.mdb"
        if (arcpy.Exists(out_data)):
            arcpy.Delete_management(out_data)
        arcpy.Copy_management(blank_data, out_data)
        count = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)

        DataCleanTemp = Folder_Location + "\\DataCleanTemp"
        if (os.path.exists(DataCleanTemp)):  # delete folder if exits, otherwise it causes error
            arcpy.Delete_management(DataCleanTemp, "Folder")
        if (arcpy.Exists("selection_parcel")):
            arcpy.Delete_management("selection_parcel")

        for i in mdb_list:
            Input_Parcel_Layer = i+"\\Parcel"
            Input_Segments_Layer = i + "\\Segments"
            arcpy.CreateFolder_management(Folder_Location, "DataCleanTemp")
            DataCleanTemp = Folder_Location + "\\DataCleanTemp"
            arcpy.env.workspace = DataCleanTemp
            arcpy.env.overwriteOutput = True

            Parcel_Dissolve = DataCleanTemp+"\\Parcel_Dissolve.shp"
            Line_shp = out_data+"\\Segments"
            Line_shp_1 = DataCleanTemp+"\\Segments.shp"
            Segments__3_ = Line_shp

            # Process: Dissolve
            arcpy.Dissolve_management(Input_Parcel_Layer, Parcel_Dissolve, "", "", "MULTI_PART", "DISSOLVE_LINES")

            # Process: Polygon To Line
            arcpy.PolygonToLine_management(Parcel_Dissolve, Line_shp_1, "IDENTIFY_NEIGHBORS")
            arcpy.Append_management(Line_shp_1, Line_shp, "NO_TEST", "", "")
            arcpy.CalculateField_management(Line_shp, "MBoundTy", 10, "PYTHON")

            # Process: Append
            arcpy.Append_management(Line_shp, Input_Segments_Layer, "NO_TEST", "", "")
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print("Ward Boundary Append process complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Ward Boundary Append" + version, message="Done")
root = Tk()
root.title("Ward Boundary Append" + version)
myapp = App(root)
myapp.mainloop()
