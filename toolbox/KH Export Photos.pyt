"""
Author: Colin T. Stiles, GISP
Version: 0.2
Last Edited Data: 2025-05-05
Description: This tool extracts attachments (i.e., photos) from GPS point data stored in a file geodatabase 
that was collected from Field Maps.

Args:
    att_table (DETable):
        Input table that stores the attachments in the file geodatabase.
    output_folder (DEFolder):
        Path to the folder where the output files will be saved.
"""

# Import system modules
import arcpy
from arcpy import da
import os
from typing import List, Optional

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Export Photos"
        self.alias = "ExportPhotos"
        self.description = "Exports photo attachments from file geodatabase table."
        self.canRunInBackground = True
        self.category = "Export Photos"

        # List of tool classes associated with this toolbox
        self.tools = [ExportPhotos]

class ExportPhotos:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Export Photos"
        self.alias = "ExportPhotos"
        self.description = "Exports photo attachments from file geodatabase table."
        self.canRunInBackground = True
        self.category = "Export Photos"

    def getParameterInfo(self):
        """Define the tool parameters."""
        # Input attachments table (required)
        param0 = arcpy.Parameter(
            displayName="Attachments Table",
            name="att_table",
            datatype="DETable",
            parameterType="Required",
            direction="Input",
        )

        # Output folder (required)
        param1 = arcpy.Parameter(
            displayName="Output Folder",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        )

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        att_table = parameters[0].valueAsText
        output_folder = parameters[1].valueAsText

        exported_files = self.export_attachments(att_table, output_folder)

        if exported_files is None:
            arcpy.AddError("Exporting attachments failed.")
        elif not exported_files:
            arcpy.AddWarning("No attachments were found in the input table.")
        else:
            arcpy.AddMessage(f"Successfully exported {len(exported_files)} attachments to: {output_folder}")
            return # Exit if the result is unexpected
        
    def export_attachments(self, att_table: str, output_folder: str):
        """Exports photo attachments from a file geodatabase.
            
        Args:
            att_table (str):
                Path to the input table that stores the attachments.
            output_folder (str):
                Path to the folder where the output files will be saved.
        """
        exported_files = []
        try:
            # Check if the input table exists
            if not arcpy.Exists(att_table):
                arcpy.AddError(f"Attachments table {att_table} does not exist.")
                return
            
            # Check if output_folder exists, if not, create it
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                arcpy.AddMessage(f"Created directory: {output_folder}")

            # Use SearchCursor to extract the attachemnts
            with da.SearchCursor(att_table, ['DATA', 'ATT_NAME', 'ATTACHMENTID']) as cursor:
                for item in cursor:
                    attachment = item[0]  # Attachment binary data
                    attachment_name = item[1]  # Attachment name
                    attachment_id = item[2]  # Attachment ID

                    # Create filename with ATT# format
                    filenum = f"ATT{attachment_id}_"
                    filename = filenum + attachment_name
                    file_path = os.path.join(output_folder, filename)

                    # Write the binary data to a file
                    with open(file_path, 'wb') as file:
                        file.write(attachment.tobytes())
                
                    arcpy.AddMessage(f"Saved attachment: {filename}")
                    exported_files.append(file_path)
                else:
                    arcpy.AddMessage(f"Attachment with ID {attachment_id} has no data and was skipped.")

            return exported_files
        
        except Exception as e:
            arcpy.AddError(f"Error while extracting attachments: {str(e)}")
            return None
