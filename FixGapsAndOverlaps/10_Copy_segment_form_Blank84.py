# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# 10_Copy_segment_form_Blank84.py
# Created on: 2020-10-08 10:44:27.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy


# Local variables:
Segments__3_ = "D:\\LIS_SYSTEM\\LIS_Spatial_Data_Templates\\BLANK84.mdb\\Segments"
Segments__4_ = "C:\\Users\\DELL\\Desktop\\Coverage_Create\\102-1139-22.mdb\\Segments"

# Process: Copy Features
arcpy.CopyFeatures_management(Segments__3_, Segments__4_, "", "0", "0", "0")
