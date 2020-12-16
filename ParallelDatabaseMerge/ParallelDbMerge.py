from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog

version = "v2.1.0"

class App (Frame):
    global version

    def browse_button1(self):
        # global folder_path
        self.SourceMDB = tkFileDialog.askopenfilename()
        self.folder_path.set(self.SourceMDB )

    def browse_button2(self):
        self.TargetMDB = tkFileDialog.askopenfilename()
        self.folder_path1.set(self.TargetMDB )

    def create_widgets(self):

        """Create buttons that do nothing"""
        self.folder_path = StringVar()
        self.folder_path1 = StringVar()

        # create label for sheet
        self.Sheet = Label (self, text="Select first mdb file as source", width=30)
        self.Sheet.grid (row=0, column=0)

        # create entry.
        self.sheet = Label(self, textvariable=self.folder_path)
        self.sheet.grid(row=0, column=1, padx=5, pady=5,sticky=E + W + N + S)

        self.sourceMdb = Button(self,text="Browse source", command=self.browse_button1,height=1)
        #folder_path.set(self.sourceMdb)
        self.sourceMdb.grid (row=0, column=2, padx=5, pady=5, sticky=E + W + N + S)

        # create label for District
        self.Sheet = Label (self, text="Select second mdb file as target", width=30)
        self.Sheet.grid (row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheet = Label(self, textvariable=self.folder_path1)
        self.sheet.grid(row=1, column=1, padx=5, pady=5,sticky=E + W + N + S)

        self.targetMdb = Button(self, text="Browse target", command=self.browse_button2)
        #folder_path1.set(self.sourceMdb)
        self.targetMdb.grid (row=1, column=2, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button (self, text="Process", command=self.ParallelDbMerge, width=30)
        self.button4.grid (row=3, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label (self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid (row=4, column=1, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: 

Process:
 
Output: 
For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label (self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid (row=5, columnspan=5, padx=5, pady=5, sticky=E + W + N + S)
    def __init__(self, master):
        Frame.__init__ (self, master)
        self.create_widgets ()
        self.pack()
        self.grid()

    def ParallelDbMerge(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        from arcpy import env
        import re
        folder_path = StringVar()
        folder_path1 = StringVar()

        ###
        # Script arguments
        #Sourceparcel = self.sourceMdb.get() + "\\Parcel"
        # print self.sourceMdb.get()
        print self.SourceMDB
        print self.TargetMDB
        Sourceparcel = self.SourceMDB + "\\Parcel"

        #TargetParcel = self.targetMdb.get() + "\\Parcel"
        TargetParcel = self.TargetMDB + "\\Parcel"

        Parcel1 = TargetParcel + "1"
        # Process: Rename
        # arcpy.Rename_management (TargetParcel, Parcel_Rename, "FeatureClass")

        # Process: Make Feature Layer (4)
        arcpy.MakeFeatureLayer_management (Sourceparcel, "Sourceparcel_layer", "", "", "PARCELKEY PARCELKEY VISIBLE NONE;PARCELNO PARCELNO VISIBLE NONE;DISTRICT DISTRICT VISIBLE NONE;VDC VDC VISIBLE NONE;WARDNO WARDNO VISIBLE NONE;GRIDS1 GRIDS1 VISIBLE NONE;PARCELTY PARCELTY VISIBLE NONE;Shape_Length Shape_Length VISIBLE NONE;Shape_Area Shape_Area VISIBLE NONE;ParcelNote ParcelNote VISIBLE NONE")

        # Process: Make Feature Layer (3)
        arcpy.MakeFeatureLayer_management (TargetParcel, "TargetParcel_layer", "", "", "PARCELKEY PARCELKEY VISIBLE NONE;PARCELNO PARCELNO VISIBLE NONE;DISTRICT DISTRICT VISIBLE NONE;VDC VDC VISIBLE NONE;WARDNO WARDNO VISIBLE NONE;GRIDS1 GRIDS1 VISIBLE NONE;PARCELTY PARCELTY VISIBLE NONE;Shape_Length Shape_Length VISIBLE NONE;Shape_Area Shape_Area VISIBLE NONE;ParcelNote ParcelNote VISIBLE NONE")

        # Process: Select Layer By Location
        # arcpy.SelectLayerByLocation_management (Parcel_Layer1, "CONTAINS", Parcel_Layer1__2_, "", "NEW_SELECTION", "NOT_INVERT")
        arcpy.SelectLayerByLocation_management ("Sourceparcel_layer", "CONTAINS", "TargetParcel_layer", "", "NEW_SELECTION", "NOT_INVERT")

        # Process: Select Layer By Attribute
        # arcpy.SelectLayerByAttribute_management (Parcel__3_, "SWITCH_SELECTION", "")
        arcpy.SelectLayerByAttribute_management ("Sourceparcel_layer", "SWITCH_SELECTION", "")

        # Process: Select Layer By Location (2)
        # arcpy.SelectLayerByLocation_management (Parcel_Layer1__2_, "CONTAINS", Parcel_F__3_, "", "NEW_SELECTION", "NOT_INVERT")
        arcpy.SelectLayerByLocation_management ("TargetParcel_layer", "CONTAINS", "Sourceparcel_layer", "", "NEW_SELECTION", "NOT_INVERT")

        # Process: Select Layer By Attribute (2)
        # arcpy.SelectLayerByAttribute_management (Parcel_F__2_, "SWITCH_SELECTION", "")
        arcpy.SelectLayerByAttribute_management ("TargetParcel_layer", "SWITCH_SELECTION", "")

        # Process: Make Feature Layer (2)
        # arcpy.MakeFeatureLayer_management (Parcel_F__4_, Output_Layer__2_, "", "", "PARCELKEY PARCELKEY VISIBLE NONE;PARCELNO PARCELNO VISIBLE NONE;DISTRICT DISTRICT VISIBLE NONE;VDC VDC VISIBLE NONE;WARDNO WARDNO VISIBLE NONE;GRIDS1 GRIDS1 VISIBLE NONE;PARCELTY PARCELTY VISIBLE NONE;Shape_Length Shape_Length VISIBLE NONE;Shape_Area Shape_Area VISIBLE NONE;ParcelNote ParcelNote VISIBLE NONE")

        # Process: Merge
        # arcpy.Merge_management ("Parcel_Rename_Layer1;Parcel_Layer", Parcel1, "PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#,Parcel_Layer,PARCELKEY,-1,-1,Parcel_Rename_Layer1,PARCELKEY,-1,-1;PARCELNO \"PARCELNO\" true true false 4 Long 0 0 ,First,#,Parcel_Layer,PARCELNO,-1,-1,Parcel_Rename_Layer1,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 2 Short 0 0 ,First,#,Parcel_Layer,DISTRICT,-1,-1,Parcel_Rename_Layer1,DISTRICT,-1,-1;VDC \"VDC\" true true false 2 Short 0 0 ,First,#,Parcel_Layer,VDC,-1,-1,Parcel_Rename_Layer1,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#,Parcel_Layer,WARDNO,-1,-1,Parcel_Rename_Layer1,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#,Parcel_Layer,GRIDS1,-1,-1,Parcel_Rename_Layer1,GRIDS1,-1,-1;PARCELTY \"PARCELTY\" true true false 2 Short 0 0 ,First,#,Parcel_Layer,PARCELTY,-1,-1,Parcel_Rename_Layer1,PARCELTY,-1,-1;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,Parcel_Layer,Shape_Length,-1,-1,Parcel_Rename_Layer1,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,Parcel_Layer,Shape_Area,-1,-1,Parcel_Rename_Layer1,Shape_Area,-1,-1;ParcelNote \"ParcelNote\" true true false 200 Text 0 0 ,First,#,Parcel_Layer,ParcelNote,-1,-1,Parcel_Rename_Layer1,ParcelNote,-1,-1")
        arcpy.Merge_management ("Sourceparcel_layer;TargetParcel_layer", Parcel1)

        # Process: Delete
        # arcpy.Delete_management (Parcel_Rename, "")
        arcpy.Delete_management (TargetParcel, "")
        arcpy.Rename_management (Parcel1, TargetParcel, "FeatureClass")

        ###
        tkMessageBox.showinfo (title="Parallel Database Merge" + version, message="Done")

root = Tk ()
root.title ("Parallel Database Merge" + version)
myapp = App (root)
myapp.mainloop ()
