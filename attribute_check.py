from Tkinter import *

version = "v2.1.3"

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
        self.button4 = Button(self, text="Process", command=self.attributeChecker, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n Checks for blank attributes and incorrect attribute within parcel layer of mdb files. The error are populated in a csv file in the same folder containing mdb file.

Requires arcpy (available through arcgis 10.x) and saex. Python executable must be from the arcgis installation.

Input: Folder path

Process: This scripts loops though each row of parcel layer of each mdb file in the path recursively and checks for blank and incorrect attributes for DISTRICT, VDC, MARDNO, GRIDS1, PARCELNO and PARCELTY columns. The errors inr each mdb file is populated showing the error along with PARCELID into seperate .csv file (containg the mdb file name) in the same location. 

Output: .csv file containing the error for each mdb file in the same location. The error in the mdb should be corrected manually.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def attributeChecker(self):
        import tkMessageBox
        import arcpy
        import os
        import time
        from arcpy import env
        starttime = time.time();
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_check_attr.csv","a")
        exception_list.truncate(0)
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
        total_mdbs = len(mdb_list)
        # print(mdb_list)
        # start geoprocess
        layers = ["Parcel"]
        allerror=open(path+"\\ALL_ERROR.csv","a")
        allerror.truncate(0)
        count = 0
        for i in mdb_list:
            try:
                arcpy.Compact_management(i)
            except:
                exception_list.write("Compact Error for ,"+i+"\n")
                print("Compact error for " + i)
            f = open(i + "_error.csv", "a")
            f.truncate(0)
            env.workspace = i
            count += 1
            print (env.workspace + " (" + str(count) + "/" + str(total_mdbs)+ ")")
            # print (" (" + str(count) + "/" + str(total_mdbs)+ ")")
            for l in layers:
                TheShapefile = i + "\\" + l
                # print TheShapefile
                try:
                    if arcpy.Exists(TheShapefile):
                        TheRows = arcpy.SearchCursor(TheShapefile)

                        #Check if Column exists
                        isDistrict = arcpy.ListFields(TheShapefile, "DISTRICT")
                        if (len(isDistrict)) != 1:
                            f.write("District Column does not exist"+ "\n")
                            allerror.write("District Column does not exist, ,"+i+ "\n")
                            skipDistrict=True
                        else:
                            skipDistrict=False

                        isVDC = arcpy.ListFields(TheShapefile, "VDC")
                        if (len(isVDC)) != 1:
                            f.write("VDC Column does not exist"+ "\n")
                            allerror.write("VDC Column does not exist, ,"+i+ "\n")
                            skipVDC=True
                        else:
                            skipVDC=False

                        isWard = arcpy.ListFields(TheShapefile, "WARDNO")
                        if (len(isWard)) != 1:
                            f.write("Ward No Column does not exist"+ "\n")
                            allerror.write("Ward No Column does not exist, ,"+i+ "\n")
                            skipWard=True
                        else:
                            skipWard=False

                        isGrid = arcpy.ListFields(TheShapefile, "GRIDS1")
                        if (len(isGrid)) != 1:
                            f.write("Grid Sheet Column does not exist"+ "\n")
                            allerror.write("Grid Sheet Column does not exist, ,"+ i + "\n")
                            skipGrid=True
                        else:
                            skipGrid=FALSE

                        isParcelty = arcpy.ListFields(TheShapefile, "PARCELTY")
                        if (len(isParcelty)) != 1:
                            f.write("Parcel Type Column does not exist" + "\n")
                            allerror.write("Parcel Type Column does not exist, ," + i + "\n")
                            skipParcelty = True
                        else:
                            skipParcelty = False

                        isParcelno = arcpy.ListFields(TheShapefile, "PARCELNO")
                        if (len(isParcelty)) != 1:
                            f.write("Parcel No Column does not exist" + "\n")
                            allerror.write("Parcel No Column does not exist, ," + i + "\n")
                            skipParcelno = True
                        else:
                            skipParcelno = False

                        #Check if Suspicious Column exists
                        isSuspicious = arcpy.ListFields(TheShapefile, "suspicious")
                        if (len(isSuspicious)) != 1:
                            f.write("Suspicious Column does not exist"+ "\n")
                            allerror.write("Suspicious Column does not exist, ,"+ i + "\n")
                            skipSuspicious=True
                        else:
                            skipSuspicious=False

                        # Loop through each row in the attributes
                        for TheRow in TheRows:
                            if not skipDistrict:
                                District = TheRow.getValue("DISTRICT")
                                if District is None or District == "" or District == " ":
                                    f.write("District Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("District Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i + "\n")
                                elif District > 75 or District == 0:
                                    f.write("District Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("District Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i + "\n")

                            if not skipVDC:
                                VDC = TheRow.getValue("VDC")
                                if VDC is None or VDC == "" or VDC == " ":
                                    f.write("VDC Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("VDC Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")
                                elif VDC > 9999 or VDC == 0:
                                    f.write("VDC Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("VDC Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i + "\n")

                            if not skipWard:
                                Wardno = TheRow.getValue("WARDNO")
                                if Wardno is None or Wardno == "" or Wardno == " ":
                                    f.write("Ward No Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Ward No Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")
                                elif (not Wardno.isdigit()):
                                    f.write("Ward No in Digit and String at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + ", Check mapsheets_code for freesheets\n")
                                    allerror.write("Ward No in Digit and String at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + ", Check mapsheets_code for freesheets" + "," + i +"\n")
                                elif (int(Wardno) == 0 or int(Wardno) > 35):
                                    f.write("Ward No Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Ward No Error at OBJECTID=," + str(TheRow.getValue("OBJECTID"))  + "," + i + "\n")

                            if not skipGrid:
                                Grid = TheRow.getValue("GRIDS1")
                                if (Grid is None or len(Grid) == 0 or Grid == " " or Grid == ""):
                                    f.write("Grid Sheet Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Grid Sheet Code Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")
                                elif (len(Grid) > 9 or len(Grid) < 7):
                                    f.write("Grid Sheet Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Grid Sheet Code Error at OBJECTID=," + str(TheRow.getValue("OBJECTID"))  + "," + i + "\n")

                            if not skipParcelno:
                                Parcelno = TheRow.getValue("PARCELNO")
                                if (Parcelno is None or Parcelno is ""):
                                    f.write("Parcel No Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Parcel No Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")
                                elif (int(Parcelno) == 0):
                                    f.write("Parcel No 0 at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Parcel No 0 at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")

                            if not skipParcelty:
                                Parceltype = TheRow.getValue("PARCELTY")
                                if (Parceltype == None):
                                    f.write("Parcel Type Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Parcel Type Blank at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")

                            if not skipSuspicious:
                                Suspicioustype = TheRow.getValue("suspicious")
                                if (str(Suspicioustype).lower() == "yes"):
                                    f.write("Suspicious Type YES at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "\n")
                                    allerror.write("Suspicious Type YES at OBJECTID=," + str(TheRow.getValue("OBJECTID")) + "," + i  + "\n")
                    else:
                        f.write("Parcel Layer not found for \n"+i)
                        allerror.write("Parcel Layer not found for \n"+i)
                except:
                    exception_list.write("Attribute Check Error for ,"+i+"\n")
        print("process complete")
        f.close()

        endtime = time.time()
        print("TIme taken: " + str(endtime -starttime))
        tkMessageBox.showinfo(title="Check Attribute Errors" + version, message="Done")
        allerror.close()


root = Tk()
root.title("Check Attribute Errors " + version)
myapp = App(root)
myapp.mainloop()
