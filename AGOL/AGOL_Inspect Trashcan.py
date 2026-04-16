"""
===============================================================================
Script Name:       AGOL Recycle Bin Inspector
Author:            Andrew Sheppard
Role:              GIS Developer | Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-04-16

Description:
-------------
This script connects to an ArcGIS Online (AGOL) organization using the
ArcGIS Python API and inspects the organization's Recycle Bin contents
via the REST portal content endpoint.

It demonstrates how to access system-level deleted items and provides
a lightweight alternative for administrative
or auditing tasks.

Core functionality:
    - Authenticates to ArcGIS Online using the ArcGIS Python API (GIS)
    - Retrieves organization portal metadata (portal ID)
    - Queries the /content/portals/{orgId} endpoint
      with inRecycleBin=True
    - Extracts and prints item titles currently in the Recycle Bin
    - Returns a list of deleted item names for further processing

Use Cases:
-------------
- Quick audit of deleted content in an AGOL organization
- Validation of user or organizational cleanup activity
- Learning example for REST-based portal queries using ArcGIS Python API
- Foundation for building admin dashboards or reporting tools

Limitations:
-------------
- Requires user-level or admin-level access depending on org settings
- Minimal error handling for API response failures
- Intended for learning, testing, and rapid prototyping only

Future Improvements:
--------------------
- Add error handling and retry logic for API requests
- Support organization-wide recycle bin aggregation (multi-user audit)
- Add CLI arguments for flexible execution
- Integrate logging to file instead of console-only output

Notes:
------
This script intentionally demonstrates a "direct access" pattern to AGOL
administration endpoints to simplify understanding of how the recycle bin
is exposed via the REST API.

===============================================================================
"""
import configparser
from arcgis.gis import GIS
import logging
import os

# ==============================
# CONFIG
# ==============================
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_path)

    return {
        "portal_url": config["AGOL"]["portal_url"],
        "username": config["AGOL"]["username"],
        "password": config["AGOL"]["password"]
    }

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "config.ini"
)

# ==============================
# LOGGING BUFFER (for TXT export)
# ==============================
logging.basicConfig(level=logging.INFO)

log_output = []

def log(msg=""):
    print(msg)
    log_output.append(str(msg))

# ==============================
# MAIN FUNCTION
# ==============================
def inspect_agol_recycling():
    log("Connecting to AGOL...")
    creds = load_config(CONFIG_PATH)

    gis = GIS(
        creds["portal_url"],
        creds["username"],
        creds["password"]
    )

    # ------------------------------
    # 1. Confirm user
    # ------------------------------
    user = gis.users.me
    log(f"Connected as: {user.username}")

    portal_id = gis.properties.id
##    log(f"Portal ID: {portal_id}")

    url = f"{creds['portal_url']}/sharing/rest/content/portals/{portal_id}"

    params = {
        "f": "json",
        "token": gis._con.token,
        "foldersContent": True,
        "inRecycleBin": True
    }

    response = gis._con.get(url, params)

##    print("RAW RESPONSE:")
##    print(response)

    # ------------------------------
    # Extract item names
    # ------------------------------
    items = response.get("items", [])

    item_names = []

    for item in items:
        title = item.get("title", "Unnamed Item")
        item_names.append(title)
        log(f"- {title}")

    log(f"\nTotal items in recycle bin: {len(item_names)}")

    return item_names

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    inspect_agol_recycling()

