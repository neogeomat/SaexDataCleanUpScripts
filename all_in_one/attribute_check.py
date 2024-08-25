from Tkinter import *
import shared_data

def attributeChecker(self):
    import tkMessageBox
    import arcpy
    import os
    import time
    from arcpy import env
    starttime = time.time();
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_check_attr.csv","a")
    exception_list.truncate(0)

    total_mdbs = len(mdb_list)

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
    print("Time taken: " + str(endtime -starttime))
    tkMessageBox.showinfo(title="Check Attribute Errors", message="Done")
    allerror.close()
