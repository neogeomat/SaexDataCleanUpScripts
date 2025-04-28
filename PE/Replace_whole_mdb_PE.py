# -*- coding: utf-8 -*-
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
            "Blank_.mdb",
            "Blank_81.mdb",
            "Blank_84.mdb",
            "Blank_87.mdb"
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
        reload(sys)
        sys.setdefaultencoding('utf-8')
        Folder_Location = "d:"
        DataCleanTemp = Folder_Location + "\\DataCleanTemp"
        startTime = time.time ()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_whole_mdb_replace.csv","a")
        exception_list.truncate(0)
        count = 0

        option_choosed=self.variable.get()
        blank_data="D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\\"+option_choosed

        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)


        for i in mdb_list:
            count += 1
            out_data = "D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\\test.mdb"

            feature_lists=[]

            building="\\Cadastre\\Building"
            const_line="\\Cadastre\\Construction_Line"
            const_poly="\\Cadastre\\Construction_Polygon"
            country="\\Cadastre\\Country"
            district="\\Cadastre\\District"
            parcel="\\Cadastre\\Parcel"
            parcel_hist="\\Cadastre\\ParcelHistory"
            parcel_line="\\Cadastre\\ParcelLine"
            region="\\Cadastre\\Region"
            VDCMunicipality="\\Cadastre\\VDCMunicipality"
            ward="\\Cadastre\\Ward"

            control_point="\\Topographic\\ControlPoint"
            designatedArea="\\Topographic\\DesignatedArea"
            geolocation="\\Topographic\\Geolocation"
            hydrographic="\\Topographic\\Hydrographic"
            hydropoint="\\Topographic\\HydroPoint"
            landuse="\\Topographic\\LandUse"
            topo="\\Topographic\\Topo"
            transportation="\\Topographic\\Transportation"
            utility="\\Topographic\\Utility"
            utility_line="\\Topographic\\UtilityLine"
            utility_point="\\Topographic\\UtilityPoint"

            annotation="\\Annotation"
            gridsheet="\\GridSheet"
            legalParcel="\\LegalParcel"
            master_table="\\MasterTable"
            owner="\\Owner"
            parcel_ref="\\ParcelReference"
            temp_table="\\TempTable"
            tenant="\\Tenant"
            verticalparcel="\\VerticalParcel"

            feature_lists.append(building)
            feature_lists.append(const_line)
            feature_lists.append(const_poly)
            feature_lists.append(country)
            feature_lists.append(district)
            feature_lists.append(parcel)
            feature_lists.append(parcel_hist)
            feature_lists.append(parcel_line)
            feature_lists.append(region)
            feature_lists.append(VDCMunicipality)
            feature_lists.append(ward)
            feature_lists.append(control_point)
            feature_lists.append(designatedArea)
            feature_lists.append(geolocation)
            feature_lists.append(hydrographic)
            feature_lists.append(hydropoint)
            feature_lists.append(landuse)
            feature_lists.append(topo)
            feature_lists.append(transportation)
            feature_lists.append(utility)
            feature_lists.append(utility_line)
            feature_lists.append(utility_point)

            feature_lists.append(annotation)
            feature_lists.append(gridsheet)
            feature_lists.append(legalParcel)
            feature_lists.append(master_table)
            feature_lists.append(owner)
            feature_lists.append(parcel_ref)
            feature_lists.append(temp_table)
            feature_lists.append(tenant)
            feature_lists.append(verticalparcel)


            arcpy.Copy_management(blank_data, out_data)

            for features in feature_lists:
                feature_path = i+features  # Source feature
                target_path = out_data+features  # Target for append
                print("For"+features)
                desc = arcpy.Describe(feature_path)
                print("Dataset Type:", desc.datasetType)
                print("Shape Type:", getattr(desc, "shapeType", "No Shape"))  # Avoids errors if no shape

                if arcpy.Exists(i + features):
                    if "SDB_4__" in features:  # If it's an SDB layer
                        arcpy.RegisterWithGeodatabase_management(feature_path)

                        try:
                            print("Processing:", feature_path)

                            temp_fc = os.path.join("in_memory", features + "_fc")  # Convert to FC
                            arcpy.FeatureClassToFeatureClass_conversion(feature_path, "in_memory", features + "_fc")

                            arcpy.Append_management(temp_fc, target_path, "NO_TEST")

                            # Recalculate Extent for spatial correctness
                            desc = arcpy.Describe(temp_fc)
                            if desc.shapeType in ["Point", "Polyline", "Polygon"]:
                                arcpy.RecalculateFeatureClassExtent_management(temp_fc)

                            # Cleanup temporary in-memory FC
                            arcpy.Delete_management(temp_fc)
                        except Exception as e:
                            print("Error appending SDB Layer:", features, e)

                    else:
                        arcpy.Append_management(i + features, out_data + features, "NO_TEST")
                    if("Cadastre" in features):
                        arcpy.RecalculateFeatureClassExtent_management(i + features)
                else:
                    print(features +" Layer not found for, " + i)

            arcpy.env.workspace = i;
            arcpy.Copy_management(out_data, i)
            arcpy.Delete_management(out_data)
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print("Replace Whole Mdb complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Replace Whole MDB" + version, message="Done")
root = Tk()
root.title("Replace Mdb databases " + version)
myapp = App(root)
myapp.mainloop()
