from Tkinter import *

version = "v1.1.3"

class App(Frame):
    global version
    global dic_case_sen

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

        # create label for District
        self.Sheet = Label(self, text="Enter District Code", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.DistrictCode = Entry(self, width=30)
        self.DistrictCode.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create label for VDC
        self.Sheet = Label(self, text="Enter VDC Code", width=30)
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.VDCCode = Entry(self, width=30)
        self.VDCCode.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.attributeChecker, width=30)
        self.button4.grid(row=3, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=4, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path, district does and vdc code

Process: At First Input the folder path for whole district, then give the district code and leave vdc code blank.This will fill the district attribute for all mdbs.
        Then again run the program and then Input the folder path for each vdc and each time give the vdc code but leave district code blank.This will fill the vdc code each time you run the program for each folder.
 
Output: The Parcel shapefile with District Code, Vdc code filled.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=5, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def attributeChecker(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        from arcpy import env
        import re
        district_code=self.DistrictCode.get()
        vdc_code=self.VDCCode.get()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_att_fill_vdc_dis_code.csv","a")
        exception_list.truncate(0)
        allerror = open (path + "\\regex.csv", "a")
        allerror.truncate (0)
        for root, dirnames, filenames in os.walk(path):
            [dirnames.remove(d) for d in list(dirnames) if os.path.join(root,d).lower().find('file')!=-1]
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    parcelfile=os.path.join(root, filename,"Parcel")
                    print (parcelfile)
                    try:
                        arcpy.Compact_management(os.path.join(root,filename))
                    except:
                        exception_list.write("Compact Error for ,"+filename+"\n")
                        print("Compact error for "+filename)

                    new_filename = filename.replace(" ", "")
                    x = re.findall ("^...[A-Za-z\s_]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
                    print(x)
                    if x:
                        #print(filename+","+x[0][0]+x[0][1]+x[0][2])
                        #bad_chars = ['_', '-', '(', ")"," "]
                        #new_string_name = ''.join(i for i in x[0][1] if not i in bad_chars)
                        try:
                            if(district_code != '' and int(district_code)):
                                arcpy.CalculateField_management(parcelfile,"DISTRICT",int(district_code),"PYTHON")#FOR DISTRICT_CODE
                            if (vdc_code != '' and int(vdc_code)):
                                arcpy.CalculateField_management(parcelfile,"VDC",int(vdc_code),"PYTHON")#FOR VDC_CODE

                        except:
                            exception_list.write("Attribute fill Error for ," + filename + "\n")
                            allerror.write(filename + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + ",error" +"\n")

                    else:
                        print(filename + "," + " ")
                        allerror.write (filename + "," + " " + "\n")
        tkMessageBox.showinfo(title="Fix Attribute Errors" + version, message="Done")
        allerror.close()
        exception_list.close()


root = Tk()
root.title("Fill Attributes " + version)
myapp = App(root)
myapp.mainloop()
