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
        self.Sheet = Label(self, text="Enter path to the main folder", width=30)
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.ReCalculateExtentDB, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process:Input the folder location 
Output: Recalculated Extent Database.

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
        exception_list= open(path+"\\exception_list_recalculate_extent.csv","a")
        count = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)

        for i in mdb_list:
            count +=1
            feature_classes = []
            walk = arcpy.da.Walk(i, datatype="FeatureClass")
            for dirpath, dirnames, filenames in walk:
                 for filename in filenames:
                     feature_classes.append(os.path.join(dirpath, filename))
            try:
                for feature in feature_classes:
                    print feature
                    arcpy.RecalculateFeatureClassExtent_management(feature)
            except:
                exception_list.write("Extent ReCalculation Error for ," + i + "\n")
                print("Extent ReCalculation error for "+i)
                print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print("Extent ReCalculation process complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Extent ReCalculation database" + version, message="Done")
root = Tk()
root.title("Recalculate Extent database " + version)
myapp = App(root)
myapp.mainloop()
