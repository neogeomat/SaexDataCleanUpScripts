# -*- coding: utf-8 -*-
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

        self.Sheet = Label(self, text="Choose Central Meridian", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "Blank_.mdb",
            "Blank_87.mdb",
            "Blank_84.mdb",
            "Blank_81.mdb"
        ]

        self.variable = StringVar(self)
        self.variable.set(options[1]) #default value
        self.optionmenu = OptionMenu(self, self.variable, *options)
        self.optionmenu.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)


        # create calculate button
        self.button4 = Button(self, text="Process", command=self.CompareMDbs, width=30)
        self.button4.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=3, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process:Compares the schema with the blank database 
Output: Differences in Databases.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def CompareMDbs(self):  # sourcery skip
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



        def getFeatureClasses(path):
            arcpy.env.workspace = path
            feature_class = []
            feature_datasets = arcpy.ListDatasets()
            feature_datasets = [''] + feature_datasets if feature_datasets is not None else []
            for ds in feature_datasets:
                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                    feature_class.append(fc)
                for fc in arcpy.ListTables():
                    feature_class.append(fc)
            return feature_class

        blank_fc=getFeatureClasses(blank_data)

        def getLayerFields(path,layer):
            arcpy.env.workspace = path
            datasets = arcpy.ListDatasets(feature_type='feature')
            datasets = [''] + datasets if datasets is not None else []
            for ds in datasets:
                for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                    if(layer == fc):
                        my_layer = os.path.join(arcpy.env.workspace, ds, fc)
                        break
            layer_fields=arcpy.ListFields(my_layer)
            layer_names=[]
            for ls in layer_fields:
                layer_names.append(ls.name)

            return layer_names


        blank_parcel = blank_data + "\\Cadastre\\Parcel"

        blank_parcel_fields = getLayerFields(blank_data,"Parcel")


        def ListDiff(input_data,blank_data,type):
            more_in_path=list(set(input_data).difference(blank_data))
            not_in_path=list(set(blank_data).difference(input_data))

            report_list = open(i +"_"+type +".csv", "a")
            report_list.truncate(0)
            report_list.write("\n" + "Added Layers in Data" + "\n")
            for j in more_in_path:
                report_list.write(j.encode('utf8') + "\n")

            report_list.write("\n" + "Layers not in Data" + "\n")
            for k in not_in_path:
                report_list.write(k.encode('utf8') + "\n")
            report_list.close()


        for i in mdb_list:
            data_parcel=i + "\\Cadastre\\Parcel"
            report = arcpy.management.FeatureCompare(data_parcel,blank_parcel,'OBJECTID','SCHEMA_ONLY','','','','','','','CONTINUE_COMPARE',i+'_parcel_report.csv')

            path_fc=getFeatureClasses(i)
            ListDiff(path_fc,blank_fc,"feature_class")
            data_parcel_fields = getLayerFields(i, "Parcel")
            ListDiff(data_parcel_fields,blank_parcel_fields,"Parcel_Fields")

            # report_list.write("Parcel Layer Report"+"\n")
            # report_list.write(report[1])
            # report_list.write(arcpy.GetMessages())
            # report_list.close()
            # blank_dataset=arcpy.ListDatasets()
        # arcpy.FeatureCompare_management
        #
        # for i in mdb_list:
        #     report_list = open(i + "_report.csv", "a")
        #     report_list.truncate(0)
        #     count += 1
        #     err_count=0
        #     arcpy.env.workspace =i
        #     data_fc=arcpy.ListFeatureClasses()
        #     report_list.write("\n" + "Added Layers in Data" + "\n")
        #
        #     for fc in data_fc:
        #         print(fc+"\n")
        #         if("Parcel" in fc):
        #             pc_fields= arcpy.ListFields(i+"\\Cadastre\\Parcel")
        #             report_list.write("\n" + "Parcel Layers: Field Added" + "\n")
        #             for fields in pc_fields:
        #                 if(fields not in blank_pc_fields):
        #                     report_list.write(str(fields))
        #                     count +=1
        #             report_list.write("\n" + "Parcel Layers: No Field" + "\n")
        #             for fields in blank_pc_fields:
        #                 if (fields not in pc_fields):
        #                     report_list.write(str(fields))
        #                     count +=1
        #         if(fc not in blank_fc):
        #             err_count +=1
        #             report_list.write(str(fc)+"\n")
        #     report_list.write("\n" + "Layers not in Data" + "\n")
        #     for fc in blank_fc:
        #         if(fc not in data_fc):
        #             err_count +=1
        #             report_list.write(str(fc)+"\n")
        #     report_list.close()
        #     print(report_list.closed)
        #     if(err_count == 0):
        #         os.remove(i + "_report.csv")
        #
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print("Compare Database with Blank Mdb")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Compare Database" + version, message="Done")
root = Tk()
root.title("Compare Database " + version)
myapp = App(root)
myapp.mainloop()
