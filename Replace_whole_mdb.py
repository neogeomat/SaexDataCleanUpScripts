from Tkinter import *

version = "v1.1.1"

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

        self.Sheet = Label(self, text="Choose Central Meridian", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "Blank.mdb",
            "Blank87.mdb",
            "Blank84.mdb",
            "Blank81.mdb"
        ]

        self.variable = StringVar(self)
        self.variable.set(options[1]) #default value
        self.optionmenu = OptionMenu(self, self.variable, *options)
        self.optionmenu.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)


        # create calculate button
        self.button4 = Button(self, text="Process", command=self.ReCalculateExtentDB, width=30)
        self.button4.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=3, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path
Process:Appends the data to the templete data andthen replaces the data 
Output: Replaced data properties with templete data properties.
For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)


    def ReCalculateExtentDB(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        import time
        arcpy.env.overwriteOutput = True
        startTime = time.time ()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_whole_mdb_replace.csv","a")
        exception_list.truncate(0)
        count = 0

        option_choosed=self.variable.get()
        

        blank_data="D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\"+option_choosed
        print ("option choosed " + blank_data)
        feature_classes = arcpy.ListFeatureClasses(blank_data)
        if feature_classes:
            for fc in feature_classes:
                print(fc)
        else:
            print("No feature classes found in the specified location.")

        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)


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

            except:
                exception_list.write("Replace Whole Mdb Error for ," + i + "\n")
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print("Replace Whole Mdb complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Extent ReCalculation database" + version, message="Done")
root = Tk()
root.title("Replace Mdb databases " + version)
myapp = App(root)
myapp.mainloop()