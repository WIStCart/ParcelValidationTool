import arcpy
from Parcel import Parcel
import os
import re
import csv


#Tool inputs
in_fc = arcpy.GetParameterAsText(0)  #input feature class
outDir = arcpy.GetParameterAsText(1)  #output directory location
outName = arcpy.GetParameterAsText(2)  #output feature class name

#Copy feature class, add new fields for error reporting
arcpy.AddMessage("Writing to Memory")
output_fc_temp = os.path.join("in_memory", "WORKING")
arcpy.AddMessage(output_fc_temp)
arcpy.Delete_management("in_memory")
dynamic_workspace = "in_memory"
arcpy.FeatureClassToFeatureClass_conversion(in_fc,dynamic_workspace, "WORKING")

#Adding new fields for error reporting.  We can change names, lenght, etc...
arcpy.AddMessage("Adding Error Fields")
arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 250)
arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 250)
arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 250)
arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 250)

#Create update cursor


#Iterate through records in feature class
#	Create a parcel object
#	Either call individual error checking methods (Error.GeomError.checkGeometry(Parcel)) or grouped methods in the parcel class (parcel.checkGeomErrors())
#	Write out errors to record
#	Del parcel object to conserve mem

#Write general error report

#Write feature class from memory back out to hard disk
arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,outDir,outName)
