from Tkinter import *
from tkMessageBox import showerror

class App(Frame):
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
        self.button4=Button(self, text="Check Topology", command=self.topologycheck, width=30)
        self.button4.grid(row=1, column=1, sticky=E+W+N+S)

    def topologycheck (self):   
        import tkMessageBox
        import arcpy
        import glob
        from arcpy import env
        path = self.sheetentry1.get()
        list = glob.glob(path+"\*.mdb")
        for i in list:
            env.workspace = i


            # Local variables:           
            TerrorLine = r"\FDS\Topologyerr_line"
            TerrorPoint = r"\FDS\Topologyerr_point"
            TerrorPoly = r"\FDS\Topologyerr_poly"

            if arcpy.Exists("FDS/Topology") and arcpy.Exists("FDS/Parcel1") and arcpy.Exists("FDS/Building1") :
                #overwrite if feature exists
                arcpy.env.overwriteOutput = True

                # Process: Create Feature Dataset
                arcpy.CreateFeatureDataset_management(i, "FDS", "")

                # Process: Create Topology
                arcpy.CreateTopology_management("FDS", "Topology", "")

                # Process: Feature Class to Feature Class
                arcpy.FeatureClassToFeatureClass_conversion("Parcel", "FDS", "Parcel1", "", "", "")
                arcpy.FeatureClassToFeatureClass_conversion("Construction", "FDS", "Building1", "", "", "")

                # Process: Add Feature Class To Topology
                arcpy.AddFeatureClassToTopology_management("FDS/Topology", "FDS/Parcel1", "1", "1")
                arcpy.AddFeatureClassToTopology_management("FDS/Topology", "FDS/Building1", "1", "1")

                # Process: Add Rule To Topology
                arcpy.AddRuleToTopology_management("FDS/Topology", "Must Not Have Gaps (Area)", "FDS/Parcel1", "", "", "")
                arcpy.AddRuleToTopology_management("FDS/Topology", "Must Not Overlap (Area)", "FDS/Parcel1", "", "", "")
                arcpy.AddRuleToTopology_management("FDS/Topology", "Must Be Covered By (Area-Area)", "FDS/Building1", "", "Parcel1", "")

                # Process: Validate Topology
                arcpy.ValidateTopology_management("FDS/Topology", "Full_Extent")

                # Process: Export Topology Errors
                arcpy.ExportTopologyErrors_management("FDS/Topology", "FDS","Topologyerr")

                #counting Number of topology errors
                NumErr1 = arcpy.GetCount_management(TerrorLine)
                NumErr2 = arcpy.GetCount_management(TerrorPoint)
                NumErr3 = arcpy.GetCount_management(TerrorPoly)          

                f=open("D://error.txt","a")
                f.write("{} has {} topological errors \n".format( i, int(NumErr1[0])+int(NumErr2[0])+int(NumErr3[0])))

                f.close()


        tkMessageBox.showinfo(title="Topology Check", message="Done")
            
root = Tk()
root.title("Topology Check")
myapp = App(root)
myapp.mainloop()




