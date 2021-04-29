from Tkinter import *

from arcpy import env

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
Output: Recalculated Extent of all feature classes within Database.

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
        count = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)

        import arcpy
        import arcpy.mapping
        # get the map document
        env.workspace = path
        mxd = arcpy.mapping.MapDocument('CURRENT')
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        mxd.activeView = df.name
        groupLayer = arcpy.mapping.Layer(path + r'\Group.lyr')
        parcelLayer = arcpy.mapping.Layer(path + r'\Parcel.lyr')
        ward_list = []
        count = 0
        total_list = arcpy.ListWorkspaces("*", "Access")
        total_count = len(total_list)
        for fc in total_mdbs:
            arcpy.env.workspace = fc
            count += 1
            new_name = os.path.basename(fc)
            new_filename = new_name.replace(" ", "")
            x = re.findall("^...[A-Za-z][A-Za-z\s_-]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
            ward = x[0][0]
            sheet = x[0][0] + x[0][1] + x[0][2]
            if not ward in ward_list:
                ward_list.append(ward)
                grp_lyr = groupLayer
                grp_lyr.name = ward
                arcpy.mapping.AddLayer(df, grp_lyr, "BOTTOM")
            sub_grp_lyr = groupLayer
            sub_grp_lyr.name = sheet
            targetGroupLayer = arcpy.mapping.ListLayers(mxd, ward, df)[0]
            arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, sub_grp_lyr, "BOTTOM")

            # fcl = arcpy.ListFeatureClasses("*", "All")
            fcl = arcpy.ListFeatureClasses("Parcel", "All")
            for feature in fcl:
                targetSubGroupLayer = arcpy.mapping.ListLayers(mxd, sheet, df)
                # print('\n'.join(map(str, targetSubGroupLayer)))
                pathToFC = arcpy.env.workspace + '/' + feature
                newlayer = arcpy.mapping.Layer(pathToFC)
                # if str(feature).startswith("Parce") and str(feature).endswith("arcel"):
                # print "Apply"+feature
                # arcpy.ApplySymbologyFromLayer_management(newlayer, parcelLayer)
                arcpy.mapping.AddLayerToGroup(df, targetSubGroupLayer[0], newlayer, "BOTTOM")

                # arcpy.mapping.AddLayer(df,newlayer,"BOTTOM")
                arcpy.RefreshTOC()
                arcpy.RefreshActiveView()
                mxd.save()
            print (fc + " (" + str(count) + "/" + str(total_count) + ")")
        print("Creating Mxd process complete")
        print ('The script took {0} second !'.format(time.time() - startTime))
        del mxd
        tkMessageBox.showinfo(title="New mxd database" + version, message="Done")
root = Tk()
root.title("Create Mxd databases " + version)
myapp = App(root)
myapp.mainloop()
