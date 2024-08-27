import tkMessageBox
import arcpy
import glob
from arcpy import env
import shared_data
def Fill_Par_FID(self,mdb):
    path = shared_data.directory
    env.workspace = i

    # Setting input and output
    inFeatures1 = ["Segments", "Parcel"]
    inFeatures2 = ["Construction", "Parcel"]
    intersectOutput1 = "Segments1"
    intersectOutput2 = "Construction1"

    if arcpy.Exists("Segments") and arcpy.Exists("Construction") and arcpy.Exists("Parcel"):
        # overwrite if feature exists
        arcpy.env.overwriteOutput = True
        # Intersect Parcel and segment
        a1 = arcpy.Intersect_analysis(inFeatures1, intersectOutput1, "", "", "line")
        a2 = arcpy.Intersect_analysis(inFeatures2, intersectOutput2, "", "", "")
        # calculating ParFID
        b1 = arcpy.CalculateField_management(intersectOutput1, "ParFID", "!FID_Parcel!", "PYTHON_9.3")
        b2 = arcpy.CalculateField_management(intersectOutput2, "ParFID", "!FID_Parcel!", "PYTHON_9.3")

        # Execute DeleteField
        dropFields1 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote",
                       "FID_Segments", "FID_Parcel"]
        dropFields2 = ["PARCELKEY", "PARCELNO", "DISTRICT", "VDC", "WARDNO", "GRIDS1", "PARCELTY", "ParcelNote",
                       "FID_Construction", "FID_Parcel"]

        arcpy.DeleteField_management(b1, dropFields1)
        arcpy.DeleteField_management(b2, dropFields2)

        # Delete FeatureClass
        arcpy.Delete_management("Segments")
        arcpy.Delete_management("Construction")

        # Rename Feature Class
        arcpy.Rename_management("Segments1", "Segments")
        arcpy.Rename_management("Construction1", "Construction")

    else:
        tkMessageBox.showerror(title="Error", message="Feature Class Missing. Please check")




