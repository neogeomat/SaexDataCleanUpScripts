# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# 17a1_merge_dummy_planning_spatial_join.py
# Created on: 2020-11-05 14:37:34.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy


# Local variables:
ParcelDissolve = "ParcelDissolve"
ParcelCentroid = "ParcelCentroid"
ParcelJoin_shp = "D:\\DataCleanTemp\\ParcelJoin.shp"

# Process: Spatial Join
arcpy.SpatialJoin_analysis(ParcelDissolve, ParcelCentroid, ParcelJoin_shp, "JOIN_ONE_TO_ONE", "KEEP_ALL", "PARCELNO \"PARCELNO\" true true false 10 Long 0 10 ,First,#,ParcelDissolve,PARCELNO,-1,-1;DISTRICT \"DISTRICT\" true true false 10 Long 0 10 ,First,#,ParcelDissolve,DISTRICT,-1,-1;VDC \"VDC\" true true false 10 Long 0 10 ,First,#,ParcelDissolve,VDC,-1,-1;WARDNO \"WARDNO\" true true false 3 Text 0 0 ,First,#,ParcelDissolve,WARDNO,-1,-1;GRIDS1 \"GRIDS1\" true true false 9 Text 0 0 ,First,#,ParcelDissolve,GRIDS1,-1,-1;PARCELKEY \"PARCELKEY\" true true false 23 Text 0 0 ,First,#,ParcelCentroid,PARCELKEY,-1,-1;PARCELTY \"PARCELTY\" true true false 10 Long 0 10 ,First,#,ParcelCentroid,PARCELTY,-1,-1;ParcelNote \"ParcelNote\" true true false 200 Text 0 0 ,First,#,ParcelCentroid,ParcelNote,-1,-1", "CONTAINS", "", "")

