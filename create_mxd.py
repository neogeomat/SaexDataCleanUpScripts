import os
import re
import arcpy
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import subprocess

# Constants
MXD_TEMPLATE = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\Blank_Template.mxd"
GROUP_LAYER_PATH = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\Group.lyr"
PARCEL_LAYER_PATH = r"D:\LIS_SYSTEM\LIS_Spatial_Data_Templates\Parcel.lyr"
ARCMAP_EXE_PATH = r"C:\Program Files (x86)\ArcGIS\Desktop10.8\bin\ArcMap.exe"


def browse_input():
    """Browse for input workspace directory"""
    directory = tkFileDialog.askdirectory()
    input_var.set(directory)


def browse_output():
    """Browse for output MXD file location"""
    file_selected = tkFileDialog.asksaveasfilename(
        defaultextension=".mxd",
        filetypes=[("MXD files", "*.mxd")]
    )
    output_var.set(file_selected)


def validate_paths(workspace, output_path):
    """Validate input and output paths"""
    if not os.path.exists(workspace):
        tkMessageBox.showerror("Error", "Invalid input workspace directory")
        return False

    if not output_path:
        tkMessageBox.showerror("Error", "Please select an output MXD path")
        return False

    if not all(os.path.exists(p) for p in [MXD_TEMPLATE, GROUP_LAYER_PATH, PARCEL_LAYER_PATH]):
        tkMessageBox.showerror("Error", "Template files missing")
        return False

    return True


def process_mdbs(mxd, df, workspace):
    """Process MDB files and create layer structure"""
    mdb_list = [
        os.path.join(root, filename)
        for root, _, filenames in os.walk(workspace)
        for filename in filenames
        if filename.endswith('.mdb')
    ]

    if not mdb_list:
        tkMessageBox.showerror("Error", "No MDB files found in workspace")
        return None

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

        sub_grp_lyr = arcpy.mapping.Layer(GROUP_LAYER_PATH)
        sub_grp_lyr.name = sheet
        target_group = arcpy.mapping.ListLayers(mxd, ward, df)

        if target_group:
            arcpy.mapping.AddLayerToGroup(df, target_group[0], sub_grp_lyr, "BOTTOM")

        for feature in arcpy.ListFeatureClasses("*", "All"):
            target_subgroup = arcpy.mapping.ListLayers(mxd, sheet, df)
            if target_subgroup:
                fc_path = os.path.join(arcpy.env.workspace, feature)
                new_layer = arcpy.mapping.Layer(fc_path)
                arcpy.mapping.AddLayerToGroup(df, target_subgroup[0], new_layer, "BOTTOM")

    return mxd


def create_mxd():
    """Main function to create MXD file"""
    env_workspace = input_var.get()
    output_mxd_path = output_var.get()

    if not validate_paths(env_workspace, output_mxd_path):
        return

    try:
        mxd = arcpy.mapping.MapDocument(MXD_TEMPLATE)
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        mxd.activeView = df.name

        processed_mxd = process_mdbs(mxd, df, env_workspace)
        if processed_mxd:
            processed_mxd.saveACopy(output_mxd_path)
            tkMessageBox.showinfo(
                "Success",
                "MXD created successfully at:\n{}".format(output_mxd_path)
            )  # Fixed closing parenthesis here
            #subprocess.call([ARCMAP_EXE_PATH, output_mxd_path])

    except Exception as e:
        tkMessageBox.showerror("Error", "Failed to create MXD: {}".format(str(e)))
    finally:
        if 'mxd' in locals():
            del mxd


# ... (keep all other imports and constants unchanged)

def setup_gui():
    """Initialize GUI components"""
    root = tk.Tk()
    root.title("MXD Creator Tool")

    # Initialize StringVars AFTER creating root
    global input_var, output_var
    input_var = tk.StringVar()
    output_var = tk.StringVar()

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack()

    # Input Workspace
    tk.Label(main_frame, text="Input Workspace:").grid(row=0, column=0, sticky='w', pady=5)
    tk.Entry(main_frame, textvariable=input_var, width=50).grid(row=0, column=1, padx=10)
    tk.Button(main_frame, text="Browse", command=browse_input).grid(row=0, column=2)

    # Output MXD
    tk.Label(main_frame, text="Output MXD:").grid(row=1, column=0, sticky='w', pady=5)
    tk.Entry(main_frame, textvariable=output_var, width=50).grid(row=1, column=1, padx=10)
    tk.Button(main_frame, text="Browse", command=browse_output).grid(row=1, column=2)

    # Create Button
    tk.Button(
        main_frame,
        text="Generate MXD",
        command=create_mxd,
        bg="#4CAF50",
        fg="white"
    ).grid(row=2, column=1, pady=15)

    return root


if __name__ == "__main__":
    app = setup_gui()
    app.mainloop()
