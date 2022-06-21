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

        # create label for District
        self.Sheet = Label(self, text="Enter X_Shift", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.XShift = Entry(self, width=30)
        self.XShift.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create label for VDC
        self.Sheet = Label(self, text="Enter Y_Shift", width=30)
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.YShift = Entry(self, width=30)
        self.YShift.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.moveData, width=30)
        self.button4.grid(row=4, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=5, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process:Input the folder location 
Output: Move Layer by Input Distance Database.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=6, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def moveData(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        import time
        startTime = time.time()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list = open(path+"\\exception_list_move_data.csv","a")
        count = 0

        xOffset = float(self.XShift.get())
        yOffset = float(self.YShift.get())

        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)

        for i in mdb_list:
            try:
                count +=1
                arcpy.env.workspace = i
                fcl = arcpy.ListFeatureClasses("*","ALL")
                for fc in fcl:
                    with arcpy.da.UpdateCursor(fc, ["SHAPE@XY"]) as cursor:
                        for row in cursor:
                            cursor.updateRow([[row[0][0] + xOffset, row[0][1] + yOffset]])
            except Exception as e:
                exception_list.write("Move Error for ," + i + "\n")
                print("Move error for "+i)
                print(e)
        print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print(" Move process complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="move database" + version, message="Done")
root = Tk()
root.title("Move database " + version)
myapp = App(root)
myapp.mainloop()
