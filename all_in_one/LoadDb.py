import os
import shared_data

def LoadDb(directory):
    if directory:
        shared_data.mdb_files = find_mdb_files(directory)
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
