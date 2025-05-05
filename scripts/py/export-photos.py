"""
Last edited by: CTS
Last edited on: 10/15/2024
Version: Python 3.11 | Packaged by Anaconda
Description: This tool extracts attachments (ie, photos) from GPS point data stored in a file geodatabase.
"""

import arcpy
from arcpy import da
import os

def extract_attachments(inTable, fileLocation):
    try:
        # Check if input table exists
        if not arcpy.Exists(inTable):
            arcpy.AddError(f"Input table {inTable} does not exist.")
            return

        # Check if fileLocation exists, if not create it
        if not os.path.exists(fileLocation):
            os.makedirs(fileLocation)
            arcpy.AddMessage(f"Created directory: {fileLocation}")

        # Use SearchCursor to extract the attachments
        with da.SearchCursor(inTable, ['DATA', 'ATT_NAME', 'ATTACHMENTID']) as cursor:
            for item in cursor:
                attachment = item[0]  # Attachment binary data
                attachment_name = item[1]  # Attachment name
                attachment_id = item[2]  # Attachment ID

                # Create filename with ATT# format
                filenum = f"ATT{attachment_id}_"
                filename = filenum + attachment_name
                file_path = os.path.join(fileLocation, filename)

                # Write the binary data to a file
                with open(file_path, 'wb') as file:
                    file.write(attachment.tobytes())
                
                arcpy.AddMessage(f"Saved attachment: {filename}")

    except Exception as e:
        arcpy.AddError(f"Error while extracting attachments: {str(e)}")

# Main code: Get parameters from user inputs
inTable = arcpy.GetParameterAsText(0)
fileLocation = arcpy.GetParameterAsText(1)

# Validate input parameters
if not inTable or not fileLocation:
    arcpy.AddError("Input table and file location are required.")
else:
    extract_attachments(inTable, fileLocation)

