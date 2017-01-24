import arcpy
from Parcel import Parcel
from Error import Error
from sys import exit
import os
import re
import csv
import json

#Tool inputs
in_fc = arcpy.GetParameterAsText(0)  #input feature class
outName = arcpy.GetParameterAsText(1)  #output feature class name
outDirTxt = arcpy.GetParameterAsText(2)  #output directory error summary .txt file


#list of field names
fieldNames = ["OID@","SHAPE@","STATEID","PARCELID","TAXPARCELID","PARCELDATE","TAXROLLYEAR",
"OWNERNME1","OWNERNME2","PSTLADRESS","SITEADRESS","ADDNUMPREFIX","ADDNUM","ADDNUMSUFFIX","PREFIX","STREETNAME",
"STREETTYPE","SUFFIX","LANDMARKNAME","UNITTYPE","UNITID","PLACENAME","ZIPCODE","ZIP4","STATE","SCHOOLDIST",
"SCHOOLDISTNO","IMPROVED","CNTASSDVALUE","LNDVALUE","IMPVALUE","FORESTVALUE","ESTFMKVALUE","NETPRPTA","GRSPRPTA",
"PROPCLASS","AUXCLASS","ASSDACRES","DEEDACRES","GISACRES","CONAME","LOADDATE","PARCELFIPS","PARCELSRC",
"SHAPE@LENGTH","SHAPE@AREA","SHAPE@XY","GeneralElementErrors","AddressElementErrors","TaxrollElementErrors","GeometricElementErrors"]

countyArray = ["ADAMS","ASHLAND","BARRON","BAYFIELD","BROWN","BUFFALO","BURNETT","CALUMET","CHIPPEWA","CLARK","COLUMBIA","CRAWFORD","DANE","DODGE","DOOR","DOUGLAS","DUNN","EAU CLAIRE","FLORENCE","FOND DU LAC","FOREST","GRANT","GREEN","GREEN LAKE","IOWA","IRON","JACKSON","JEFFERSON","JUNEAU","KENOSHA","KEWAUNEE","LA CROSSE","LAFAYETTE","LANGLADE","LINCOLN","MANITOWOC","MARATHON","MARINETTE","MARQUETTE","MENOMINEE","MILWAUKEE","MONROE","OCONTO","ONEIDA","OUTAGAMIE","OZAUKEE","PEPIN","PIERCE","POLK","PORTAGE","PRICE","RACINE","RICHLAND","ROCK","RUSK","SAUK","SAWYER","SHAWANO","SHEBOYGAN","ST CROIX","TAYLOR","TREMPEALEAU","VERNON","VILAS","WALWORTH","WASHBURN","WASHINGTON","WAUKESHA","WAUPACA","WAUSHARA","WINNEBAGO","WOOD"]

def runStatsOn(countyName):
	
	#dictionary for V3 completeness collection
	v3CompDict = {
		'STATEID':0,
		'PARCELID':0,
		'TAXPARCELID':0,
		'PARCELDATE':0,
		'TAXROLLYEAR':0,
		'OWNERNME1':0,
		'OWNERNME2':0,
		'PSTLADRESS':0,
		'SITEADRESS':0,
		'ADDNUMPREFIX':0,
		'ADDNUM':0,
		'ADDNUMSUFFIX':0,
		'PREFIX':0,
		'STREETNAME':0,
		'STREETTYPE':0,
		'SUFFIX':0,
		'LANDMARKNAME':0,
		'UNITTYPE':0,
		'UNITID':0,
		'PLACENAME':0,
		'ZIPCODE':0,
		'ZIP4':0,
		'STATE':0,
		'SCHOOLDIST':0,
		'SCHOOLDISTNO':0,
		'IMPROVED':0,
		'CNTASSDVALUE':0,
		'LNDVALUE':0,
		'IMPVALUE':0,
		'FORESTVALUE':0,
		'ESTFMKVALUE':0,
		'NETPRPTA':0,
		'GRSPRPTA':0,
		'PROPCLASS':0,
		'AUXCLASS':0,
		'ASSDACRES':0,
		'DEEDACRES':0,
		'GISACRES':0,
		'CONAME':0,
		'LOADDATE':0,
		'PARCELFIPS':0,
		'PARCELSRC':0,
	}

	#Copy feature class, add new fields for error reporting
	arcpy.AddMessage("Writing to memory using the following parameters:")
	output_fc_temp = os.path.join("in_memory", "WORKING")
	arcpy.AddMessage("Output path: " + output_fc_temp)
	arcpy.Delete_management("in_memory")
	dynamic_workspace = "in_memory"
	expression =   "CONAME = '"+countyName+"'"
	arcpy.AddMessage("Query expression: " + expression)
	# Execute FeatureClassToFeatureClass
	arcpy.FeatureClassToFeatureClass_conversion(in_fc,dynamic_workspace, "WORKING", expression)
	
	#Run primary checks
	totError = Error(output_fc_temp,countyName)
	
	# Fields that we do not need to collect summary stats on
	fieldListPass = ["OID","OID@","SHAPE","SHAPE@","SHAPE_LENGTH","SHAPE_AREA","SHAPE_XY","SHAPE@LENGTH","SHAPE@AREA","SHAPE@XY","GENERALELEMENTERRORS","ADDRESSELEMENTERRORS","TAXROLLELEMENTERRORS","GEOMETRICELEMENTERRORS"]

	#Adding new fields for error reporting.  We can change names, lenght, etc... (need to keep these, BUT SETTING THEIR LENGTH TO 1)
	arcpy.AddMessage("Adding Error Fields")
	arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 1)
	arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 1)
	arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 1)
	arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 1)

	#Create update cursor then use it to iterate through records in feature class
	arcpy.AddMessage("Testing the data for field completeness ("+countyName+" COUNTY)")
	with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:	
		for row in cursor:
			#Construct the Parcel object for the row
			currParcel = Parcel(row, fieldNames)
			#compile completeness stats via the Error class function
			totError,currParcel = Error.fieldCompleteness(totError,currParcel,fieldNames,fieldListPass,v3CompDict)
			#End of loop, clear parcel
			currParcel = None
	# Create a .csv and then write the dictionary to it  
	fd = open(os.path.join(outDirTxt, outName+".py"),'a')
	statString = ((countyName.replace(" ","_"))+"LegacyDict = ")+str(v3CompDict)
	fd.write(statString+'\n')
	fd.close()
	# testing code for validation tool (converting string back into usable dict):
	'''statArray = statString.split("|")
	reincarnatedString = (statArray[1].replace("'",'"'))
	reincarnatedCounty = (statArray[0])
	reincarnatedDict = json.loads(reincarnatedString) # REQUIRES import json
	for value in reincarnatedDict:
			arcpy.AddMessage(reincarnatedCounty )
			arcpy.AddMessage(value)
			arcpy.AddMessage(reincarnatedDict[value])'''
	# Clear memory to free up space for other county processing
	arcpy.Delete_management("in_memory")
	
for countyName in countyArray:
	arcpy.AddMessage("ABOUT TO RUN STATS ON: " +countyName)
	runStatsOn(countyName)