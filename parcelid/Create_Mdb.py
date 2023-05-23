from Tkinter import *

version = "v1.0.0"

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
        self.Sheet = Label(self, text="Enter path to the folder containing "+"\n"+
                                      "Parcel Segment and Const", width=30)
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Choose Central Meridian", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "Blank87.mdb",
            "Blank84.mdb",
            "Blank81.mdb"
        ]

        self.variable = StringVar(self)
        self.variable.set(options[1]) #default value
        self.optionmenu = OptionMenu(self, self.variable, *options)
        self.optionmenu.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.compactDB, width=30)
        self.button4.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=3, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process:Input the folder location 
Output: Compacted Database.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def compactDB(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        import time
        startTime = time.time ()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_create_mdb.csv","a")
        count = 0
        # parcel = path+"\\parcel.shp"
        # construction = path+"\\construction.shp"
        # segments = path+"\\segments.shp"
        arcpy.env.workspace = path
        feature_lists = arcpy.ListFeatureClasses()

        for fc in feature_lists:
            print (fc+"   \n")


        option_choosed = self.variable.get()
        blank_data = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\parcel_id\\" + option_choosed
        out_data = "D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\\test.mdb"

        if(arcpy.Exists(out_data)):
            arcpy.Delete_management(out_data)
        arcpy.Copy_management(blank_data, out_data)

        for features in feature_lists:
            if("parcel" in features):
                arcpy.Append_management(features, out_data + "\\Parcel", "NO_TEST")
                continue

            elif("construction" in features):
                arcpy.Append_management(features, out_data + "\\Construction", "NO_TEST")
                continue

            elif("segments" in features):
                arcpy.Append_management(features, out_data + "\\Segments", "NO_TEST")
                continue
            else:
                print(features + " Layer not found for, " + path)
                continue


        arcpy.env.workspace = path
        arcpy.Copy_management(out_data, path+"\\new.mdb")
        arcpy.Delete_management(out_data)

        print(" Creating mdb process complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Create MDB" + version, message="Done")
root = Tk()
root.title("Create MDB " + version)
myapp = App(root)
myapp.mainloop()
