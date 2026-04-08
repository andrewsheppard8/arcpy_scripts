"""
===============================================================================
Script Name:       AGOL Feature Service Publisher
Author:            Andrew Sheppard
Role:              GIS Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-04-08

Description:
-------------
This script automates the process of publishing a feature class from an ArcGIS 
Pro project to ArcGIS Online as a hosted feature layer. 
    - Loads a specified ArcGIS Pro project and map
    - Clears existing layers from the map
    - Adds the target feature class
    - Deletes any existing services or service definitions with the same name
      in AGOL
    - Creates a timestamped service name
    - Generates a Web Layer Sharing Draft and stages it
    - Uploads the staged service to AGOL
    - Logs progress and errors with timestamped logs in the scratch folder

This tool is **interactive** and designed to run within ArcGIS Pro. 
A fully headless version for automated batch publishing will be developed 
in a future iteration.

Future Improvements:
--------------------
- Add a fully headless mode for automated batch publishing
- Allow dynamic selection of hosting server or portal URL
- Optionally store logs in a permanent folder outside the scratch workspace
- Implement more robust error handling and retry logic for AGOL API calls
- Add email or Teams notifications upon completion or failure

===============================================================================
"""
import arcpy
import os
import logging
import traceback
import time
from datetime import datetime
from arcgis.gis import GIS

# ==============================
# 1. LOGGING SETUP
# ==============================
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(arcpy.env.scratchFolder, f"publish_log_{timestamp}.txt")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)
    arcpy.AddMessage(msg)

def log_error(msg):
    print(msg)
    logging.error(msg)
    arcpy.AddError(msg)

# ==============================
# 2. DELETE EXISTING AGOL SERVICE
# ==============================
def delete_existing_service(service_name, log, log_error, max_wait=15):
    try:
        log(f"Connecting to AGOL to check for existing service: {service_name}")
        gis = GIS("home")
        username = gis.users.me.username

        search_results = gis.content.search(
            query=f'title:"{service_name}" AND owner:{username}',
            item_type=None,
            max_items=50
        )

        if not search_results:
            log("No existing items found.")
            return

        for item in search_results:
            if item.type in ["Feature Layer",
                             "Feature Layer Collection",
                             "Service Definition",
                             "Feature Service"]:
                log(f"Deleting: {item.title} ({item.type})")
                try:
                    item.delete()
                    log(f"Deleted: {item.title}")
                except Exception as e:
                    log_error(f"Failed to delete {item.title}: {str(e)}")

        # Poll AGOL to confirm deletion
        log("Verifying deletion in AGOL...")
        wait_time = 0
        while wait_time < max_wait:
            remaining = gis.content.search(
                query=f'title:"{service_name}" AND owner:{username}',
                item_type=None,
                max_items=50
            )
            remaining_items = [item for item in remaining if item.type in ["Feature Layer",
                                                                           "Feature Layer Collection",
                                                                           "Service Definition",
                                                                           "Feature Service"]]
            if not remaining_items:
                log("All existing items fully deleted.")
                return
            log(f"Waiting for AGOL to finish deletion... {len(remaining_items)} items remaining")
            time.sleep(3)
            wait_time += 3

        remaining_titles = [item.title for item in remaining_items]
        raise Exception(f"Could not delete all items: {remaining_titles}")

    except Exception as e:
        log_error("Failed to fully delete existing service/items.")
        log_error(str(e))
        raise

# ==============================
# 3. MAIN PUBLISH FUNCTION
# ==============================
def publish_feature_layer(aprx_path, map_name, feature_class, service_name, folder_name=None):
    try:
        log("========== START PUBLISH PROCESS ==========")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        map_obj = aprx.listMaps(map_name)[0]
        log(f"Map loaded: {map_name}")

        # ------------------------------
        # Clean up previous scratch files
        # ------------------------------
        for ext in [".sddraft", ".sd"]:
            for f in os.listdir(arcpy.env.scratchFolder):
                if f.startswith(service_name) and f.endswith(ext):
                    full_path = os.path.join(arcpy.env.scratchFolder, f)
                    try:
                        os.remove(full_path)
                        log(f"Deleted leftover scratch file: {full_path}")
                    except:
                        pass

        # ------------------------------
        # Clear existing layers
        # ------------------------------
        existing_layers = map_obj.listLayers()
        if existing_layers:
            for lyr in existing_layers:
                log(f"Removing layer: {lyr.name}")
                map_obj.removeLayer(lyr)
        else:
            log("No existing layers found.")

        # ------------------------------
        # Add target feature class
        # ------------------------------
        log(f"Adding feature class: {feature_class}")
        layer = map_obj.addDataFromPath(feature_class)
        if not layer:
            raise Exception("Failed to add feature class to map.")
        log(f"Layer added successfully: {layer.name}")

        # ------------------------------
        # Delete old services
        # ------------------------------
        log("Deleting any existing AGOL service with the same root name...")
        delete_existing_service(service_name, log, log_error)

        # ------------------------------
        # Confirm single layer
        # ------------------------------
        layers_now = map_obj.listLayers()
        log(f"Current layer count: {len(layers_now)}")
        if len(layers_now) != 1:
            raise Exception("More than one layer detected — aborting to prevent accidental publishing.")

        # ------------------------------
        # Create timestamped service name
        # ------------------------------
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        service_name_unique = f"{service_name}_{timestamp}"
        log(f"Service will be published as: {service_name_unique}")

        # ------------------------------
        # Create sharing draft
        # ------------------------------
        log("Creating Web Layer Sharing Draft...")
        sharing_draft = map_obj.getWebLayerSharingDraft(
            "HOSTING_SERVER",
            "FEATURE",
            service_name_unique
        )
        sharing_draft.summary = f"Automated publish via ArcPy: {service_name_unique}"
        sharing_draft.tags = "automation, arcpy"
        sharing_draft.overwriteExistingService = True
        sharing_draft.allowExporting = True

        # ------------------------------
        # Export SDDraft
        # ------------------------------
        sddraft = os.path.join(arcpy.env.scratchFolder, f"{service_name_unique}.sddraft")
        log(f"Exporting SDDraft: {sddraft}")
        sharing_draft.exportToSDDraft(sddraft)
        if not os.path.exists(sddraft):
            raise Exception("SDDraft was not created.")
        log("SDDraft created successfully.")

        # ------------------------------
        # Stage Service (.sd)
        # ------------------------------
        sd = os.path.join(arcpy.env.scratchFolder, f"{service_name_unique}.sd")
        log("Staging service...")
        arcpy.server.StageService(sddraft, sd)
        if not os.path.exists(sd):
            raise Exception("Service Definition (.sd) not created.")
        log("Service successfully staged (.sd created).")

        # ------------------------------
        # Upload to AGOL
        # ------------------------------
        log("Uploading Service Definition to AGOL...")
        arcpy.server.UploadServiceDefinition(
            sd,
            "HOSTING_SERVER",
            in_override="OVERRIDE_DEFINITION",
            in_public="PRIVATE",
            in_organization="SHARE_ORGANIZATION",
            in_groups="",
            in_folder_type="EXISTING" if folder_name else "NONE",
            in_folder=folder_name
        )

        # ------------------------------
        # Confirm upload exists in AGOL
        # ------------------------------
        gis = GIS("home")
        uploaded_items = gis.content.search(query=f'title:"{service_name_unique}" AND owner:{gis.users.me.username}', max_items=1)
        if uploaded_items:
            log(f"Upload confirmed: {uploaded_items[0].title} ({uploaded_items[0].type})")
        else:
            log_error("Upload may have failed; item not found in AGOL.")

        log("Publish completed successfully!")

    except Exception as e:
        log_error("ERROR DURING PUBLISH PROCESS")
        log_error(str(e))
        tb = traceback.format_exc()
        log_error(tb)
        raise

    finally:
        log("========== END PROCESS ==========")

# ==============================
# 4. RUN
# ==============================
if __name__ == "__main__":
    # Replace the placeholders with your local paths and AGOL info
    aprx_path = r"C:\Path\To\YourProject.aprx"
    map_name = "YourMapName"
    feature_class = r"C:\Path\To\FeatureClass.gdb\FeatureClassName"
    service_name = "MyFeatureService"
    folder_name = "AGOL_Folder"

    publish_feature_layer(
        aprx_path=aprx_path,
        map_name=map_name,
        feature_class=feature_class,
        service_name=service_name,
        folder_name=folder_name
    )
