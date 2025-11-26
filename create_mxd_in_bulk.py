# -*- coding: utf-8 -*-
import os
import re
import arcpy
import Tkinter as tk
import tkFileDialog
import tkMessageBox

# Constants
MXD_TEMPLATE = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\Blank_Template.mxd"
GROUP_LAYER_PATH = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\Group.lyr"
PARCEL_LAYER_PATH = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\Parcel1.lyr"


def browse_input():
    directory = tkFileDialog.askdirectory()
    input_var.set(directory)


def validate_paths(workspace):
    if not os.path.exists(workspace):
        tkMessageBox.showerror("Error", "Invalid input workspace directory")
        return False
    if not all(os.path.exists(p) for p in [MXD_TEMPLATE, GROUP_LAYER_PATH, PARCEL_LAYER_PATH]):
        tkMessageBox.showerror("Error", "Template or layer files missing")
        return False
    return True


def find_folders_with_mdbs(root_folder):
    """Return list of folders that actually contain MDB files"""
    folders = []
    for root, dirs, files in os.walk(root_folder):
        if any(f.lower().endswith(".mdb") for f in files):
            folders.append(root)
    return folders


def find_mdbs(folder):
    """Find MDB files inside a specific folder"""
    return [os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(".mdb")]


def process_mdbs(mxd, df, mdb_list):
    ward_list = []

    for fc in mdb_list:
        arcpy.env.workspace = fc
        base_name = os.path.basename(fc).replace(" ", "")
        pattern = r"^.[A-Za-z][A-Za-z\s_-]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)"
        match = re.findall(pattern, base_name)
        if not match:
            continue

        ward, sheet = match[0][0], match[0][0] + match[0][1] + match[0][2]

        if ward not in ward_list:
            ward_list.append(ward)
            grp_lyr = arcpy.mapping.Layer(GROUP_LAYER_PATH)
            grp_lyr.name = ward
            arcpy.mapping.AddLayer(df, grp_lyr, "BOTTOM")

        subgrp = arcpy.mapping.Layer(GROUP_LAYER_PATH)
        subgrp.name = sheet

        g = arcpy.mapping.ListLayers(mxd, ward, df)
        if g:
            arcpy.mapping.AddLayerToGroup(df, g[0], subgrp, "BOTTOM")

        for feature in arcpy.ListFeatureClasses("*", "All"):
            target = arcpy.mapping.ListLayers(mxd, sheet, df)
            if target:
                new_layer = arcpy.mapping.Layer(os.path.join(fc, feature))
                if feature.lower() == "parcel":
                    arcpy.ApplySymbologyFromLayer_management(new_layer, PARCEL_LAYER_PATH)
                arcpy.mapping.AddLayerToGroup(df, target[0], new_layer, "BOTTOM")


def create_bulk_mxds():
    outer_folder = input_var.get()

    if not validate_paths(outer_folder):
        return

    output_folder = os.path.join(outer_folder, "_MXD_Output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # -------- NEW LOGIC: FIND ACTUAL FOLDERS CONTAINING MDBS --------
    folders = find_folders_with_mdbs(outer_folder)

    for folder in folders:
        mdb_list = find_mdbs(folder)
        if not mdb_list:
            continue

        # -------- Extract last + second-last folder names --------
        parts = folder.replace("\\", "/").split("/")
        if len(parts) >= 2:
            second_last = parts[-2]
            last = parts[-1]
            mxd_name = "{}_{}.mxd".format(second_last, last)
        else:
            mxd_name = last + ".mxd"

        output_mxd_path = os.path.join(output_folder, mxd_name)

        try:
            mxd = arcpy.mapping.MapDocument(MXD_TEMPLATE)
            df = arcpy.mapping.ListDataFrames(mxd)[0]

            process_mdbs(mxd, df, mdb_list)

            mxd.saveACopy(output_mxd_path)

        except Exception as e:
            tkMessageBox.showerror(
                "Error",
                "Failed to create MXD for {}\nError: {}".format(folder, str(e))
            )

    tkMessageBox.showinfo("Success", "MXDs created at:\n" + output_folder)


def setup_gui():
    root = tk.Tk()
    root.title("Bulk MXD Creator")

    global input_var
    input_var = tk.StringVar()

    f = tk.Frame(root, padx=20, pady=20)
    f.pack()

    tk.Label(f, text="Outer Folder:").grid(row=0, column=0, sticky="w")
    tk.Entry(f, textvariable=input_var, width=50).grid(row=0, column=1, padx=10)
    tk.Button(f, text="Browse", command=browse_input).grid(row=0, column=2)

    tk.Button(f, text="Generate Bulk MXDs",
              command=create_bulk_mxds,
              bg="#4CAF50", fg="white").grid(row=1, column=1, pady=20)

    return root


if __name__ == "__main__":
    app = setup_gui()
    app.mainloop()
