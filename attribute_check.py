from Tkinter import *


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
        self.button4=Button(self, text="Process", command=self.parcelIDcreator, width=30)
        self.button4.grid(row=1, column=1, sticky=E+W+N+S)

        self.Sheet = Label (self, text="Instruction", width=30)
        self.Sheet.grid (row=2, column=0, sticky=E + W + N + S)

    def parcelIDcreator (self):   
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
            f=open(i+"_error.csv","a")
            f.truncate(0)
            env.workspace = i
            #print (env.workspace)
            for l in layers:
                TheShapefile=i+"\\"+l
                #print TheShapefile    
                TheRows=arcpy.SearchCursor(TheShapefile)
                # Loop through each row in the attributes
                for TheRow in TheRows:
                   District = TheRow.getValue("DISTRICT")
                   VDC=TheRow.getValue("VDC")
                   Wardno=TheRow.getValue("WARDNO")
                   Grid=TheRow.getValue("GRIDS1")
                   Parcelno=TheRow.getValue("PARCELNO")
                   Parceltype=TheRow.getValue("PARCELTY")
                   #print "Parcel Type= "+str(Parceltype)
                   if(District is None):
                           f.write("District Code Blank at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("District Code Blank in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))
                   elif(District>99 or District==0):
                           f.write("District Code Error at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("District Code Error in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))

                   if(VDC is None):
                           f.write("VDC Code Blank at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("VDC Code Blank in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))
                   elif(VDC>9999 or VDC==0):
                           f.write("VDC Code Error at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("VDC Code Error in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))

                   if(Wardno is None or Wardno==""):
                           f.write("Ward No Blank at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("Ward No Blank in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))
                   elif(len(Wardno)>3 or int(Wardno)==0 or int(Wardno) > 35):
                          f.write("Ward No Error at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                          #print ("Ward No Error in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))

                   if(Grid is None or len(Grid)==0 or Grid==" "):
                          f.write("Grid Sheet Code Blank at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                          #print ("Grid Sheet Code Blank in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))
                   elif(len(Grid)>9 or len(Grid)<7):
                          f.write("Grid Sheet Code Error at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                          #print ("Grid Sheet Code Error in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))

                   if(Parcelno is None or Parcelno is ""):
                           f.write("Parcel No Blank at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("Parcel No Blank in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))
                   elif(int(Parcelno)==0):
                           f.write("Parcel No 0 at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           #print ("Parcel No 0 in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))

                   if(Parceltype==None):
                           f.write("Parcel Type Blank at OBJECTID=,"+str(TheRow.getValue("OBJECTID"))+"\n")
                           # print ("Parcel Type Blank in "+TheShapefile+" at OBJECTID="+str(TheRow.getValue("OBJECTID")))

        print("process complete")
        f.close()
        tkMessageBox.showinfo(title="Check Attribute Errors v2.0", message="Done")
            
root = Tk()
root.title("Check Attribute Errors v2.0")
myapp = App(root)
myapp.mainloop()
