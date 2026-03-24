"""
===============================================================================
Script Name:       Clean Fields in Geocode Feature Class
Author:            Andrew Sheppard
Role:              GIS Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-03-24

Description:
-------------

The goal of this tool is to clean up the fields in a geocoded feature class for
ease of use. It will first remove all unneccessary fields but also rename pre-existing
fields to be used for future analysis.

1. Cleans excess fields from a geocode, based on fields that are created during a geocode process
2. Rename fields based on specific conditions
===============================================================================
"""
import arcpy
import tkinter as tk
from tkinter import messagebox

def show_confirmation_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    root.wm_attributes("-topmost",1)
##    root.update()
##    root.deiconify()
##    root.focus_force()
    response = messagebox.askokcancel("Confirm", "Is the geocode fully complete? If not, do not run this tool. Only run this tool after the geocoding process if fully completed.",parent=root)
    root.destroy()
    return response

def CleanFields(output_fc):
    confirmed = show_confirmation_dialog()
    if not confirmed:
        arcpy.AddMessage("Tool execution cancelled by user.")
        return
    fields_to_del = []
    field_List = [field.name for field in arcpy.ListFields(output_fc)]
    for field_name in field_List:
        if field_name in ['Match_type','Longlabel','ShortLabel',
                      'Addr_type','Type','PlaceName','Place_addr','Phone','URL',
                      'Rank','AddBldg','AddNum','AddNumFrom','AddNumTo','AddRange',
                      'Side','StPreDir','StPreType','StName','StType','StDir','BldgType',
                      'BldgName','LevelType','LevelName','UnitType','UnitName','SubAddr',
                      'Block','Sector','Nbrhd','District','City','MetroArea','Subregion',
                      'Region','RegionAbbr','Territory','Zone','Postal','PostalExt',
                      'Country','CntryName','LangCode','Distance','X','Y','DisplayX',
                      'DisplayY','Xmin','Xmax','Ymin','Ymax','ExInfo','IN_Address2',
                      'IN_Address3','IN_Neighborhood','IN_City','IN_Subregion','IN_Region',
                      'IN_Postal','IN_PostalExt','IN_CountryCode','USER_AddNum','USER_StPreDir','USER_StPreType',
                          'USER_StName','USER_StType','USER_StDir','USER_UnitType','USER_UnitName','USER_UnitName',
                          'USER_BuildingType','USER_BuildingUnit','USER_LevelType','USER_LevelName']:
            fields_to_del.append(field_name)
            arcpy.AddMessage(f'{field_name} will be deleted')
    fields_to_delete=[field for field in field_List if field in fields_to_del]
    fields_to_delete_str = ";".join(fields_to_delete)
    for field in fields_to_delete:
        arcpy.DeleteField_management(output_fc, fields_to_delete_str)
        arcpy.AddMessage(f'{field} deleted')
    fields=arcpy.ListFields(output_fc)
    user_status_found=False
    user_stutype_found=False
    for field in fields:
        if field.name.lower()=="user_status".lower():
            status_name=field.name.replace("USER_Status","Status1")
            arcpy.AlterField_management(output_fc,field.name,status_name)
            arcpy.AddMessage(f'{field.name} renamed to {status_name}')
            user_status_found=True
        if field.name.lower()=="user_stutype".lower():
            stutype_name=field.name.replace("user_stutype".lower(),"Stutype1")
            new_alias="Stutype1"
            arcpy.AlterField_management(output_fc,field.name,stutype_name,new_alias)
            arcpy.AddMessage(f'{field.name} renamed to {stutype_name}')
            user_stutype_found=True
        elif field.name.startswith("USER_"):
            new_name=field.name.replace("USER_","")
            arcpy.AlterField_management(output_fc, field.name, new_name)
            arcpy.AddMessage(f'{field.name} renamed to {new_name}')
    arcpy.AddMessage('Geocode fields removed')
if __name__=="__main__":
    
    output_fc=arcpy.GetParameterAsText(0)
    CleanFields(output_fc)
