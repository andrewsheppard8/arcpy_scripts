"""
===============================================================================
Script Name:       Utilization Tool
Author:            Andrew Sheppard
Role:              GIS Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-03-25

Description:
-------------

Overall, this is not a particulary interesting tool, quite niche, used to gather information on
the intersection of a point feature class and a polygon feature class. It is not broken into functions,
is tough to read and is generally not organized/optimized. I don't recommend going through it. I
added it because I do like how the script deals with adding the information to a map, symbolizing,
labeling, and working with the layers in the contents pane. The actual analysis is unsophisticated.
But the final output, to be used by an analyst, is effective and clean.

The sections on labeling, symbology, and working in the map view will be broken into seperate functions
and added to the arcpy_functions repo.
===============================================================================
"""
import arcpy
from arcpy import env
import os
#First, this tool will run the dissolve tool in the SIS Directory Tools. 
studyareas=arcpy.GetParameterAsText(0)
destination=arcpy.GetParameterAsText(1)
toolbox_path = r"TOOLBOX_PATH"
if arcpy.Exists(toolbox_path):
    arcpy.AddMessage("toolbox exists")
    arcpy.ImportToolbox(toolbox_path,"custom_tools")
    arcpy.AddMessage("Toolbox imported")
    try:
        arcpy.custom_tools.DistrictDissolvesSeon(studyareas,destination)
        arcpy.AddMessage("Tracts Update second tool executed successfully")
    except Exception as e:
        arcpy.AddMessage(f"Error running Dissolve Tool: {e}")
#Parameters for Utilization tool
workspace=arcpy.GetParameterAsText(2)
outdir_main=os.path.join(workspace, 'Basemap.gdb/Main/')
outdir_misc=os.path.join(workspace, 'Misc.gdb')
outdir_stud=os.path.join(workspace, 'Students.gdb')
stud_features=arcpy.GetParameterAsText(3)
stud_fc=os.path.join(outdir_stud,stud_features)
if arcpy.Exists(stud_fc):
    stud_Count=arcpy.GetParameterAsText(4)
#get information on student count
summaryField = ['SCHL_CODE']
summaryStatistics = [[stud_Count, 'COUNT']]
summaryTable = os.path.join(outdir_misc,'SUMMARY')
#summarize school code by student ID and get Summary table output to Misc.gdb
arcpy.gapro.SummarizeAttributes(stud_fc,summaryTable, summaryField, summaryStatistics)
arcpy.AddMessage('Created Summary table of Student count by SCHL_CODE')
school_features = os.path.join(outdir_main, 'Schools')
fieldName = 'UTILIZATION'
fieldName2 = 'SCHLCODE_TXT'
fields_to_check = [fieldName,fieldName2]
existing_fields=[field.name for field in arcpy.ListFields(school_features)]
for field_name in fields_to_check:
    if field_name in existing_fields:
        arcpy.DeleteField_management(school_features,field_name)
        arcpy.AddMessage(f"{field_name} exists. Deleted")
    else:
        #add fields to Schools Feature Class
        arcpy.management.AddField(school_features,fieldName, 'INTEGER', field_length=3, field_is_nullable='NULLABLE')
        arcpy.management.AddField(school_features,fieldName2, 'TEXT', field_is_nullable='NULLABLE')
        arcpy.AddMessage(f'{field_name} added to Schools fc')
#calculate SCHL_CODE to text for use in AA layers
arcpy.management.CalculateField(school_features,fieldName2,expression='!SCHL_CODE!',expression_type='PYTHON3',code_block="")
arcpy.AddMessage('Calculated SCHL_CODE_TXT field from integer to text')
#join schools layer to summarize layer
school_join=arcpy.management.AddJoin(school_features,'SCHL_CODE',summaryTable,'SCHL_CODE')
arcpy.management.CopyFeatures(school_join, (os.path.join(outdir_misc,'schools_join')))
schools_join=os.path.join(outdir_misc,'schools_join')
arcpy.AddMessage('Joined Summary table to Schools fc')
#calculate utilization
join_table=schools_join
arcpy.management.CalculateField(join_table,'Schools_UTILIZATION',expression='(!SUMMARY_COUNT!/!Schools_CAPACITY!)*100',
                                expression_type='PYTHON3',code_block="")
arcpy.AddMessage('Calculated Utilization in new Schools fc')
#create ElemAA utilization layer
elemAA_UT=os.path.join(outdir_misc,'ElemAA_Utilization')
if arcpy.Exists(os.path.join(outdir_misc,'ElemAA')):
    elemAA= os.path.join(outdir_misc,'ElemAA')
    elem_join=arcpy.management.AddJoin(elemAA,'SchoolCode',join_table,'Schools_SCHLCODE_TXT')
    arcpy.management.CopyFeatures(elem_join,(os.path.join(outdir_misc, 'ElemAA_Utilization')))
    elemAA_UT=os.path.join(outdir_misc,'ElemAA_Utilization')
    arcpy.AddMessage('ElemAA join completed')
##    fields = arcpy.ListFields(elemAA_UT)
##    fields_to_keep= []
##    for field in fields:
##        if (field.name.startswith('ElemAA') or (field.name == 'schools_join_Schools_UTILIZATION') or field.required):
##            fields_to_keep.append(field.name)
##        else: arcpy.management.DeleteField(elemAA_UT, field.name)
    arcpy.AddMessage('Enriched ElemAA')
    arcpy.Delete_management(elemAA)
    arcpy.AddMessage('Original ElemAA deleted')
    arcpy.management.Rename(elemAA_UT,'ElemAA')
    arcpy.AddMessage('ElemAA utilization layer renamed')
    
else:
    arcpy.AddMessage('ElemAA does not exist. Skipping geoprocess')
#create IntAA utilization layer
intAA_UT=os.path.join(outdir_misc,'IntAA_Utilization')
if arcpy.Exists(os.path.join(outdir_misc,'IntAA')):
    intAA= os.path.join(outdir_misc,'IntAA')
    int_join=arcpy.management.AddJoin(intAA,'SchoolCode',join_table,'Schools_SCHLCODE_TXT')
    arcpy.management.CopyFeatures(int_join,(os.path.join(outdir_misc,'IntAA_Utilization')))
    intAA_UT=os.path.join(outdir_misc,'IntAA_Utilization')
    arcpy.AddMessage('IntAA join completed')
##    fields = arcpy.ListFields(intAA_UT)
##    fields_to_keep= []
##    for field in fields:
##        if (field.name.startswith('IntAA') or (field.name == 'schools_join_Schools_UTILIZATION') or field.required):
##            fields_to_keep.append(field.name)
##        else: arcpy.management.DeleteField(intAA_UT, field.name)
    arcpy.AddMessage('Enriched IntAA')
    arcpy.Delete_management(intAA)
    arcpy.AddMessage('Original IntAA deleted')
    arcpy.management.Rename(intAA_UT,'IntAA')
    arcpy.AddMessage('IntAA utilization layer renamed')
    
else:
    arcpy.AddMessage('IntAA does not exist. Skipping geoprocess')
#create MidAA utilization layer
midAA_UT=os.path.join(outdir_misc,'MidAA_Utilization')
if arcpy.Exists(os.path.join(outdir_misc,'MidAA')):
    midAA= os.path.join(outdir_misc,'MidAA')
    ms_join=arcpy.management.AddJoin(midAA,'SchoolCode',join_table,'Schools_SCHLCODE_TXT')
    arcpy.management.CopyFeatures(ms_join,(os.path.join(outdir_misc,'MidAA_Utilization')))
    midAA_UT=os.path.join(outdir_misc,'MidAA_Utilization')
    arcpy.AddMessage('MidAA join completed')
##    fields = arcpy.ListFields(midAA_UT)
##    fields_to_keep= []
##    for field in fields:
##        if (field.name.startswith('MidAA') or (field.name == 'schools_join_Schools_UTILIZATION') or field.required):
##            fields_to_keep.append(field.name)
##        else: arcpy.management.DeleteField(midAA_UT, field.name)
    arcpy.AddMessage('Enriched MidAA')
    arcpy.Delete_management(midAA)
    arcpy.AddMessage('Original MidAA deleted')
    arcpy.management.Rename(midAA_UT,'MidAA')
    arcpy.AddMessage('MidAA utilization layer renamed')
    
else:
    arcpy.AddMessage('MidAA does not exist. Skipping geoprocess')
#create HighAA utilization layer
highAA_UT=os.path.join(outdir_misc,'HighAA_Utilization')
if arcpy.Exists(os.path.join(outdir_misc,'HighAA')):
    highAA= os.path.join(outdir_misc,'HighAA')
    hs_join=arcpy.management.AddJoin(highAA,'SchoolCode',join_table,'Schools_SCHLCODE_TXT')
    arcpy.management.CopyFeatures(hs_join,(os.path.join(outdir_misc,'HighAA_Utilization')))
    highAA_UT=os.path.join(outdir_misc,'HighAA_Utilization')
    arcpy.AddMessage('HighAA join completed')
##    fields = arcpy.ListFields(highAA_UT)
##    fields_to_keep= []
##    for field in fields:
##        if (field.name.startswith('HighAA') or (field.name == 'schools_join_Schools_UTILIZATION') or field.required):
##            fields_to_keep.append(field.name)
##        else: arcpy.management.DeleteField(highAA_UT, field.name)
    arcpy.AddMessage('Enriched HighAA')
    arcpy.Delete_management(highAA)
    arcpy.AddMessage('Original HighAA deleted')
    arcpy.management.Rename(highAA_UT,'HighAA')
    arcpy.AddMessage('HighAA utilization layer renamed')
    
else:
    arcpy.AddMessage('HighAA does not exist. Skipping geoprocess')
#delete intermediate layers
arcpy.Delete_management(summaryTable)
arcpy.AddMessage('Deleted Summary table')
arcpy.Delete_management(join_table)
arcpy.AddMessage('Deleted intermediate Schools layer')
#delete extra fields in schools layer
fields_to_delete = [fieldName,fieldName2]
schl_fields_delete=[field.name for field in arcpy.ListFields(school_features)]
for field_name in fields_to_delete:
    if field_name in schl_fields_delete:
        arcpy.DeleteField_management(school_features,field_name)
        arcpy.AddMessage(f"{field_name} deleted from Schools fc")
aprx_path = "CURRENT"
feature_classes = ['HighAA', 'MidAA', 'IntAA', 'ElemAA']
arcpy.env.workspace = outdir_misc

"""
==========================================================================
From here down is the interesting part of the script for future use
==========================================================================
"""

def ensure_map_exists(aprx, map_name):
    """
    Ensure that a map exists in the ArcGIS Pro project. If not, create it.
    """
    for map_obj in aprx.listMaps(map_name):
        aprx.deleteItem(map_obj)
        arcpy.AddMessage(f"{map_name} map exists, deleted")
    map_obj = aprx.createMap(map_name)
    arcpy.AddMessage(f"{map_name} map created")
    
    return map_obj
def add_feature_class_layers(map_obj, feature_classes):
    """
    Add feature class layers to the specified map object.
    """
    for fc in feature_classes:
        fc_path = os.path.join(arcpy.env.workspace, fc)
        if arcpy.Exists(fc_path):
            lyr = map_obj.addDataFromPath(fc_path)
            arcpy.AddMessage(f"Added {fc} to the map")
            if fc != "ElemAA" and fc != "District":
                lyr.visible = False
            else:
                lyr.visible = True
                
        else:
            arcpy.AddMessage(f"{fc} does not exist")
def symbolize_layers(map_obj, layer_names, field):
    """
    Apply symbology to the layers specified in layer_names based on the given field.
    """
    color_ramp_name = "Viridis"
    color_ramps = aprx.listColorRamps(color_ramp_name)
    if not color_ramps:
        arcpy.AddMessage(f"Color ramp '{color_ramp_name}' not found.")
        return
    color_ramp = color_ramps[0]
    symbolized_layers=set()
    
    for lyr in map_obj.listLayers():
        if lyr.isFeatureLayer and lyr.name in layer_names:
            if lyr.name not in symbolized_layers:
                sym = lyr.symbology
                if hasattr(sym, 'renderer'):
                    sym.updateRenderer('GraduatedColorsRenderer')
                    sym.renderer.classificationField = field
                    sym.renderer.breakCount = 5  # Set a reasonable break count
                    sym.renderer.colorRamp = color_ramp
                    if lyr.name != "District":
                        layer_cim = lyr.getDefinition('V3')
                        layer_cim.blendingMode = 'Multiply'  # Default is 'Normal'
                        lyr.setDefinition(layer_cim)
                    lyr.symbology = sym
                    symbolized_layers.add(lyr.name)  # Mark this layer as symbolized
                    arcpy.AddMessage(f"Symbolized {lyr.name} based on '{field}' field")
def Label_AttendanceAreas(map_obj):
    layer_expressions = {
        "ElemAA": "$feature.ElemAA_ELEM_DESC + TextFormatting.NewLine + $feature.schools_join_Schools_UTILIZATION + '%'",
        "MidAA": "$feature.MidAA_MID_DESC + TextFormatting.NewLine + $feature.schools_join_Schools_UTILIZATION + '%'",
        "IntAA": "$feature.IntAA_INT_DESC + TextFormatting.NewLine + $feature.schools_join_Schools_UTILIZATION + '%'",
        "HighAA": "$feature.HighAA_HIGH_DESC + TextFormatting.NewLine + $feature.schools_join_Schools_UTILIZATION + '%'"
    }
    for layer_name, label_expression in layer_expressions.items():
        if any(lyr.name == layer_name for lyr in map_obj.listLayers(layer_name)):
            for lyr in map_obj.listLayers(layer_name):
                lblClass=lyr.listLabelClasses()[0]
                lblClass.expression = label_expression
                l_cim=lyr.getDefinition('V2')
                lc = l_cim.labelClasses[0]
                # Set the text symbol properties
                text_symbol = lc.textSymbol
##                text_symbol.symbol.color = {'RGB': [255, 255, 255]}  # White text
                text_symbol.symbol.fontFamilyName = 'Calibri'
##                text_symbol.symbol.fontSize = 14
##                text_symbol.haloSize = 1
##                text_symbol.haloSymbol.symbol.color = {'red': 255, 'green': 255, 'blue': 255, 'alpha': 255}
            
            lyr.setDefinition(l_cim)
            lyr.showLabels = True
            arcpy.AddMessage(f'{layer_name} labels turned on')
                
def add_district_layer(map_obj):
    """
    Add the 'District' layer to the map and set its symbology.
    """
    fc_path = os.path.join(arcpy.env.workspace, "District")
    if arcpy.Exists(fc_path):
        district_layer = map_obj.addDataFromPath(fc_path)
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
layer_rename_map = {
    "ElemAA": "Elementary School Capacity",
    "MidAA": "Middle School Capacity",
    "IntAA": "Intermediate School Capacity",
    "HighAA": "High School Capacity"
}
def rename_layers(map_obj, rename_map):
    """Rename layers in the specified map according to the provided rename map."""
    for old_name, new_name in rename_map.items():
        # Find the layer by name
        layer = map_obj.listLayers(old_name)
        if layer:
            layer[0].name = new_name
            arcpy.AddMessage(f"Renamed layer '{old_name}' to '{new_name}'.")
        else:
            arcpy.AddMessage(f"Layer '{old_name}' not found.")
def set_active_view(map_name):
    aprx_path = 'CURRENT'
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    map_view = aprx.listMaps(map_name)[0]
    map_view.openView()
    arcpy.AddMessage(f"Set {map_name} as the active view")
    arcpy.AddMessage("Tool complete!")
    
try:
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    utilization_map = ensure_map_exists(aprx, "Utilization")
    add_district_layer(utilization_map)
    add_feature_class_layers(utilization_map, feature_classes)
    layer_names_to_symbolize = ["ElemAA", "MidAA", "IntAA", "HighAA"]
    symbolize_layers(utilization_map, layer_names_to_symbolize, 'schools_join_Schools_UTILIZATION')
    Label_AttendanceAreas(utilization_map)
    rename_layers(utilization_map,layer_rename_map)
    set_active_view("Utilization")
    
    aprx.save()
    arcpy.AddMessage("Project saved successfully")
except Exception as e:
    arcpy.AddMessage(f"An error occurred: {e}")
arcpy.AddMessage('Tool complete')
