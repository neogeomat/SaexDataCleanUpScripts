from Tkinter import *

version = "v2.1.1"

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
        if os.path.exists(path+"\\"+path.split("\\")[-1]+"_merged.mdb"):
            os.remove(path+"\\"+path.split("\\")[-1]+"_merged.mdb")
            print("old merged file deleted")
        # mdb_list = glob.glob(path+"\**\*.mdb")
        # mdb_list.extend(glob.glob(path+"\*.mdb"))

        mdb_list = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
        
        # print(mdb_list)
        total_mdbs = len (mdb_list)
        # merged = "D:\\LIS_SYSTEM\\LIS_Spatial_Data\\merged.mdb"

        # copy first file
        try:
            shutil.copy(r'D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\BLANK84.mdb', path+"\\"+path.split("\\")[-1]+"_merged.mdb")
            print("D:\\LIS_SYSTEM\\LIS_Spatial_Templates\\BLANK84.mdb copied as "+path.split("\\")[-1]+"_merged.mdb")
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", sys.exc_info())
        merged = path+"\\"+path.split("\\")[-1]+"_merged.mdb\\"

        # start geoprocess
        layers = ["Parcel","Segments","Construction","Parcel_History"]
        count = 0
        for i in mdb_list:
            env.workspace = i
            count += 1
            print (env.workspace + " (" + str (count) + "/" + str (total_mdbs) + ")")
            for l in layers:
                arcpy.Append_management(l, merged + l, "NO_TEST", "", "")
                # print(merged + l)
                # arcpy.Merge_management(l, merged)
        print("process complete")
        tkMessageBox.showinfo(title="Merge Saex Mdb files" + version, message="Done")
            
root = Tk()
root.title("Merge Saex Mdb files" + version)
myapp = App(root)
myapp.mainloop()




