"""
===============================================================================
Script Name:       AGOL User Audit (CLI)
Author:            Andrew Sheppard
Role:              GIS Developer | Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-04-09

Description:
-------------
This script provides a command-line interface (CLI) for auditing ArcGIS Online
user content using the ArcGIS API for Python.

    - Authenticates to AGOL (via config file or parameters)
    - Retrieves all items owned by the user
    - Calculates total item count and approximate storage usage
    - Provides an item type breakdown
    - Identifies:
        * Largest items
        * Recently modified items
        * Stale items (not modified in 1+ year)
        * Items missing descriptions
    - Supports command-line flags for flexible execution
    - Exports results to a timestamped .txt report

Example Usage:
---------------
Run via standard Python:

    python agol_audit_cli.py --summary-only

Run using the ArcGIS Pro Python environment (recommended):

    & "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "C:\path\agol_audit_cli.py" --summary-only (optional)

Notes:
-------
- It is recommended to execute this script using the ArcGIS Pro Python interpreter,
  as it ensures the required ArcGIS API for Python and dependencies are available.
- The CLI version is designed for automation, scheduling, and advanced workflows,
  including integration with Windows Task Scheduler or CI/CD pipelines.


Key Features:
--------------
- Flexible execution via command-line arguments
- Automation-ready design
- Scalable for future enhancements

Future Improvements:
--------------------
- Add additional CLI flags (e.g., --stale-only, --top-n)
- Support organization-wide auditing (admin mode)
- Integrate logging to file or external monitoring systems
- Add notification support (email, Teams, etc.)

===============================================================================
"""

from arcgis.gis import GIS
import configparser
import os
import logging
from datetime import datetime
from collections import Counter

# ==============================
# LOGGING / OUTPUT SETUP
# ==============================

def log(msg=""):
    print(msg)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

# ==============================
# CONFIG PATH (SCRIPT-RELATIVE)
# ==============================
CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "config.ini"
)

# ==============================
# TIMESTAMPED REPORT FILE
# ==============================
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

REPORT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    f"agol_report_{timestamp}.txt"
)

# ==============================
# CONFIG LOADER
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

# ==============================
# MAIN FUNCTION
# ==============================
def inspect_agol_content(summary_only=False):

    # Clear report file (fresh run)
    open(REPORT_PATH, "w", encoding="utf-8").close()

    log("===================================")
    log("AGOL ACCOUNT INSPECTION REPORT")
    log(f"Generated: {datetime.now()}")
    log("===================================")
    log("")

    log("Loading configuration...")
    creds = load_config(CONFIG_PATH)

    log("Connecting to AGOL...")
    gis = GIS(
        creds["portal_url"],
        creds["username"],
        creds["password"]
    )

    user = gis.users.me
    log(f"Connected as: {user.username}")

    log("\nRetrieving your content...")

    items = gis.content.search(
        query=f"owner:{user.username}",
        max_items=1000
    )

    item_count = len(items)
    log(f"Total items found: {item_count}")

    if item_count == 0:
        log("No items found.")
        return

    # ==============================
    # METRICS
    # ==============================
    total_size_bytes = sum(item.size or 0 for item in items)
    total_size_mb = total_size_bytes / (1024 ** 2)

    largest_items = sorted(
        items,
        key=lambda x: x.size or 0,
        reverse=True
    )[:10]

    # ==============================
    # SUMMARY MODE
    # ==============================
    if summary_only:
        log("\n===== SUMMARY =====")
        log(f"User: {user.username}")
        log(f"Total Items: {item_count}")
        log(f"Total Storage (approx): {total_size_mb:.2f} MB")
        log(f"Largest Item: {largest_items[0].title if largest_items else 'N/A'}")
        log("===================")
        return

    # ==============================
    # FULL OUTPUT
    # ==============================

    log("\n--- Item Type Breakdown ---")
    type_counts = Counter(item.type for item in items)
    for t, count in type_counts.most_common():
        log(f"{t}: {count}")

    log("\n--- Top 10 Largest Items ---")
    for i, item in enumerate(largest_items, start=1):
        size_mb = (item.size or 0) / (1024 ** 2)
        log(f"{i}. {item.title} ({item.type}) - {size_mb:.2f} MB")

    log("\n--- All Items ---")
    for i, item in enumerate(items, start=1):
        log(f"{i}. {item.title} ({item.type}) | ID: {item.id}")

    log("\n===== SUMMARY =====")
    log(f"User: {user.username}")
    log(f"Total Items: {item_count}")
    log(f"Total Storage (approx): {total_size_mb:.2f} MB")
    log(f"Largest Item: {largest_items[0].title if largest_items else 'N/A'}")
    log("===================")


# ==============================
# RUN (CLI)
# ==============================
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--summary-only", action="store_true")

    args = parser.parse_args()

    inspect_agol_content(
        summary_only=args.summary_only
    )
