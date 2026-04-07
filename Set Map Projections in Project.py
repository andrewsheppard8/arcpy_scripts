"""
===============================================================================
Script Name:       set_map_projection.py
Author:            Andrew Sheppard
Role:              GIS Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-04-07

Description:
-------------
This script sets the spatial reference for all maps in the current ArcGIS Pro project.

1. Connects to the currently open ArcGIS Pro project.
2. Iterates through all maps in the project.
3. Sets the spatial reference of each map to the user-specified coordinate system.
4. Provides messages for each map indicating the new projection.
===============================================================================
"""
import arcpy

def mapProjection(coord_system):
    aprx=arcpy.mp.ArcGISProject("CURRENT")
    for map_obj in aprx.listMaps():
       map_obj.spatialReference=coord_system
       arcpy.AddMessage(f"Projection set to {coord_system.name} for map: {map_obj.name}")
       
coord_system=arcpy.GetParameter(0)
mapProjection(coord_system)

