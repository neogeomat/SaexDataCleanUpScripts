from Tkinter import *

version = "v2.2.2"
dic_case_sen={
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
    "sa": "32",
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
    "ksha":"34",
    "kshya": "34",
    "tra": "35",
    "gya": "36"
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

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.attributeChecker, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process: 
Output: .csv file containing the error for each mdb file in the same location. The error in the mdb should be corrected manually.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def attributeChecker(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        from arcpy import env
        import re
        path = self.sheetentry1.get()
        mdb_list = []
        allerror = open (path + "\\regex.csv", "a")
        allerror.truncate (0)
        for root, dirnames, filenames in os.walk(path):
            for dirname in dirnames:
                print dirname
                if (os.path.join(root,dirname).lower().find('file') != -1):
                    allerror.write(os.path.join(root,dirname) + ",error, name contains file, check if filemap or not" +"\n")
                else:
                    print os.path.join(root,dirname)
                    for filename in filenames:
                        if filename.endswith('.mdb'):
                            mdb_list.append(os.path.join(root, filename))
                            parcelfile=os.path.join(root, filename,"Parcel")
                            print (parcelfile)
                            new_filename = filename.replace(" ", "")
                            x = re.findall ("^...[A-Za-z\s_]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
                            print(x)
                            if x:
                                print(filename+","+x[0][0]+x[0][1]+x[0][2])
                                bad_chars = ['_', '-', '(', ")"," "]
                                new_string_name = ''.join(i for i in x[0][1] if not i in bad_chars)
                                if(new_string_name) in dic_case_sen:
                                    dic_code=dic_case_sen[new_string_name]
                                else:
                                    dic_code=dic_case_insen[new_string_name.lower()]
                                new_string_no = x[0][2]
                                if new_string_no=="":
                                    new_string_no="0"
                                try:
                                    print("code=5555" + x[0][0].zfill(2) + dic_code + new_string_no)
                                    sheet_code="5555" + x[0][0].zfill(2) + dic_code + new_string_no
                                    arcpy.CalculateField_management(parcelfile,"GRIDS1",sheet_code,"PYTHON")
                                    arcpy.CalculateField_management(parcelfile,"WARDNO",int(x[0][0]),"PYTHON")
                                    allerror.write(filename + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + "\n")
                                except:
                                    allerror.write(filename + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + ",error" +"\n")

                            else:
                                print(filename + "," + " ")
                                allerror.write (filename + "," + " " + "\n")
        tkMessageBox.showinfo(title="Fix Attribute Errors" + version, message="Done")
        allerror.close()


root = Tk()
root.title("Fix Attribute Errors " + version)
myapp = App(root)
myapp.mainloop()
