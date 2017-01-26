import arcpy
from Parcel import Parcel
from Error import Error
from Summary import Summary
from sys import exit
import os
import re
import csv
import LegacyCountyStats

#Tool inputs
in_fc = arcpy.GetParameterAsText(0)  #input feature class
outDir = arcpy.GetParameterAsText(1)  #output directory location
outName = arcpy.GetParameterAsText(2)  #output feature class name
outDirTxt = arcpy.GetParameterAsText(3)  #output directory error summary .txt file
coName = arcpy.GetParameterAsText(4)  #name of county making submission
#Run Original checks
totError = Error(in_fc,coName)

#Get the filepath of this script (for loading files relative to this path)  
dir = os.path.dirname(__file__)

#street name list
streetNames = [line.strip() for line in open(os.path.join(dir, 'V2_StreetName_Simplified.txt'), 'r')]

#street types domain list
streetTypes = [line.strip() for line in open(os.path.join(dir, 'V2_StreetType_Simplified.txt'), 'r')]

#unitid domain list
unitIdTypes = [line.strip() for line in open(os.path.join(dir, 'V2_UnitID_Simplified.txt'), 'r')]

#unit type domain list
unitTypes = [line.strip() for line in open(os.path.join(dir, 'V2_UnitType_Simplified.txt'), 'r')]

#placename domain list
placeNameDomains = [line.strip() for line in open(os.path.join(dir,'V2_PlacenameSummary_Simplified.txt'), 'r')]

#taxroll years to test (past,expected,future1,future2)
taxRollYears = [line.strip() for line in open(os.path.join(dir,'TaxRollYears.txt'), 'r')]

#suffix domain list
suffixDomains = [line.strip() for line in open(os.path.join(dir,'V2_SuffixDomains_Simplified.txt'), 'r')]

#prefix domain list
prefixDomains = [line.strip() for line in open(os.path.join(dir, 'V2_PrefixDomains_Simplified.txt'), 'r')]

#list of non-parcelid values found in field to ignore when checking for dups (and use in other functions)
pinSkips = [line.strip() for line in open(os.path.join(dir, 'V2_PinSkips.txt'), 'r')]

#list of field names 
fieldNames = ["OID@","SHAPE@","STATEID","PARCELID","TAXPARCELID","PARCELDATE","TAXROLLYEAR",
"OWNERNME1","OWNERNME2","PSTLADRESS","SITEADRESS","ADDNUMPREFIX","ADDNUM","ADDNUMSUFFIX","PREFIX","STREETNAME",
"STREETTYPE","SUFFIX","LANDMARKNAME","UNITTYPE","UNITID","PLACENAME","ZIPCODE","ZIP4","STATE","SCHOOLDIST",
"SCHOOLDISTNO","IMPROVED","CNTASSDVALUE","LNDVALUE","IMPVALUE","FORESTVALUE","ESTFMKVALUE","NETPRPTA","GRSPRPTA",
"PROPCLASS","AUXCLASS","ASSDACRES","DEEDACRES","GISACRES","CONAME","LOADDATE","PARCELFIPS","PARCELSRC",
"SHAPE@LENGTH","SHAPE@AREA","SHAPE@XY","GeneralElementErrors","AddressElementErrors","TaxrollElementErrors","GeometricElementErrors"]

schemaReq = {
	'STATEID':[['String'],[100]],
	'PARCELID':[['String'],[100]],
	'TAXPARCELID':[['String'],[100]],
	'PARCELDATE':[['String'],[25]],
	'TAXROLLYEAR':[['String'],[10]],
	'OWNERNME1':[['String'],[254]],
	'OWNERNME2':[['String'],[254]],
	'PSTLADRESS':[['String'],[200]],
	'SITEADRESS':[['String'],[200]],
	'ADDNUMPREFIX':[['String'],[50]],
	'ADDNUM':[['String'],[50]],
	'ADDNUMSUFFIX':[['String'],[50]],
	'PREFIX':[['String'],[50]],
	'STREETNAME':[['String'],[50]],
	'STREETTYPE':[['String'],[50]],
	'SUFFIX':[['String'],[50]],
	'LANDMARKNAME':[['String'],[50]],
	'UNITTYPE':[['String'],[50]],
	'UNITID':[['String'],[50]],
	'PLACENAME':[['String'],[100]],
	'ZIPCODE':[['String'],[50]],
	'ZIP4':[['String'],[50]],
	'STATE':[['String'],[50]],
	'SCHOOLDIST':[['String'],[50]],
	'SCHOOLDISTNO':[['String'],[50]],
	'IMPROVED':[['String'],[10]],
	'CNTASSDVALUE':[['String','Double'],[50,8]],
	'LNDVALUE':[['String','Double'],[50,8]],
	'IMPVALUE':[['String','Double'],[50,8]],
	'FORESTVALUE':[['String','Double'],[50,8]],
	'ESTFMKVALUE':[['String','Double'],[50,8]],
	'NETPRPTA':[['String','Double'],[50,8]],
	'GRSPRPTA':[['String','Double'],[50,8]],
	'PROPCLASS':[['String'],[150]],
	'AUXCLASS':[['String'],[150]],
	'ASSDACRES':[['String','Double'],[50,8]],
	'DEEDACRES':[['String','Double'],[50,8]],
	'GISACRES':[['String','Double'],[50,8]],
	'CONAME':[['String'],[50]],
	'LOADDATE':[['String'],[10]],
	'PARCELFIPS':[['String'],[10]],
	'PARCELSRC':[['String'],[50]],
}

#bad characters dictionary
fieldNamesBadChars = {
"PARCELID": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")"],
"TAXPARCELID": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")"],
"PARCELDATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\-"],
"TAXROLLYEAR": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',"\-"],
"OWNERNME1": ["\n","\r"],
"OWNERNME2": ["\n","\r"],
"PSTLADRESS": ["\n","\r"],
"SITEADRESS": ["\n","\r"],
"ADDNUMPREFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ADDNUM": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ADDNUMSUFFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")",',','.',"\-"],
"PREFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"STREETNAME": ["\n","\r","$","^","=","<",">","@","#","%","?","!","*","~","(",")"],
"STREETTYPE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"SUFFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"LANDMARKNAME": ["\n","\r"],
"UNITTYPE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"UNITID": ["\n","\r","$","^","=","<",">","@","%","&","?","`","!","*","~","(",")","\\",'/',','],
"PLACENAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"ZIPCODE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ZIP4": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"STATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"SCHOOLDIST": ["\n","\r","$","^","=","<",">","@","#","%","&","?","!","*","~","(",")","\\",'/',','],
"SCHOOLDISTNO": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"IMPROVED": ["\n","\r","$","^","=","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"CNTASSDVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"LNDVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"IMPVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"FORESTVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"ESTFMKVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"NETPRPTA": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"GRSPRPTA": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"PROPCLASS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/','.',"\-"],
"AUXCLASS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/','.',"\-"],
"ASSDACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"DEEDACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"GISACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"CONAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"LOADDATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")",',','.','\-'],
"PARCELFIPS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"PARCELSRC": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"]
}

#list of non-parcelid values found in field to ignore when checking for dups
#pinSkips = ["ALLEY","CANAL","CE","CONDO","CREEK","CTH","CTH C","CTH G","CTH H","CTH H","GAP","HYDRO","LAKE","LCE","MARSH",
#"MOUND","NIR","NOPID","OL","OTHER","OUT","PARK","PIER","POND","PVT","RIVER","ROAD","ROW","RR","RVR","RW","STATE","STH","TBD",
#"TOA","TOB","TOF","TOJ","TOL","TOM","TOWN","TRAIL","TRIBE","UNK","USH","WALK","WATER","WELL","WET","WPS","WVIC"]

#testing prefix domain list
#prefixDomains = ["CTH", "STH", "USH", "W CTH", "S CTH", "E CTH", "N CTH", "W STH", "S STH", "E STH", "N STH", "W USH", "S USH", "E USH", "N USH", "N", "E", "S", "W"]

#testing suffix domain list
#suffixDomains = ["N", "E", "S", "W"]

#taxroll years to test (past,expected,future1,future2)
#taxRollYears = ['2015','2016','2017','2018']

#acceptable COP domains
copDomains = ['1','2','3','4','5','6','7','5M','M']

#acceptable AUXCOP domains
auxDomins = ['W1','W2','W3','W4','W5','W6','W7','W8','X1','X2','X3','X4','M']

#schooldist and schooldistno dictionaries
reader = csv.reader(open(os.path.join(dir, 'school_district_codes.csv'),'rU'))
schoolDist_nameNo_dict = {}
schoolDist_noName_dict = {}
for row in reader:
	k,v = row
	schoolDist_noName_dict[k] = v
	schoolDist_nameNo_dict[v] = k

arcpy.AddMessage("School Dist Dictionaries created...")

#CONAME and FIPS dictionaries
reader = csv.reader(open(os.path.join(dir, 'CoNameFips.csv')))
county_nameNo_dict = {}
county_noName_dict = {}
for row in reader:
	k, v = row
	county_nameNo_dict[k] = v
	county_noName_dict[v] = k

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

#lists for collecting parcelids and taxparcelids for checking for dups
uniquePinList = []
uniqueTaxparList = []

#Copy feature class, add new fields for error reporting
arcpy.AddMessage("Writing to Memory")
output_fc_temp = os.path.join("in_memory", "WORKING")
arcpy.AddMessage(output_fc_temp)
arcpy.Delete_management("in_memory")
dynamic_workspace = "in_memory"
arcpy.FeatureClassToFeatureClass_conversion(in_fc,dynamic_workspace, "WORKING")

# Check feature class for all expected fields, note fields that don't match requirements or excess fields that need to be removed...
arcpy.AddMessage("Checking for all fields")
fieldList = arcpy.ListFields(output_fc_temp)
fieldDictNames = {}
missingFields = []
excessFields = []
var = True
fieldListPass = ["OID","OID@","SHAPE","SHAPE@","SHAPE_LENGTH","SHAPE_AREA","SHAPE_XY","SHAPE@LENGTH","SHAPE@AREA","SHAPE@XY","LONGITUDE","LATITUDE","GENERALELEMENTERRORS","ADDRESSELEMENTERRORS","TAXROLLELEMENTERRORS","GEOMETRICELEMENTERRORS"]
for field in fieldList:
        fieldDictNames[field.name] = [[field.type],[field.length]]

for field in fieldDictNames:
	if field.upper() not in fieldListPass:
		if field not in schemaReq.keys():
			excessFields.append(field)
			var = False
		elif fieldDictNames[field][0][0] not in schemaReq[field][0] or fieldDictNames[field][1][0] not in schemaReq[field][1]:
			missingFields.append(field)
			var = False

if var == False:	
	arcpy.AddMessage("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
	arcpy.AddMessage("A NUMBER OF FIELDS DO NOT MEET THE PARCEL SCHEMA REQUIREMENTS.\n")
	if len(missingFields) > 0:
		arcpy.AddMessage("THE PROBLEMATIC FIELDS INCLUDE: (" + str(missingFields).strip("[").strip("]").replace('u','') + ")\n")
		arcpy.AddMessage("------->> PLEASE CHECK TO MAKE SURE THE NAMES, DATA TYPES, AND LENGTHS MATCH THE SCHEMA REQUIREMENTS.\n")
	if len(excessFields) > 0:
		arcpy.AddMessage("THE EXCESS FIELDS INCLUDE: (" + str(excessFields).strip("[").strip("]").replace('u','') + ")\n")
		arcpy.AddMessage("------->> PLEASE REMOVED FIELDS THAT ARE NOT IN THE PARCEL ATTRIBUTE SCHEMA.\n")
	arcpy.AddMessage("PLEASE MAKE NEEDED ALTERATIONS TO THESE FIELDS AND RUN THE TOOL AGAIN.\n")
	arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
	exit()

#Adding new fields for error reporting.  We can change names, lenght, etc...
arcpy.AddMessage("Adding Error Fields")
arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 1000)

#Call all pre-cursor test functions
totError = Error.checkCRS(totError, output_fc_temp)

#Create update cursor then use it to iterate through records in feature class
arcpy.AddMessage("Testing the data for various attribute error types.")
with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:	
	for row in cursor:
		#Construct the Parcel object for the row
		currParcel = Parcel(row, fieldNames)
		#Execute in-cursor error tests
		totError,currParcel = Error.checkGeometricQuality(totError,currParcel)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"addnum","address", True) 
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"parcelfips","general", False)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"zipcode","address", True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"zip4","address", True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"cntassdvalue","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"lndvalue","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"impvalue","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"forestvalue","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"estfmkvalue","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"netprpta","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"grsprpta","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"assdacres","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"deedacres","tax",True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"gisacres","tax",True)
		totError,currParcel = Error.checkIsDuplicate(totError,currParcel,"parcelid","general", True, pinSkips, uniquePinList)
		totError,currParcel = Error.checkIsDuplicate(totError,currParcel,"taxparcelid","general", True, pinSkips, uniqueTaxparList)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"prefix","address",True, prefixDomains)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"streettype","address",True,streetTypes)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"unittype","address",True,unitTypes)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"unitid","address",True,unitIdTypes)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"placename","general",True,placeNameDomains)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"suffix","address",True, suffixDomains)
		totError,currParcel = Error.trYear(totError,currParcel,"taxrollyear","parcelid","tax",False,pinSkips,taxRollYears)
		totError,currParcel = Error.streetNameCheck(totError,currParcel,"streetname","siteadress","address",True,streetNames)
		totError,currParcel = Error.zipCheck(totError,currParcel,"zipcode","address",True)
		totError,currParcel = Error.impCheck(totError,currParcel,"improved","impvalue","tax")
		totError,currParcel = Error.badChars(totError,currParcel,fieldNames,fieldNamesBadChars,'general')
		totError,currParcel = Error.classOfPropCheck(totError,currParcel,'propclass',copDomains,'tax',True)
		totError,currParcel = Error.classOfPropCheck(totError,currParcel,'auxclass',auxDomins,'tax',True)
		totError,currParcel = Error.matchContrib(totError,currParcel,"coname","parcelfips","parcelsrc",county_nameNo_dict,county_noName_dict,"general",False)
		totError,currParcel = Error.schoolDistCheck(totError,currParcel,"parcelid","schooldist","schooldistno",schoolDist_noName_dict,schoolDist_nameNo_dict,"tax",pinSkips,False)
		totError,currParcel = Error.fieldCompleteness(totError,currParcel,fieldNames,fieldListPass,v3CompDict)
		totError,currParcel = Error.fieldCompletenessComparison(totError,currParcel,fieldNames,fieldListPass,v3CompDict,getattr(LegacyCountyStats, (coName.replace(" ","_"))+"LegacyDict"))
		#End of loop, finalize errors with the writeErrors function, then clear parcel
		currParcel.writeErrors(row,cursor, fieldNames)
		currParcel = None


# Write all summary-type errors to file via the Summary class
summaryTxt = Summary()
Summary.writeSummaryTxt(summaryTxt,outDirTxt,outName,totError)

# User messages (for testing):
arcpy.AddMessage("General Errors: " + str(totError.generalErrorCount))
arcpy.AddMessage("Geometric Errors: " + str(totError.geometricErrorCount))
arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))

#Write feature class from memory back out to hard disk
arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,outDir,outName)
