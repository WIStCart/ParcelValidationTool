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
outDirTxt = arcpy.GetParameterAsText(3)  #output directory error summary .txt file

#Run Original checks
totError = Error()

#list of field names 
fieldNames = ["OID@","SHAPE@","STATEID","PARCELID","TAXPARCELID","PARCELDATE","TAXROLLYEAR",
"OWNERNME1","OWNERNME2","PSTLADRESS","SITEADRESS","ADDNUMPREFIX","ADDNUM","ADDNUMSUFFIX","PREFIX","STREETNAME",
"STREETTYPE","SUFFIX","LANDMARKNAME","UNITTYPE","UNITID","PLACENAME","ZIPCODE","ZIP4","STATE","SCHOOLDIST",
"SCHOOLDISTNO","IMPROVED","CNTASSDVALUE","LNDVALUE","IMPVALUE","FORESTVALUE","ESTFMKVALUE","NETPRPTA","GRSPRPTA",
"PROPCLASS","AUXCLASS","ASSDACRES","DEEDACRES","GISACRES","CONAME","LOADDATE","PARCELFIPS","PARCELSRC",
"SHAPE@LENGTH","SHAPE@AREA","GeneralElementErrors","AddressElementErrors","TaxrollElementErrors","GeometricElementErrors"]

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
		totError,currParcel = Error.testCheckNum(totError,currParcel) # This line can be deleted in the future we are simply calling the testCheckNum() function twice here for sake of planting duplicate errors to be tested by writeErrors() 
		#arcpy.AddMessage(currParcel.addressErrors)
		#arcpy.AddMessage(str(totError.addressErrorCount))

		#End of loop, clear parcel
		currParcel.writeErrors(row,cursor, fieldNames)
		currParcel = None

#Write general error report
errorSummaryFile = open(outDirTxt + "/" + outName + "_ValidationSummary.txt","w")
arcpy.AddMessage("Creating Validation Summary here: " + outDirTxt + "/" + outName + "_ValidationSummary.txt")
errorSummaryFile.write(outDirTxt + "\\" + outName + "_ValidationSummary.txt" + "\n")
errorSummaryFile.write("Validation Summary Table: " + "\n")
errorSummaryFile.write("This validation summary table contains an overview of any errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary." + "\n\n")
errorSummaryFile.write("In-line errors - The following lines summarize the element-specific errors that were found while validating your parcel dataset. The stats below are meant as a means of reviewing the output. Please see the " + "GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields in the output feature class to address these errors individually."+ "\n")
errorSummaryFile.write("	General Errors: " + str(totError.genErrorCount) + "\n")
errorSummaryFile.write("	Geometric Errors: " + str(totError.geomErrorCount) + "\n")
errorSummaryFile.write("	Address Errors: " + str(totError.addressErrorCount) + "\n")
errorSummaryFile.write("	Tax Errors: " + str(totError.taxErrorCount) + "\n")
errorSummaryFile.write("* Within: " + outDirTxt + "\\" + outName  + "\n")

# User messages:
arcpy.AddMessage("General Errors: " + str(totError.genErrorCount))
arcpy.AddMessage("Geometric Errors: " + str(totError.geomErrorCount))
arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))

#Write feature class from memory back out to hard disk
#arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,outDir,outName)
