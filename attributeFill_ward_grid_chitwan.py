from Tkinter import *

version = "v2.3.2"
dic_case_sen = {
    "Ta": "11",
    "Tha": "12",
    "Da": "13",
    "Dha": "14",
    "tta": "16",
    "ttha": "17",
    "dda": "18",
    "ddha": "19",
    "dhha": "19",
    "sha": "30",
    "SHA": "31",
    "sa": "32"
}
dic_case_insen = {
    "": "00",
    "ka": "01",
    "k": "01",

    "kha": "02",
    "kh": "02",

    "ga": "03",
    "gha": "04",
    "nga": "05",
    "ng": "05",
    "ch": "06",
    "cha": "06",
    "chha": "07",
    "ja": "08",
    "jha": "09",
    "yna": "10",
    "yan": "10",
    "ana": "15",
    "na": "20",
    "pa": "21",
    "pha": "22",
    "fa": "22",
    "ba": "23",
    "bha": "24",
    "ma": "25",
    "ya": "26",
    "ra": "27",
    "la": "28",
    "wa": "29",
    "ha": "33",
    "ksha": "34",
    "kshya": "34",
    "tra": "35",
    "gya": "36"
}

dict_scale = {
    "500": "5554",
    "600": "5553",
    "1200": "5555",
    "1250": "5556",
    "2400": "5557",
    "2500": "5558",
    "4800": "5559"
}


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

        # create label for sheet
        self.Sheet = Label(self, text="Enter vdc_code", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheetentry_vdc = Entry(self, width=30)
        self.sheetentry_vdc.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)


        self.Sheet = Label(self, text="Choose Mapped Scale", width=30)
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "500",
            "600",
            "1200",
            "1250",
            "2400",
            "2500",
            "4800"
        ]

        self.variable = StringVar(self)
        self.variable.set(options[5])  # default value(2500)
        self.optionmenu = OptionMenu(self, self.variable, *options)
        self.optionmenu.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.attributeFillWardFrid, width=30)
        self.button4.grid(row=3, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=4, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process: Extracts the ward no and no from the name of the file and creates the grid sheet code. Then it fills the grid code if the grid attribute is blank or error. Also it adds the ward no. to WARDNO column. 
Output: Mdb file with grid sheet code and ward no column filled.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=4, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def attributeFillWardFrid(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        from arcpy import env
        import re
        path = self.sheetentry1.get()
        vdc_code = self.sheetentry_vdc.get()
        mdb_list = []
        allerror = open(path + "\\regex.csv", "a")
        exception_list = open(path + "\\exception_list_att_fill_ward_grid.csv", "a")
        allerror.truncate(0)
        exception_list.truncate(0)

        mapped_scale = self.variable.get()
        if mapped_scale in dict_scale:
            scaled_value = dict_scale[mapped_scale]
        else:
            scaled_value = "5555"
        matches=["file","trig"]

        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    parcelfile=os.path.join(root, filename,"Parcel")
                    print (parcelfile)
                    # Get the list of field names
                    fields = arcpy.ListFields(parcelfile)
                    fields.sort(key=lambda field: field.name)

                    for field in fields:
                        if (field.name == "mother_parcel"):
                            break
                        if ((field.name.lower()) == "old_parcel"):
                            print field.name
                            try:
                                arcpy.AddField_management(parcelfile, "mother_parcel", "TEXT")
                                arcpy.CalculateField_management(parcelfile, "mother_parcel", "!" + field.name + "!",
                                                                "PYTHON")
                                arcpy.DeleteField_management(parcelfile, field.name)
                            except arcpy.ExecuteError as e:
                                print (e)

                    TheRows_1 = arcpy.UpdateCursor(parcelfile)

                    for TheRow in TheRows_1:
                        if ("mother_parcel" in fields):
                            input_m_parcel = TheRow.getValue("mother_parcel")
                            if ("_" in input_m_parcel):
                                input_m_parcel = input_m_parcel.replace("_", ",")
                            TheRows_1.updateRow(TheRow)

                    input_scale = mapped_scale;
                    fieldnames = [str(field.name).lower() for field in fields]
                    # for fn in fieldnames:
                    #    print("Fieldnames:"+fn+"\n")
                    TheRows_2 = arcpy.UpdateCursor(parcelfile)
                    if ('scale' in fieldnames):
                        for TheRow in TheRows_2:
                            input_scale = str(TheRow.getValue("scale"))
                            print("the Scale is:", input_scale);
                            TheRows_2.updateRow(TheRow)
                            break
                        if (":" in input_scale):
                            input_scale = input_scale.split(':')[1]

                        # <editor-fold desc="Description">
                        if(input_scale is None or input_scale ==''):

                            print("No Scale in "+ filename+"\n")

                        else:
                            scaled_value = dict_scale[input_scale]
                            new_filename = filename.replace(" ", "")
                            x = re.findall("^.[A-Za-z][A-Za-z\s_-]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)",
                                           new_filename)
                            print(x)
                            if x:
                                # print(filename+","+x[0][0]+x[0][1]+x[0][2])
                                bad_chars = ['_', '-', '(', ")", " "]
                                new_string_name = ''.join(i for i in x[0][1] if not i in bad_chars)
                                if (new_string_name) in dic_case_sen:
                                    dic_code = dic_case_sen[new_string_name]
                                elif (new_string_name.lower()) in dic_case_insen:
                                    dic_code = dic_case_insen[new_string_name.lower()]
                                # new_string_no = x[0][2]
                                new_string_no = ""
                                ward_code = int(x[0][0])
                                if (ward_code > 99):
                                    continue
                                if new_string_no == "":
                                    new_string_no = "0"
                                try:
                                    print("code=" + scaled_value + x[0][0].zfill(2) + dic_code + new_string_no)
                                    sheet_code = scaled_value + x[0][0].zfill(2) + dic_code + new_string_no
                                    del dic_code
                                    del new_string_no
                                    TheRows = arcpy.UpdateCursor(parcelfile)
                                    for TheRow in TheRows:
                                        # Grid = TheRow.getValue("GRIDS1")
                                        # if (Grid is None or len(Grid) == 0 or Grid == " " or Grid == ""):
                                        TheRow.setValue("GRIDS1", sheet_code)
                                        TheRows.updateRow(TheRow)
                                        Ward = TheRow.getValue("WARDNO")
                                        # print("old_ward=",Ward)
                                        # if (Ward is None or len(Ward) == 0 or Ward == " " or Ward == "" or int(Ward) > 40):
                                        TheRow.setValue("WARDNO", int(x[0][0]))
                                        TheRows.updateRow(TheRow)
                                    # arcpy.CalculateField_management(parcelfile,"GRIDS1",sheet_code,"PYTHON")
                                    # arcpy.CalculateField_management(parcelfile,"WARDNO",int(x[0][0]),"PYTHON")
                                    allerror.write(filename + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + "\n")
                                except:
                                    exception_list.write("Attribute fill Error for ," + filename + "\n")
                                    allerror.write(
                                        filename + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + ",error" + "\n")

                            else:
                                print(filename + "," + " ")
                                allerror.write(filename + "," + " " + "\n")
                        # </editor-fold>

                    else:
                        print ("No scale in = " + filename)
                        allerror.write(filename + "," + " No Scale Field" + " " + "\n")

                    # arcpy.RemoveWorkspaceFromLockFileArea_management(parcelfile)
                    arcpy.CalculateField_management(parcelfile, "DISTRICT", 35, "PYTHON")  # FOR DISTRICT_CODE
                    if (vdc_code != '' and int(vdc_code)):
                        arcpy.CalculateField_management(parcelfile, "VDC", int(vdc_code), "PYTHON")  # FOR VDC_CODE

                    TheRows_3 = arcpy.UpdateCursor(parcelfile)
                    for TheParcelRow in TheRows_3:
                        parcel_no = TheParcelRow.getValue("PARCELNO")
                        OID = TheParcelRow.getValue("OBJECTID")
                        if (parcel_no is None):
                            TheParcelRow.setValue("PARCELNO", 0)
                            print("parceno set 0 at" + OID + " of " + filename + " \n")

                    try:
                        arcpy.Compact_management(os.path.join(root,filename))
                    except:
                        exception_list.write("Compact Error for ," + filename + "\n")
                        print("Compact error for " + filename)
        tkMessageBox.showinfo(title="Fill Ward No and Grid in freesheet" + version, message="Done")
        allerror.close()
        exception_list.close()


root = Tk()
root.title("Fill Ward No and Grid in freesheet" + version)
myapp = App(root)
myapp.mainloop()
