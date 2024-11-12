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
        self.button4 = Button(self, text="Process", command=self.compactDB, width=30)
        self.button4.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process:Input the folder location 
Output: Mdb to GDb Database.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=3, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def compactDB(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        import time
        startTime = time.time ()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_convert.csv","a")
        count = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))
                    total_mdbs = len(mdb_list)

        for i in mdb_list:

            output_gdb = i.replace(".mdb", ".gdb")
            # Create the output GDB if it doesn't exist
            try:
                if not arcpy.Exists(output_gdb):
                    arcpy.CreateFileGDB_management(os.path.dirname(output_gdb), os.path.basename(output_gdb))
                    # List all feature classes in the MDB
                arcpy.env.workspace = i
                feature_classes = arcpy.ListFeatureClasses()

                # Convert each feature class to the new GDB
                for feature_class in feature_classes:
                    arcpy.FeatureClassToGeodatabase_conversion(feature_class, output_gdb)

                # Convert tables if needed
                tables = arcpy.ListTables()
                for table in tables:
                    arcpy.TableToGeodatabase_conversion(table, output_gdb)

            except:
                exception_list.write("Convert Error for ," + i + "\n")
                print("Convert error for "+i)
            print (i + " (" + str(count) + "/" + str(total_mdbs) + ")")
        print(" Convert process complete")
        exception_list.close()
        print ('The script took {0} second !'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="Convert database to GDb" + version, message="Done")
root = Tk()
root.title("Convert database " + version)
myapp = App(root)
myapp.mainloop()
