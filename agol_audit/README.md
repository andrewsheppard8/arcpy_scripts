# AGOL Audit Toolkit (ArcGIS API for Python)

###### 

###### A modular auditing toolkit for analyzing ArcGIS Online (AGOL) content at both the user and organization level using the ArcGIS API for Python.

###### 

###### This project demonstrates multiple execution patterns—from simple scripts to automation-ready CLI workflows—while providing actionable insights into content usage, storage, and data quality.

# 

# 🔍 What This Toolkit Does

#### User-Level Auditing



###### Retrieves all items owned by a user

###### Calculates:

Total item count

Approximate storage usage

###### Provides:

Item type breakdown

Largest items

Recently modified items

Stale items (not modified in 1+ year)

Items missing descriptions



#### Organization-Level Auditing (Admin)



###### Iterates through all users in an AGOL organization

###### Calculates per-user:

Item counts

Storage usage

Identifies:

Top users by storage

Users with no content

Provides high-level organizational metrics



# 🧩 Execution Patterns



###### This repository intentionally includes multiple implementations to demonstrate how GIS automation evolves from simple scripts into scalable tools.



##### 1\. Hardcoded Script



Credentials stored directly in script

Best for quick testing and learning

Minimal setup required



Use Case:

Rapid prototyping or one-off analysis



##### 2\. Config-Based Script



Credentials stored in an external config.ini file

More secure and reusable than hardcoding

Suitable for repeatable workflows



Example config:



\[AGOL]

portal\_url = https://your-org.maps.arcgis.com

username = your\_username

password = your\_password



Use Case:

Reusable scripts in controlled environments



##### 3\. CLI Script (Automation-Ready)



Supports command-line arguments

Designed for automation and scheduling

Flexible execution patterns



Example Usage:



python agol\_audit\_cli.py --summary-only



ArcGIS Pro Python Environment (Recommended):



\& "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" "C:\\path\\agol\_audit\_cli.py" --summary-only



Use Case:

Task Scheduler, pipelines, automation workflows



##### 4\. Organization Admin Audit



Requires AGOL administrative privileges

Audits all users in the organization

Provides organization-wide metrics



Outputs:



Total users

Total items across org

Total storage usage

Top users by storage

Users with no content



Use Case:

Governance, storage optimization, platform oversight



# 📄 Output



###### All scripts generate a timestamped report:

agol\_report\_YYYYMMDD\_HHMMSS.txt



###### Admin script generates:

agol\_org\_audit\_YYYYMMDD\_HHMMSS.txt



###### Reports include:

Summary statistics

Detailed item/user breakdowns

Data quality indicators



# 🚀 Why This Project Matters



##### This toolkit demonstrates:



Multiple authentication and execution patterns

Secure credential management practices

Scalable automation design

Real-world AGOL auditing workflows



# 🔮 Future Improvements



CSV / Excel export for reporting

Organization-wide credit usage tracking

Filtering options (e.g., stale-only, large items only)

Parallel processing for large organizations

Dashboard integration (ArcGIS Dashboards / Streamlit)

Notification system (email / Teams)



# 👤 Author



Andrew Sheppard

GIS Developer | Solutions Engineer | Automation Specialist

