from Tkinter import *


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
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.parcelIDcreator, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """Version: 2.0

Checks for blank attributes and incorrect attribute within parcel layer of mdb files. The error are populated in a csv file in the same folder containing mdb file.

Requires arcpy (available through arcgis 10.x) and saex. Python executable must be from the arcgis installation.

Input: Folder path

Process: This scripts loops though each row of parcel layer of each mdb file in the path recursively and checks for blank and incorrect attributes for DISTRICT, VDC, MARDNO, GRIDS1, PARCELNO and PARCELTY columns. The errors inr each mdb file is populated showing the error along with PARCELID into seperate .csv file (containg the mdb file name) in the same location. 

Output: .csv file containing the error for each mdb file in the same location. The error in the mdb should be corrected manually."""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def parcelIDcreator(self):
        import tkMessageBox
        import arcpy
        import os
        from arcpy import env
        path = self.sheetentry1.get()
        mdb_list = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))

        print(mdb_list)
        # start geoprocess
        layers = ["Parcel"]
        for i in mdb_list:
            f = open(i + "_error.csv", "a")
            f.truncate(0)
            env.workspace = i
            print (env.workspace)
            for l in layers:
                TheShapefile = i + "\\" + l
                # print TheShapefile
                TheRows = arcpy.SearchCursor(TheShapefile)
                # Loop through each row in the attributes
                for TheRow in TheRows:
                    District = TheRow.getValue("DISTRICT")
                    VDC = TheRow.getValue("VDC")
                    Wardno = TheRow.getValue("WARDNO")
                    Grid = TheRow.getValue("GRIDS1")
                    Parcelno = TheRow.getValue("PARCELNO")
                    Parceltype = TheRow.getValue("PARCELTY")

                    if District is None or District == "" or District == " ":
                        f.write("District Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                    elif District > 75 or District == 0:
                        f.write("District Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")

                    if VDC is None or VDC:
                        f.write("VDC Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                    elif VDC > 9999 or VDC == 0:
                        f.write("VDC Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")


                    if Wardno is None or Wardno == "" or Wardno == " ":
                        f.write("Ward No Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                    elif (not Wardno.isdigit()):
                        f.write("Ward No in Digit and String at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + ", Check mapsheets_code for freesheets\n")
                    elif (int(Wardno) == 0 or int(Wardno) > 35):
                        f.write("Ward No Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")


                    if (Grid is None or len(Grid) == 0 or Grid == " " or Grid == ""):
                        f.write("Grid Sheet Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                    elif (len(Grid) > 9 or len(Grid) < 7):
                        f.write("Grid Sheet Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")

                    if (Parcelno is None or Parcelno is ""):
                        f.write("Parcel No Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                    elif (int(Parcelno) == 0):
                        f.write("Parcel No 0 at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")


                    if (Parceltype == None):
                        f.write("Parcel Type Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")

        print("process complete")
        f.close()
        tkMessageBox.showinfo(title="Check Attribute Errors v2.0.1", message="Done")


root = Tk()
root.title("Check Attribute Errors v2.0.1")
myapp = App(root)
myapp.mainloop()
