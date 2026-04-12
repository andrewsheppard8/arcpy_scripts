"""
===============================================================================
Script Name:       AGOL User Audit (Hardcoded)
Author:            Andrew Sheppard
Role:              GIS Developer | Solutions Engineer
Email:             andrewsheppard8@gmail.com
Date Created:      2026-04-09

Description:
-------------
This script connects to ArcGIS Online using hardcoded credentials and performs
a basic audit of the user's content.

    - Authenticates to AGOL using embedded credentials
    - Retrieves all items owned by the user
    - Calculates total item count and approximate storage usage
    - Provides an item type breakdown
    - Identifies:
        * Largest items
        * Recently modified items
        * Stale items (not modified in 1+ year)
        * Items missing descriptions
    - Outputs results to console and exports a timestamped .txt report

This version is intended for **quick testing, learning, and rapid execution**.

Limitations:
-------------
- Credentials are stored directly in the script (not secure)
- Not suitable for shared environments or production use

Future Improvements:
--------------------
- Replace hardcoded credentials with config file or environment variables
- Add CLI argument support for flexible execution
- Expand reporting options (CSV, Excel)
- Extend to support organization-wide auditing

===============================================================================
"""

from arcgis.gis import GIS
import logging
from datetime import datetime
from collections import Counter
import os

# ==============================
# CONFIG
# ==============================
PORTAL_URL = "portal_url" #UPDATE
USERNAME = "username" #UPDATE
PASSWORD = "password" #UPDATE

# ==============================
# LOGGING BUFFER (for TXT export)
# ==============================
logging.basicConfig(level=logging.INFO)

log_output = []

def log(msg=""):
    print(msg)
    log_output.append(str(msg))


# ==============================
# EXPORT FUNCTION
# ==============================
def export_report():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        f"agol_report_{timestamp}.txt"
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_output))

    print(f"\nReport saved to:\n{report_path}")


# ==============================
# MAIN FUNCTION
# ==============================
def inspect_agol_content():
    log("Connecting to AGOL...")
    gis = GIS(PORTAL_URL, USERNAME, PASSWORD)

    # ------------------------------
    # 1. Confirm user
    # ------------------------------
    user = gis.users.me
    log(f"Connected as: {user.username}")

    # ------------------------------
    # 2. Get all owned items
    # ------------------------------
    log("\nRetrieving your content...")

    items = gis.content.search(
        query=f"owner:{user.username}",
        max_items=1000
    )

    item_count = len(items)
    log(f"Total items found: {item_count}")

    if item_count == 0:
        log("No items found in your account.")
        export_report()
        return

    # ------------------------------
    # 3. Storage Calculation
    # ------------------------------
    total_size_bytes = sum(item.size or 0 for item in items)
    total_size_mb = total_size_bytes / (1024 ** 2)

    # ------------------------------
    # 4. Item Type Breakdown
    # ------------------------------
    log("\n--- Item Type Breakdown ---")

    type_counts = Counter(item.type for item in items)

    for t, count in type_counts.most_common():
        log(f"{t}: {count}")

    # ------------------------------
    # 5. Top 10 Largest Items
    # ------------------------------
    log("\n--- Top 10 Largest Items ---")

    largest_items = sorted(
        items,
        key=lambda x: x.size or 0,
        reverse=True
    )[:10]

    for i, item in enumerate(largest_items, start=1):
        size_mb = (item.size or 0) / (1024 ** 2)
        log(f"{i}. {item.title} ({item.type}) - {size_mb:.2f} MB")

    # ------------------------------
    # 6. Full Item List
    # ------------------------------
    log("\n--- All Items ---")

    for i, item in enumerate(items, start=1):
        log(f"{i}. {item.title} ({item.type}) | ID: {item.id}")

    # ------------------------------
    # 7. Recently Modified Items
    # ------------------------------
    log("\n--- Recently Modified Items ---")

    recent_items = sorted(
        items,
        key=lambda x: x.modified or 0,
        reverse=True
    )[:5]

    for item in recent_items:
        mod_time = datetime.fromtimestamp(item.modified / 1000)
        log(f"{item.title} - Last modified: {mod_time}")

    # ------------------------------
    # 8. Stale Items (1+ year)
    # ------------------------------
    log("\n--- Items Not Modified in 1+ Year ---")

    one_year_ms = 365 * 24 * 60 * 60 * 1000
    now_ms = datetime.now().timestamp() * 1000

    stale_items = [
        item for item in items
        if item.modified and (now_ms - item.modified > one_year_ms)
    ]

    log(f"Found {len(stale_items)} stale items")

    # ------------------------------
    # 9. Missing Descriptions
    # ------------------------------
    log("\n--- Items Missing Descriptions ---")

    no_desc = [item for item in items if not item.description]

    log(f"{len(no_desc)} items missing descriptions")

    # ------------------------------
    # 10. SUMMARY
    # ------------------------------
    log("\n===== SUMMARY =====")
    log(f"User: {user.username}")
    log(f"Total Items: {item_count}")
    log(f"Total Storage (approx): {total_size_mb:.2f} MB")

    if largest_items:
        largest_name = largest_items[0].title
        largest_size = (largest_items[0].size or 0) / (1024 ** 2)
        log(f"Largest Item: {largest_name} ({largest_size:.2f} MB)")
    else:
        log("Largest Item: N/A")

    log("===================")

    # ------------------------------
    # EXPORT REPORT
    # ------------------------------
    export_report()


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    inspect_agol_content()
