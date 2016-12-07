import arcpy
from Parcel import Parcel
from Error import Error
import os
import re
import csv


#Tool inputs
in_fc = arcpy.GetParameterAsText(0)  #input feature class
outDir = arcpy.GetParameterAsText(1)  #output directory location
outName = arcpy.GetParameterAsText(2)  #output feature class name

#Run Original checks
totError = Error()


#list of field names 
fieldNames = ["OID@","SHAPE@","STATEID","PARCELID","TAXPARCELID","PARCELDATE","TAXROLLYEAR",
"OWNERNME1","OWNERNME2","PSTLADRESS","SITEADRESS","ADDNUMPREFIX","ADDNUM","ADDNUMSUFFIX","PREFIX","STREETNAME",
"STREETTYPE","SUFFIX","LANDMARKNAME","UNITTYPE","UNITID","PLACENAME","ZIPCODE","ZIP4","STATE","SCHOOLDIST",
"SCHOOLDISTNO","IMPROVED","CNTASSDVALUE","LNDVALUE","IMPVALUE","FORESTVALUE","ESTFMKVALUE","NETPRPTA","GRSPRPTA",
"PROPCLASS","AUXCLASS","ASSDACRES","DEEDACRES","GISACRES","CONAME","LOADDATE","PARCELFIPS","PARCELSRC",
"SHAPE@LENGTH","SHAPE@AREA","GeneralElementErrors","AddressElementErrors","TaxrollElementErrors","GeometricElementErrors"]

#This is just a comment, that has been edited...
#Just another comment, from Codie.

#Copy feature class, add new fields for error reporting
arcpy.AddMessage("Writing to Memory")
output_fc_temp = os.path.join("in_memory", "WORKING")
arcpy.AddMessage(output_fc_temp)
arcpy.Delete_management("in_memory")
dynamic_workspace = "in_memory"
arcpy.FeatureClassToFeatureClass_conversion(in_fc,dynamic_workspace, "WORKING")

#Adding new fields for error reporting.  We can change names, lenght, etc...
arcpy.AddMessage("Adding Error Fields")
arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 250)
arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 250)
arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 250)
arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 250)

#Create update cursor
#Iterate through records in feature class
#	Create a parcel object
#	Either call individual error checking methods (Error.GeomError.checkGeometry(Parcel)) or grouped methods in the parcel class (parcel.checkGeomErrors())
#	Write out errors to record
#	Del parcel object to conserve mem
with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:
	
	for row in cursor:
		currParcel = Parcel(row)
		#arcpy.AddMessage(currParcel.addnum)
		totError,currParcel = Error.testCheckNum(totError,currParcel)
		#arcpy.AddMessage(currParcel.addressErrors)
		#arcpy.AddMessage(str(totError.addressErrorCount))
		row[fieldNames.index("AddressElementErrors")] = "currParcel.addressErrors"
		cursor.updateRow(row)


		#End of loop, clear parcel
		currParcel = None

#Write general error report
arcpy.AddMessage("General Errors: " + str(totError.genErrorCount))
arcpy.AddMessage("Geometric Errors: " + str(totError.geomErrorCount))
arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))
#Write feature class from memory back out to hard disk
#arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,outDir,outName)
