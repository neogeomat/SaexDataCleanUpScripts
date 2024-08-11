from Tkinter import *
from tkMessageBox import showerror


class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()

        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create buttons that do nothing"""

        # create label for sheet
        self.Sheet = Label(self, text="Enter path to the main folder", width=30)
        self.Sheet.grid(row=0, column=0, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.parcelIDcreator, width=30)
        self.button4.grid(row=1, column=1, sticky=E + W + N + S)

    def parcelIDcreator(self):
        import tkMessageBox
        import arcpy
        import glob
        from arcpy import env
        path = self.sheetentry1.get()
        list = glob.glob(path + "\*.mdb")
        for i in list:
            env.workspace = i

            # Setting input and output
            inFeatures1 = ["Segments", "Parcel"]
            inFeatures2 = ["Construction", "Parcel"]
            intersectOutput1 = "Segments1"
            intersectOutput2 = "Construction1"

            if arcpy.Exists("Segments") and arcpy.Exists("Construction") and arcpy.Exists("Parcel"):
                # overwrite if feature exists
                arcpy.env.overwriteOutput = True
                # Intersect Parcel and segment
                a1 = arcpy.Intersect_analysis(inFeatures1, intersectOutput1, "", "", "line")
                a2 = arcpy.Intersect_analysis(inFeatures2, intersectOutput2, "", "", "")
                # calculating ParFID
                b1 = arcpy.CalculateField_management(intersectOutput1, "ParFID", "!FID_Parcel!", "PYTHON_9.3")
                b2 = arcpy.CalculateField_management(intersectOutput2, "ParFID", "!FID_Parcel!", "PYTHON_9.3")

                # Execute DeleteField
                dropFields1 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote",
                               "FID_Segments", "FID_Parcel"]
                dropFields2 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote",
                               "FID_Construction", "FID_Parcel"]

                arcpy.DeleteField_management(b1, dropFields1)
                arcpy.DeleteField_management(b2, dropFields2)

                # Delete FeatureClass
                arcpy.Delete_management("Segments")
                arcpy.Delete_management("Construction")

                # Rename Feature Class
                arcpy.Rename_management("Segments1", "Segments")
                arcpy.Rename_management("Construction1", "Construction")

            else:
                tkMessageBox.showerror(title="Error", message="Feature Class Missing. Please check")

        tkMessageBox.showinfo(title="Fill parFID", message="Done")


root = Tk()
root.title("Fill parFID")
myapp = App(root)
myapp.mainloop()




