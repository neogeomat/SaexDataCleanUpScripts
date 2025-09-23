# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import tkFileDialog
import arcpy
import os
import time

version = "v1.3.0 (Py2.7)"

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        # Input label
        Label(self, text="Select main folder:", width=30).grid(
            row=0, column=0, padx=5, pady=5, sticky=E+W
        )

        # Input entry
        self.input_entry = Entry(self, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky=E+W)

        # Browse button
        Button(self, text="Browse", command=self.browse_folder, width=15).grid(
            row=0, column=2, padx=5, pady=5, sticky=E+W
        )

        # Conversion type radio buttons
        self.conv_type = StringVar()
        self.conv_type.set("mdb2gdb")  # default

        Label(self, text="Select Conversion Type:", width=30).grid(
            row=1, column=0, padx=5, pady=5, sticky=E+W
        )
        Radiobutton(self, text="MDB → GDB", variable=self.conv_type, value="mdb2gdb").grid(
            row=1, column=1, sticky=W
        )
        Radiobutton(self, text="GDB → MDB", variable=self.conv_type, value="gdb2mdb").grid(
            row=2, column=1, sticky=W
        )

        # Process button
        Button(self, text="Process", command=self.run_conversion, width=30).grid(
            row=3, column=1, padx=5, pady=10, sticky=E+W
        )

    def browse_folder(self):
        """Open a folder selection dialog"""
        folder_selected = tkFileDialog.askdirectory(title="Select main folder")
        if folder_selected:
            self.input_entry.delete(0, END)
            self.input_entry.insert(0, folder_selected)

    def run_conversion(self):
        path = self.input_entry.get().strip()
        if not path or not os.path.exists(path):
            tkMessageBox.showerror("Error", "Invalid folder path!")
            return

        start_time = time.time()
        errors = []

        if self.conv_type.get() == "mdb2gdb":
            errors = self.convert_mdb_to_gdb(path)
        else:
            errors = self.convert_gdb_to_mdb(path)

        elapsed = round(time.time() - start_time, 2)
        msg = "Conversion completed!\nTime taken: {0} sec".format(elapsed)
        if errors:
            msg += "\nSome errors occurred. See exception_list_convert.csv"
        tkMessageBox.showinfo("Convert database " + version, msg)

    def convert_mdb_to_gdb(self, path):
        mdb_list = []
        errors = []
        exception_file = os.path.join(path, "exception_list_convert.csv")
        exception_list = open(exception_file, "a")

        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".mdb"):
                    mdb_list.append(os.path.join(root, filename))

        total = len(mdb_list)
        if total == 0:
            tkMessageBox.showinfo("Info", "No .mdb files found in this folder.")
            return []

        count = 0
        for mdb_path in mdb_list:
            count += 1
            output_gdb = mdb_path.replace(".mdb", ".gdb")
            try:
                if not arcpy.Exists(output_gdb):
                    arcpy.CreateFileGDB_management(
                        os.path.dirname(output_gdb),
                        os.path.basename(output_gdb)
                    )
                arcpy.env.workspace = mdb_path
                for fc in arcpy.ListFeatureClasses():
                    arcpy.FeatureClassToGeodatabase_conversion(fc, output_gdb)
                for tbl in arcpy.ListTables():
                    arcpy.TableToGeodatabase_conversion(tbl, output_gdb)
                print "[{0}/{1}] Converted MDB: {2}".format(count, total, mdb_path)
            except Exception as e:
                exception_list.write("MDB2GDB Error, {0}, {1}\n".format(mdb_path, str(e)))
                errors.append(mdb_path)
            self.update()

        exception_list.close()
        return errors

    def convert_gdb_to_mdb(self, path):
        gdb_list = []
        errors = []
        exception_file = os.path.join(path, "exception_list_convert.csv")
        exception_list = open(exception_file, "a")

        for root, dirs, files in os.walk(path):
            for d in dirs:
                if d.endswith(".gdb"):
                    gdb_list.append(os.path.join(root, d))

        total = len(gdb_list)
        if total == 0:
            tkMessageBox.showinfo("Info", "No .gdb folders found in this folder.")
            return []

        count = 0
        for gdb_path in gdb_list:
            count += 1
            output_mdb = gdb_path.replace(".gdb", ".mdb")
            try:
                if not arcpy.Exists(output_mdb):
                    arcpy.CreatePersonalGDB_management(
                        os.path.dirname(output_mdb),
                        os.path.basename(output_mdb)
                    )
                arcpy.env.workspace = gdb_path
                for fc in arcpy.ListFeatureClasses():
                    arcpy.FeatureClassToGeodatabase_conversion(fc, output_mdb)
                for tbl in arcpy.ListTables():
                    arcpy.TableToGeodatabase_conversion(tbl, output_mdb)
                print "[{0}/{1}] Converted GDB: {2}".format(count, total, gdb_path)
            except Exception as e:
                exception_list.write("GDB2MDB Error, {0}, {1}\n".format(gdb_path, str(e)))
                errors.append(gdb_path)
            self.update()

        exception_list.close()
        return errors


# ---------------- Run GUI ----------------
if __name__ == "__main__":
    root = Tk()
    root.title("MDB ↔ GDB Converter " + version)
    app = App(root)
    root.mainloop()
