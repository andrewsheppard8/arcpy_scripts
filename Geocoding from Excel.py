"""
===============================================================================
Script Name:       Geocoding from Excel
Author:            Andrew Sheppard
Role:              GIS Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-03-23

Description:
-------------
From an Excel file (.xlsx):
1. Add a new field for the address, copying over addresses, cleaning to improve geocoding potential
2. Creating table in ArcGIS Pro
3. Geocode
4. Enable Editor Tracking
5. Get some statistics
6. Create a map to display the new geocode
7. Symbolize two feature classes, points and polygons
8. Delete unnecessary table in ArcGIS Pro


===============================================================================
"""

import arcpy
import pandas as pd
from arcpy import env
import tkinter as tk
from tkinter import messagebox

#Step 1
def CleanExcel(excel_path,add_field):
    root=tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost",1)
    # Make sure the pop-up is centered on the screen
    root.update_idletasks()  # Update geometry info
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 300
    window_height = 100
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_down}')
    messagebox.showwarning('Excel File','Make sure the Excel file is closed before running this tool',parent=root)
    root.destroy()
    try:
        arcpy.AddWarning("Please ensure that the Excel file is closed before running this tool.")

        try:
            df = pd.read_excel(excel_path)
            arcpy.AddMessage('Excel file read successfully')
        except PermissionError:
            arcpy.AddError("Excel file is still open. Close it and restart the tool.")
            return
        except Exception as e:
            arcpy.AddError(f"An unexpected error occurred while reading the file: {str(e)}")
            return
        
        address_field=df[add_field]
        df['DDP_Address']=address_field
        arcpy.AddMessage(f'DDP_Address field added, copied values from {add_field}')
        df['DDP_Address']=df['DDP_Address'].str.replace('1/2','',regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace('[,:/_.]', '', regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace(' Unit',' #Unit',regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace(' Apt',' #Apt', regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace(' Spc',' #Spc', regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace('##',"#", regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace('  ',' ', regex=True)
        df['DDP_Address']=df['DDP_Address'].str.replace('   ',' ', regex=True)
        df.to_excel(excel_path, index=False)
        arcpy.AddMessage('Excel file cleaned')

    except Exception as e:
        arcpy.AddError(f"An unexpected error occurred: {str(e)}")
        
#Step 2
def CreateTable(excel_path,students_path,student_fc):
    arcpy.env.workspace=students_path
    table=f"TABLE_{student_fc}"
    arcpy.conversion.ExcelToTable(excel_path,table)
    arcpy.AddMessage(f'Excel turned into ArcGIS Table')

#Step 3 
def Geocode(students_path,student_fc,locator,zip_field):
    arcpy.env.workspace=students_path
    table=f"TABLE_{student_fc}"
    zip_field = zip_field.replace(' ', '_')
    arcpy.AddMessage(zip_field)
    field_mapping = (
        "\'Address or Place\' DDP_Address VISIBLE NONE;Address2 <None> VISIBLE NONE;Address3 <None> VISIBLE NONE;"
        "Neighborhood <None> VISIBLE NONE;City <None> VISIBLE NONE;Subregion <None> VISIBLE NONE;"
        f"Region <None> VISIBLE NONE;\'ZIP\' {zip_field} VISIBLE NONE;ZIP4 <None> VISIBLE NONE;"
        "Country <None> VISIBLE NONE"
    )
    arcpy.AddMessage("Geocoding with the following field mapping:")
    arcpy.AddMessage(field_mapping)
    
    arcpy.GeocodeAddresses_geocoding(
        in_table=table,
        address_locator=locator,
        in_address_fields=field_mapping,
        out_feature_class=student_fc,
        out_relationship_type="STATIC"
    )
    arcpy.AddMessage('Geocode complete')

#Step 4
def EditorTracking(students_path,student_fc):
    arcpy.env.workspace=students_path
    arcpy.management.EnableEditorTracking(student_fc,"Creator","Created",
                                          "Editor","Edited","ADD_FIELDS","UTC")
    arcpy.AddMessage("Editor tracking enabled for geocode")

#Step 5
#Looking at statistics, match count for the geocode based on Status field created during geocoding
def TOTAL(students_path,student_fc):
    arcpy.env.workspace=students_path
    total_count=int(arcpy.GetCount_management(student_fc).getOutput(0))
    arcpy.AddMessage(f'Total number of features: {total_count}')
    query="Status = 'M'"
    output_status=arcpy.management.SelectLayerByAttribute(student_fc, "NEW_SELECTION", query)
    status_count = int(arcpy.GetCount_management(output_status).getOutput(0))
    arcpy.AddMessage(f'Number of matched features: {status_count}')
    percent_value=round(((status_count/total_count)*100),2)
    percent_x=f'Percent match rate for geocode: {percent_value}%'
    if percent_value >=94:
        percent_x += "\n\n                Match Rate OK!"
    else:
        arcpy.AddError("script stopped. Match rate too low.")
        percent_x += "\n\nMatch Rate low, please review student data and try again."
##        #Punishment initiated
##        arcpy.Delete_management(student_fc)
##        arcpy.AddMessage(f"{student_fc} has been deleted due to low match rate.")
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.wm_attributes("-topmost",1)
        messagebox.showerror('Match Rate', percent_x,parent=root)  # Use showwarning to indicate an issue
        root.destroy()
        
        sys.exit('The match rate is below 94%. Script execution stopped.')  # Stop the script
    #PERCENT POPUP
    root=tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost",1)
    # Make sure the pop-up is centered on the screen
    root.update_idletasks()  # Update geometry info
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 300
    window_height = 100
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    
    # Set the geometry and make sure it appears in the center
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_down}')
    messagebox.showinfo('Match Rate',percent_x,parent=root)
    root.destroy()

#Adding additional fields based on organization needs
def AddFields(students_path,student_fc):
    arcpy.env.workspace=students_path
    field_infos = [
        ('RESIDENT', 'TEXT', 1),
        ('STUTYPE', 'TEXT', 2),
        ('GRD', 'SHORT', None),
        ('SCHL_CODE', 'SHORT', None),
        ('SCHL_NAME', 'TEXT', None)
        #('STU_ID', 'SHORT', None)
        ]
    existing_fields = [field.name for field in arcpy.ListFields(student_fc)]
    for field_name, field_type, field_length in field_infos:
        if field_name not in existing_fields:
            arcpy.AddField_management(student_fc, field_name, field_type, field_length=field_length)
            arcpy.AddMessage(f"Added new field: {field_name}")
        else:
            arcpy.AddMessage(f'{field_name} already exists. Not added to feature class')
            
def SpatialJoin_Y(students_path,student_fc,district):
    arcpy.env.workspace=students_path
    in_district=arcpy.SelectLayerByLocation_management(student_fc, "WITHIN", district, "", "NEW_SELECTION")
    arcpy.CalculateField_management(in_district,"RESIDENT", "'Y'")
    
    arcpy.SelectLayerByAttribute_management(student_fc, "CLEAR_SELECTION")
    
def SpatialJoin_N(students_path,student_fc,district):
    arcpy.env.workspace=students_path
    out_district=arcpy.SelectLayerByLocation_management(student_fc, "WITHIN", district, "", "NEW_SELECTION", "INVERT")
    query_M="Status = 'M'"
    status_M=arcpy.management.SelectLayerByAttribute(out_district,"SUBSET_SELECTION",query_M)
    arcpy.CalculateField_management(status_M,"RESIDENT", "'N'")
    arcpy.SelectLayerByAttribute_management(student_fc, "CLEAR_SELECTION")
    
def Resident(students_path,student_fc):
    arcpy.env.workspace=students_path
    query_Y="RESIDENT = 'Y'"
    resident=arcpy.management.SelectLayerByAttribute(student_fc,"NEW_SELECTION",query_Y)
    total_resident=int(arcpy.GetCount_management(resident).getOutput(0))
    arcpy.AddMessage(f'Total number of students where RESIDENT = Y: {total_resident}')
    query_N="RESIDENT = 'N'"
    nonresident=arcpy.management.SelectLayerByAttribute(student_fc,"NEW_SELECTION",query_N)
    total_nonresident=int(arcpy.GetCount_management(nonresident).getOutput(0))
    arcpy.AddMessage(f'Total number of students where RESIDENT = N: {total_nonresident}')
    query_NULL="RESIDENT IS NULL"
    select_NULL=arcpy.management.SelectLayerByAttribute(student_fc,"NEW_SELECTION",query_NULL)
    total_NULL=int(arcpy.GetCount_management(select_NULL).getOutput(0))
    arcpy.AddMessage(f'Total number of students where RESIDENT is NULL: {total_NULL}')

#Step 6
def ensure_map_exists(students_path,student_fc,map_name):
    aprx_path='CURRENT'
    aprx=arcpy.mp.ArcGISProject(aprx_path)
    for map_obj in aprx.listMaps(map_name):
        aprx.deleteItem(map_obj)
        arcpy.AddMessage(f"{map_name} map exists, deleted")
    map_obj = aprx.createMap(map_name)
    arcpy.AddMessage(f"{map_name} map created")
    
    return map_obj

#Step 7
def add_feature_class_layers(map_obj,students_path,student_fc):
    aprx_path='CURRENT'
    aprx=arcpy.mp.ArcGISProject(aprx_path)
    arcpy.env.workspace=students_path
    studfc_name=student_fc
    stud_fc=os.path.join(students_path, studfc_name)
    if arcpy.Exists(stud_fc):
            lyr = map_obj.addDataFromPath(stud_fc)
            arcpy.AddMessage(f"Added {student_fc} to the map")
            lyr.visible = True
                
    else:
        arcpy.AddMessage(f"{student_fc} does not exist")
        
def symbolize_studentsfc(map_obj,students_path,student_fc):
    aprx_path='CURRENT'
    aprx=arcpy.mp.ArcGISProject(aprx_path)
    arcpy.env.workspace=students_path
    arcpy.AddMessage(student_fc)
    aprx = arcpy.mp.ArcGISProject('CURRENT')
    color_ramp_name = "Condition Number"
    color_ramps = aprx.listColorRamps(color_ramp_name)
    
    if not color_ramps:
        arcpy.AddMessage(f"Color ramp '{color_ramp_name}' not found.")
        return
    color_ramp = color_ramps[0]
    
    for lyr in map_obj.listLayers():
        if lyr.isFeatureLayer and lyr.name == student_fc:
            sym = lyr.symbology
            if hasattr(sym, 'renderer'):
                sym.updateRenderer('UniqueValueRenderer')
                sym.renderer.fields = ["RESIDENT"]
                sym.renderer.colorRamp = color_ramp
                #sym.renderer.addAllValues()
                lyr.symbology = sym
                arcpy.AddMessage(f"Symbolized {student_fc} based on RESIDENT field")
                
def add_district_layer(map_obj, district):
    if arcpy.Exists(district):
        district_layer = map_obj.addDataFromPath(district)
        symbology = district_layer.symbology
        symbology.updateRenderer('SimpleRenderer')
        renderer = symbology.renderer
        symbol = renderer.symbol
        symbol.outlineColor = {'RGB': [0, 0, 0]}  # Black outline
        symbol.outlineWidth = 3
        symbol.color = {"RGB": [0, 0, 0, 0]}  # No fill
        district_layer.symbology = symbology
        arcpy.AddMessage('District symbology updated')
    else:
        arcpy.AddMessage("District feature class does not exist")
        
def set_active_view(map_name):
    aprx_path = 'CURRENT'
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    map_view = aprx.listMaps(map_name)[0]
    map_view.openView()
    arcpy.AddMessage(f"Set {map_name} as the active view")
    arcpy.AddMessage("Tool complete!")

#Step 8
def DeleteTable(students_path,student_fc):
    tbl=f"TABLE_{student_fc}"
    split_tbl=f"TABLE_{student_fc}_SPLIT"
    table=os.path.join(students_path,tbl)
    split_table=os.path.join(students_path,split_tbl)
    arcpy.management.Delete(table)
    arcpy.AddMessage("Deleted table")
    arcpy.management.Delete(split_table)
    arcpy.AddMessage("Deleted table w/ split addresses")
    arcpy.AddMessage("Tool complete!")
    
if __name__=="__main__":
    excel_path=arcpy.GetParameterAsText(0)
    add_field=arcpy.GetParameterAsText(1)
    zip_field = arcpy.GetParameterAsText(2)  # This is optional
    students_path=arcpy.GetParameterAsText(3)
    student_fc=arcpy.GetParameterAsText(4)
    locator = arcpy.GetParameterAsText(5)
    district = arcpy.GetParameterAsText(6)
    CleanExcel(excel_path,add_field)
    CreateTable(excel_path,students_path,student_fc)
    Geocode(students_path,student_fc,locator,zip_field)
    EditorTracking(students_path,student_fc)
    TOTAL(students_path,student_fc)
    AddFields(students_path,student_fc)
    SpatialJoin_Y(students_path,student_fc,district)
    SpatialJoin_N(students_path,student_fc,district)
    Resident(students_path,student_fc)
    geocoding_map=ensure_map_exists(students_path,student_fc,"Geocoding")
    add_district_layer(geocoding_map, district)
    add_feature_class_layers(geocoding_map,students_path,student_fc)
    symbolize_studentsfc(geocoding_map,students_path,student_fc)
    set_active_view("Geocoding")
