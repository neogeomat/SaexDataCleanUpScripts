from Tkinter import *

version = "v2.1.1"

class App(Frame):
    global version
    ka_kha_ga={"":"00",

               "ka":"01",
               "k":"01",

               "kha":"02",
               "kh":"02",
               
               "ga":"03",
               "gha":"04",
               "nga":"05",
               "cha":"06",
               "chha":"07",
               "ja":"08",
               "jha":"09",
               "yna":"10",
               "Ta":"11",
               "Tha":"12",
               "Da":"13",
               "Dha":"14",
               "ana":"15",
               "ta":"16",
               "tha":"17",
               "da":"18",
               "dha":"19",
               "na":"20",
               "pa":"21",
               "fa":"22",
               "ba":"23",
               "bha":"24",
               "ma":"25",
               "ya":"26",
               "ra":"27",
               "la":"28",
               "wa":"29",
               "sha":"30",
               "SHA":"31",
               "sa":"32",
               "ha":"33",
               "kshya":"34",
               "tra":"35",
               "gya":"36"
               }
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
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    new_filename = filename.replace(" ", "")
                    x = re.findall ("^[A-Za-z\s_]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
                    print(x)
                    if x:
                        print(filename+","+x[0][0]+x[0][1]+x[0][2])
                        allerror.write (filename+","+x[0][0]+","+x[0][1]+","+x[0][2]+"\n")
                    else:
                        print(filename + "," + " ")
                        allerror.write (filename + "," + " " + "\n")
        tkMessageBox.showinfo(title="Fix Attribute Errors" + version, message="Done")
        allerror.close()


root = Tk()
root.title("Fix Attribute Errors " + version)
myapp = App(root)
myapp.mainloop()
