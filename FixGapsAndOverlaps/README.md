\n Removes gaps and overlaps in parcel layer of mdb files. Circularuty and suspiciousness of the cleaned features ae calculated. This is to detect sliver polygons which needs to be merged to adjacent parcels. The segments and construction layer are populated with the corresponding parcelid. The mdb is compacted (compressed) to reduce file size.

Requires arcpy (available through arcgis 10.x) and saex. Python executable must be from the arcgis installation.

Input: Folder path

Process: This scripts loops though each mdb file in the path recursively and fixes any gaps or overlaps in the parcel layer. BLANK84 template is used in processing so the final output is in this template. D:\\DataCleanTemp is created as temporary workspace and deleted at the end. If due to error this folder is not deleted, then it may have to be deleted manually.

Output: mdbs in the folder do not have gaps or overlap in parcel layer. The mdbs then need to be processed for sliver polygons.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts
