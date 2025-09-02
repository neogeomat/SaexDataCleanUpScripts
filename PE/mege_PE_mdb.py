from Tkinter import *

version = "v2.2.0"

class App(Frame):
    global version
    def __init__(self, master):
        Frame.__init__(self,master)
        self.pack()

        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create buttons that do nothing"""

        #create label for sheet
        self.Sheet=Label(self, text="Enter path to the main folder",width=30)
        self.Sheet.grid(row=0, column=0,sticky=E+W+N+S)

        #create entry.
        self.sheetentry1= Entry(self,width=30)
        self.sheetentry1.grid(row=0, column =1, sticky=E+W+N+S)        

        #create calculate button
        self.button4=Button(self, text="Process", command=self.mergeSaexMdbs, width=30)
        self.button4.grid(row=1, column=1, sticky=E+W+N+S)

        self.Sheet = Label (self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid (row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n Merges parcel, segments, construction and history layers from all saex mdb files in a folder. Requires arcpy (available through arcgis 10.x) and saex. Python executable must be from the arcgis installation.

Input: Folder path Output: merged database of name path_merged, It uses BLANK84 template.

How to run: open the file in python idle and run (press F5). If error occurs, the process repeats from start (deletes the file created before).

If run from a network location, the process may appear as not running as network file access is slower.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts
        """
        self.Sheet = Label (self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid (row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def mergeSaexMdbs (self):
        import tkMessageBox
        import arcpy
        import glob
        import os
        import shutil
        from arcpy import env
        path = self.sheetentry1.get()
        #print(path)
        exception_list= open(path+"\\exception_list_merge.csv","a")
        if os.path.exists(path+"\\"+path.split("\\")[-1]+"_merged.mdb"):
            os.remove(path+"\\"+path.split("\\")[-1]+"_merged.mdb")
            print("old merged file deleted")
        # mdb_list = glob.glob(path+"\**\*.mdb")
        # mdb_list.extend(glob.glob(path+"\*.mdb"))

        mdb_list = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    if (filename.startswith("Backup")):
                        continue
                    mdb_list.append(os.path.join(root, filename))
        
        # print(mdb_list)
        total_mdbs = len (mdb_list)
        # merged = "D:\\LIS_SYSTEM\\LIS_Spatial_Data\\merged.mdb"

        # copy first file
        try:
            shutil.copy(r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\BLANK_81.mdb', path+"\\"+path.split("\\")[-1]+"_merged.mdb")
            print("D:\\LIS_SYSTEM\\LIS_Spatial_Templates\\BLANK_81.mdb copied as "+path.split("\\")[-1]+"_merged.mdb")
        except IOError as e:
            exception_list.write("Unable to Copy Error for ," + path + "\n")
            print("Unable to copy file. %s" % e)
        except:
            exception_list.write("Unexpected Error for ," + path + "\n")
            print("Unexpected error:", sys.exc_info())
        merged = path+"\\"+path.split("\\")[-1]+"_merged.mdb\\"

        building = "\\Cadastre\\Building"
        const_line = "\\Cadastre\\Construction_Line"
        const_poly = "\\Cadastre\\Construction_Polygon"
        country = "\\Cadastre\\Country"
        district = "\\Cadastre\\District"
        parcel = "\\Cadastre\\Parcel"
        parcel_hist = "\\Cadastre\\ParcelHistory"
        parcel_line = "\\Cadastre\\ParcelLine"
        region = "\\Cadastre\\Region"
        VDCMunicipality = "\\Cadastre\\VDCMunicipality"
        ward = "\\Cadastre\\Ward"

        control_point = "\\Topographic\\ControlPoint"
        designatedArea = "\\Topographic\\DesignatedArea"
        geolocation = "\\Topographic\\Geolocation"
        hydrographic = "\\Topographic\\Hydrographic"
        hydropoint = "\\Topographic\\HydroPoint"
        landuse = "\\Topographic\\LandUse"
        topo = "\\Topographic\\Topo"
        transportation = "\\Topographic\\Transportation"
        utility = "\\Topographic\\Utility"
        utility_line = "\\Topographic\\UtilityLine"
        utility_point = "\\Topographic\\UtilityPoint"

        annotation = "\\Annotation"
        gridsheet = "\\GridSheet"
        legalParcel = "\\LegalParcel"
        master_table = "\\MasterTable"
        owner = "\\Owner"
        parcel_ref = "\\ParcelReference"
        temp_table = "\\TempTable"
        tenant = "\\Tenant"
        verticalparcel = "\\VerticalParcel"

        arcpy.AddField_management(merged + parcel, "source_file", "TEXT")
        arcpy.AddField_management(merged + parcel_line, "source_file", "TEXT")
        arcpy.AddField_management(merged + const_poly, "source_file", "TEXT")

        # start geoprocess
        cadastre_layers = [building,const_line,const_poly ,country,district,parcel,parcel_hist,parcel_line,region,VDCMunicipality,ward ]
        topo_layers = [ control_point,designatedArea,geolocation,hydrographic, hydropoint, landuse,topo,transportation, utility, utility_line, utility_point]
        other_layers = [  annotation,gridsheet,legalParcel, master_table, owner,parcel_ref,temp_table,tenant,verticalparcel]
        # arcpy.AddField_management(merged + "Parcel","source_file","TEXT",None,None,50,None,True,None,None)
        count = 0
        for i in mdb_list:
            env.workspace = i
            count += 1
            print (env.workspace + " (" + str (count) + "/" + str (total_mdbs) + ")")
            for l in cadastre_layers:
                try:
                    if ("Parcel" in l):
                        arcpy.AddField_management(i + parcel, "source_file", "TEXT")
                        head, tail = os.path.split(i)
                        tail = tail.replace(" ", "")
                        location_str = str(tail[:-4])
                        arcpy.CalculateField_management(i + parcel, "source_file", "'" + location_str + "'", "PYTHON")

                    arcpy.Append_management(l, merged + l, "NO_TEST", "", "")
                    arcpy.DeleteField_management(l,["source_file"])
                    # print(merged + l)
                    # arcpy.Merge_management(l, merged)
                except:
                    exception_list.write("Merge Database Error for ," + i + "\n")
        for l in topo_layers:
            try:
                arcpy.Append_management(l, merged + l, "NO_TEST", "", "")
                arcpy.DeleteField_management(l, ["source_file"])
            except:
                exception_list.write("Merge Database Error for ," + i + "\n")
        for l in other_layers:
            try:
                arcpy.Append_management(l, merged + l, "NO_TEST", "", "")
                arcpy.DeleteField_management(l, ["source_file"])
            except:
                exception_list.write("Merge Database Error for ," + i + "\n")
        print("process complete")
        tkMessageBox.showinfo(title="Merge PE Mdb files" + version, message="Done")
            
root = Tk()
root.title("Merge PE Mdb files" + version)
myapp = App(root)
myapp.mainloop()




