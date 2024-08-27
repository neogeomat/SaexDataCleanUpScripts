import os

import arcpy

import shared_data



def LoadDb(directory):
    if directory:
        shared_data.mdb_files = find_mdb_files(directory)
        shared_data.filtered_mdb_files=shared_data.mdb_files
        for mdb in shared_data.filtered_mdb_files:
            shared_data.initial_central_meridian = getCentralMeridian(mdb)
            break
        # Process the list of .mdb files
        shared_data.directory = directory
        print("Found .mdb files:", shared_data.mdb_files)
        # You can now pass this list to your database processing function
        # e.g., process_mdb_files(mdb_files)
    else:
        print("No directory selected.")


def find_mdb_files( directory):
    """Recursively find all .mdb files in the given directory"""
    mdb_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mdb'):
                mdb_files.append(os.path.join(root, file))
    return mdb_files


def getCentralMeridian(mdb):
    try:
        # Set the workspace once
        arcpy.env.workspace = mdb

        # List feature classes and get the first one
        feature_classes = arcpy.ListFeatureClasses()
        if not feature_classes:
            raise ValueError("No feature classes found in the MDB file.")

        # Get the spatial reference from the first feature class
        fc = feature_classes[0]
        desc = arcpy.Describe(fc)
        spatial_ref = desc.spatialReference

        # Return the central meridian
        return spatial_ref.centralMeridian

    except Exception as e:
        print("Error occurred:"+e)
        return None



