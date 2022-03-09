from Tkinter import *

version = "v1.0.1"

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
        self.button4 = Button(self, text="Process", command=self.createMPfield, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process:Input the folder location 
Output: motherparceled Database.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def createMPfield(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        import time
        startTime = time.time ()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_motherparcel.csv","a")
        count = 0
        matches=["file"]
        for root, dirnames, filenames in os.walk(path):
            if any(x in root.lower() for x in matches):
                [dirnames.remove(d) for d in dirnames if not any(x in os.path.join(root,d).lower() for x in matches)] # To only use files if they contain "file" in absolute path
                for filename in filenames:
                    if filename.endswith('.mdb'):
                        mdb_list.append(os.path.join(root, filename))
                        total_mdbs = len(mdb_list)

        for i in mdb_list:

            count +=1
            try:                
                if arcpy.Exists(i+"\\Parcel"):
                    if arcpy.ListFields(i+"\\Parcel", "mother_parcel"):
                        print("mother_parcel field already exists")
                    else:
                        arcpy.management.AddField(i+"\\Parcel", "mother_parcel","TEXT")
                        print("Field Added")
                else:
                    print("Parcel Layer not found for, "+i)                
            except:
                exception_list.write("motherparcel Error for ," + i + "\n")
                print("motherparcel error for "+i)
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print(" motherparcel process complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="motherparcel database" + version, message="Done")
root = Tk()
root.title("motherparcel database " + version)
myapp = App(root)
myapp.mainloop()
