import arcpy,os,re,csv,collections
from Parcel import Parcel
from Error import Error
from Summary import Summary
from sys import exit
import LegacyCountyStats
from externalDicts import *

#Collect tool inputs
inputNameList = ['isSearchable','isFinal','county','inFC','outDir','outName','outSummaryDir','exportModel','inExportTable','inExportGeometryFC','inXREFTable','tablePIN','geomPin','xmlPIN','xrefTablePIN','xrefGeomPIN','subName','subEmail','condoModel','cert','isNameRedact','redactPolicy','zoningGenType','zoningGenFC','zoningFarmType','zoningFarmFC','zoningShoreType','zoningShoreFC','zoningFloodType','zoningFloodFC','zoningAirType','zoningAirFC','isCOPDomainV3','copClass1','copClass2','copClass3','copClass4','copClass5','copClass5M','copClass6','copClass7','auxClassW1','auxClassW2','auxClassW3','auxClassW4','auxClassW5','auxClassW6','auxClassW7','auxClassW8','auxClassW9','auxClassX1','auxClassX2','auxClassX3','auxClassX4','PARCELID','TAXPARCELID','PARCELDATE','TAXROLLYEAR','OWNERNME1','OWNERNME2','PSTLADRESS','SITEADRESS','ADDNUMPREFIX','ADDNUM','ADDNUMSUFFIX','PREFIX','STREETNAME','STREETTYPE','SUFFIX','LANDMARKNAME','UNITTYPE','UNITID','PLACENAME','ZIPCODE','ZIP4','STATE','SCHOOLDIST','SCHOOLDISTNO','IMPROVED','CNTASSDVALUE','LNDVALUE','IMPVALUE','FORESTVALU','ESTFMKVALUE','NETPRPTA','GRSPRPTA','PROPCLASS','AUXCLASS','ASSDACRES','DEEDACRES','GISACRES','CONAME','PARCELFIPS','PARCELSRC']
inputDict = collections.OrderedDict()
i = 0
for inputName in inputNameList:
	inputDict[inputName] = arcpy.GetParameterAsText(i)
	i += 1
	arcpy.AddMessage(inputName + "=" + inputDict[inputName])

#Create summary object
summary = Summary()

if inputDict['isSearchable'] == 'true':

	#Load files for current domain lists 
	directory = os.path.dirname(__file__)
	streetNames = [line.strip() for line in open(os.path.join(directory, 'V2_StreetName_Simplified.txt'), 'r')] #street name list
	streetTypes = [line.strip() for line in open(os.path.join(directory, 'V2_StreetType_Simplified.txt'), 'r')] #street types domain list
	unitIdTypes = [line.strip() for line in open(os.path.join(directory, 'V2_UnitId_Simplified.txt'), 'r')] #unitid domain list
	unitTypes = [line.strip() for line in open(os.path.join(directory, 'V2_UnitType_Simplified.txt'), 'r')] #unit type domain list
	placeNameDomains = [line.strip() for line in open(os.path.join(directory,'V2_PlacenameSummary_Simplified.txt'), 'r')] #placename domain list
	taxRollYears = [line.strip() for line in open(os.path.join(directory,'TaxRollYears.txt'), 'r')] #taxroll years to test (past,expected,future1,future2)
	suffixDomains = [line.strip() for line in open(os.path.join(directory,'V2_SuffixDomains_Simplified.txt'), 'r')] #suffix domain list
	prefixDomains = [line.strip() for line in open(os.path.join(directory, 'V2_PrefixDomains_Simplified.txt'), 'r')] #prefix domain list
	pinSkips = [line.strip() for line in open(os.path.join(directory, 'V2_PinSkips.txt'), 'r')] #list of non-parcelid values found in field to ignore when checking for dups (and use in other functions)

	reader = csv.reader(open(os.path.join(directory, 'school_district_codes.csv'),'rU')) #school district code list
	schoolDist_nameNo_dict = {}
	schoolDist_noName_dict = {}
	for row in reader:
		k,v = row
		schoolDist_noName_dict[k] = v
		schoolDist_nameNo_dict[v] = k

	reader = csv.reader(open(os.path.join(directory, 'CoNameFips.csv'))) #CONAME and FIPS list
	county_nameNo_dict = {}
	county_noName_dict = {}
	for row in reader:
		k,v = row
		county_nameNo_dict[k] = v
		county_noName_dict[v] = k

	#Create error object
	totError = Error(inputDict['inFC'],inputDict['county'])

	#lists for collecting parcelids and taxparcelids for checking for dups
	uniquePinList = []
	uniqueTaxparList = []

	#Copy feature class, add new fields for error reporting
	arcpy.AddMessage("Writing to Memory")
	output_fc_temp = os.path.join("in_memory", "WORKING")
	arcpy.AddMessage(output_fc_temp)
	arcpy.Delete_management("in_memory")
	dynamic_workspace = "in_memory"
	arcpy.FeatureClassToFeatureClass_conversion(inputDict['inFC'],dynamic_workspace, "WORKING")

	# Check feature class for all expected fields, note fields that don't match requirements or excess fields that need to be removed...
	arcpy.AddMessage("Checking for all fields")
	fieldList = arcpy.ListFields(output_fc_temp)
	fieldDictNames = {}
	missingFields = []
	excessFields = []
	var = True

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
			totError,currParcel = Error.fieldCompletenessComparison(totError,currParcel,fieldNames,fieldListPass,v3CompDict,getattr(LegacyCountyStats, (inputDict['county'].replace(" ","_"))+"LegacyDict"))

			#End of loop, finalize errors with the writeErrors function, then clear parcel
			currParcel.writeErrors(row,cursor, fieldNames)
			currParcel = None

	# Write all summary errors to file
	Summary.writeSummaryTxt(summary,inputDict['outSummaryDir'],inputDict['outName'],totError)
	arcpy.AddMessage(inputDict['isFinal'])
	#Write the ini file if final
	if inputDict['isFinal'] == 'true':
		summary.writeIniFile(inputDict,totError)

	arcpy.AddMessage("General Errors: " + str(totError.generalErrorCount))
	arcpy.AddMessage("Geometric Errors: " + str(totError.geometricErrorCount))
	arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
	arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))

	#Write feature class from memory back out to hard disk
	arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,inputDict['outDir'],inputDict['outName'])
#Export
else:
	totError = Error(inputDict['inExportGeometryFC'],inputDict['county'])
	summary.writeIniFile(inputDict,totError)