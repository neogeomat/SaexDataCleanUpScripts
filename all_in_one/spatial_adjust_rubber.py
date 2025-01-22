import Tkinter as tk
import tkFileDialog as filedialog
import tkMessageBox as messagebox
import arcpy
import sheet_to_coordinate
from LoadDb import getSpatialRef
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from scipy.interpolate import Rbf

def get_extreme_corners(parcel_layer):
    # Recalculate extent before getting the corners
    recalculate_extent(parcel_layer)

    desc = arcpy.Describe(parcel_layer)
    extent = desc.extent
    top_left = (extent.XMin, extent.YMax)
    top_right = (extent.XMax, extent.YMax)
    bottom_left = (extent.XMin, extent.YMin)
    bottom_right = (extent.XMax, extent.YMin)
    return [top_left, top_right, bottom_left, bottom_right]

def get_target_coordinates(mapsheet_number):
    try:
        top_left, bottom_left, top_right, bottom_right, scale = sheet_to_coordinate.get_corners(mapsheet_number)
        return [top_left, top_right, bottom_left, bottom_right]
    except ValueError as e:
        messagebox.showerror("Error", "Error getting coordinates: %s" % e)
        return None

def recalculate_extent(parcel_layer):
    # Recalculate the extent of the parcel layer
    arcpy.RecalculateFeatureClassExtent_management(parcel_layer)

def rubber_sheet_adjustment(parcel_layer, mapsheet_number,spatial_ref):

    output_layer = "adjusted_parcel_layer"

    # Get the original and target corner points
    source_points  = get_extreme_corners(parcel_layer)
    destination_points  = get_target_coordinates(mapsheet_number)

    workspace = r"D:\test_sa"

    # Create a new feature class for source points
    arcpy.CreateFeatureclass_management(workspace, "source_points.shp", "POINT")
    arcpy.CreateFeatureclass_management(workspace, "destination_points.shp", "POINT")

    # Populate source points
    with arcpy.da.InsertCursor(workspace+"/source_points.shp", ["SHAPE@XY"]) as cursor:
        for point in source_points:
            cursor.insertRow([point])

    # Populate destination points
    with arcpy.da.InsertCursor(workspace+"/destination_points.shp", ["SHAPE@XY"]) as cursor:
        for point in destination_points:
            cursor.insertRow([point])
    print("Source and destination points created.")
    arcpy.edit.SpatialAdjustment()

def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("MDB files", "*.mdb")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def create_control_points_feature_class(control_points, output_fc,spatial_ref):
    try:
        # Check if the feature class already exists and delete it if it does
        if arcpy.Exists(output_fc):
            arcpy.Delete_management(output_fc)

        # Create a new feature class for control points
        arcpy.CreateFeatureclass_management("D:/test_sa", "output_fc.shp", "POINT", spatial_reference=spatial_ref)

        # Add fields for source and destination coordinates
        arcpy.AddField_management("D:/test_sa/output_fc.shp", "SRC_X", "DOUBLE")
        arcpy.AddField_management("D:/test_sa/output_fc.shp", "SRC_Y", "DOUBLE")
        arcpy.AddField_management("D:/test_sa/output_fc.shp", "DST_X", "DOUBLE")
        arcpy.AddField_management("D:/test_sa/output_fc.shp", "DST_Y", "DOUBLE")

        # Insert control points into the feature class
        with arcpy.da.InsertCursor("D:/test_sa/output_fc.shp", ["SHAPE@XY", "SRC_X", "SRC_Y", "DST_X", "DST_Y"]) as cursor:
            for src, dst in control_points:
                cursor.insertRow([(src[0], src[1]), src[0], src[1], dst[0], dst[1]])

    except arcpy.ExecuteError as e:
        print("Error creating control points feature class: ", e)
        raise
    except Exception as e:
        print("Unexpected error: ", e)
        raise

def rubbersheet_adjustment(input_fc, output_fc, control_points,spatial_ref):
    # Create control points feature class
    try:

        control_points_fc = "in_memory/control_points"
        print("Control Points: ", control_points)
        print("Output Feature Class: ", output_fc)
        create_control_points_feature_class(control_points, control_points_fc,spatial_ref)

        # Perform rubbersheet adjustment
        arcpy.RubbersheetFeatures_edit(input_fc, control_points_fc, output_fc)
        print("Rubbersheet adjustment completed successfully.")
    except arcpy.ExecuteError as e:
        print("Error during rubbersheet adjustment: "+e)
        raise

def perform_adjustment():
    mdb= file_entry.get()
    parcel_layer = mdb + "\\Parcel"

    spatial_ref = getSpatialRef(mdb)
    mapsheet_number = mapsheet_entry.get()

    if not parcel_layer or not mapsheet_number:
        messagebox.showwarning("Input Error", "Please enter the mapsheet number and choose an MDB file.")
        return

    adjusted_layer = rubber_sheet_adjustment(parcel_layer, mapsheet_number,spatial_ref)
    if adjusted_layer:
        messagebox.showinfo("Success", "Adjusted layer created: %s" % adjusted_layer)
    else:
        messagebox.showerror("Failure", "Adjustment failed.")

# Create the main window
root = tk.Tk()
root.title("Spatial Adjustment Tool")

# Create and place widgets
tk.Label(root, text="Mapsheet Number:").grid(row=0, column=0, padx=10, pady=10)
mapsheet_entry = tk.Entry(root)
mapsheet_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="MDB File:").grid(row=1, column=0, padx=10, pady=10)
file_entry = tk.Entry(root)
file_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=choose_file).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="Perform Adjustment", command=perform_adjustment).grid(row=2, column=0, columnspan=3, pady=20)

# Run the Tkinter event loop
root.mainloop()
