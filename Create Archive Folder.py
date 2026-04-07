"""
===============================================================================
Script Name:       archive_geodatabases.py
Author:            Andrew Sheppard
Role:              GIS Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-04-07

Description:
-------------
This script automates the archiving of geodatabases within a workspace. It:

1. Deletes any existing Archive folders to avoid duplication.
2. Creates a new Archive folder with the current date.
3. Copies specified geodatabases (Basemap, Misc, Students, Students_YYYYMMDD)
   into the new Archive folder.
4. Handles file locks and provides user-friendly messages for troubleshooting.
===============================================================================
"""
import shutil
import os
from datetime import datetime
def Archive(gdb_source):
    root_folder=gdb_source
    gdb_folder=os.path.join(root_folder,"GDB")
    current_date = datetime.now().strftime("%d%b%Y")
    new_folder_name = f"Archive_{current_date}"
    destination_folder = os.path.join(gdb_folder, new_folder_name)
    for item in os.listdir(gdb_folder):
        if "Archive" in item:
            archive_folder_path=os.path.join(gdb_folder,item)
            try:
                shutil.rmtree(archive_folder_path)
                arcpy.AddMessage(f"Deleted existing Archive folder: {item}")
            except Exception as e:
                arcpy.AddMessage(f"Error deleting folder {item}: {e}")
    arcpy.AddMessage(f"Created new Archive folder: {new_folder_name}")
    geodatabases_to_copy = ["Basemap", "Misc", "Students","Students_YYYYMMDD"]
    for gdb_name in geodatabases_to_copy:
        source_gdb_path = os.path.join(gdb_folder, f"{gdb_name}.gdb")
        if os.path.exists(source_gdb_path):
            destination_gdb_path = os.path.join(destination_folder, f"{gdb_name}.gdb")
            try:
                shutil.copytree(source_gdb_path, destination_gdb_path)
                arcpy.AddMessage(f"Copied {gdb_name}.gdb to {new_folder_name}")
            except Exception as e:
                if "rd.lock" or "rs.lock" in str(e):
                    arcpy.AddError(f"Cannot create {gdb_name}.gdb because it is locked.")
                    arcpy.AddError(f"Save all edits, save the project, and try again.")
                    arcpy.AddError("If that didn't work, remove the fc from the map and try again.")
                    arcpy.AddError("If that didn't work, save/close the project, reopen, and try again.")
                else:
                    arcpy.AddError(f"Error copying {gdb_name}.gdb: {e}")
gdb_source=arcpy.GetParameterAsText(0)
Archive(gdb_source)

