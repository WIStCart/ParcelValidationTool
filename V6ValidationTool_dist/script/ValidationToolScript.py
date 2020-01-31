import arcpy,os,re,csv,collections,urllib2
from Parcel import Parcel
from Error import Error
from Summary import Summary
from sys import exit
import LegacyCountyStats
from externalDicts import *
import os

#Collect tool inputs
# FROM V1.0.1 (For V3 call) TOOL: inputNameList = ['isSearchable','isFinal','county','inFC','outDir','outName','outSummaryDir',''''exportModel','inExportTable','inExportGeometryFC','inXREFTable','tablePIN','geomPin','xmlPIN','xrefTablePIN','xrefGeomPIN',''''outINIDir','subName','subEmail','condoModel','inCert','isNameRedact','redactPolicy','zoningGenType','zoningGenFC','zoningFarmType','zoningFarmFC','zoningShoreType','zoningShoreFC','zoningFloodType','zoningFloodFC','zoningAirType','zoningAirFC','isCOPDomainV3','copClass1','copClass2','copClass3','copClass4','copClass5','copClass5M','copClass6','copClass7','auxClassW1','auxClassW2','auxClassW3','auxClassW4','auxClassW5','auxClassW6','auxClassW7','auxClassW8','auxClassW9','auxClassX1','auxClassX2','auxClassX3','auxClassX4','PARCELID','TAXPARCELID','PARCELDATE','TAXROLLYEAR','OWNERNME1','OWNERNME2','PSTLADRESS','SITEADRESS','ADDNUMPREFIX','ADDNUM','ADDNUMSUFFIX','PREFIX','STREETNAME','STREETTYPE','SUFFIX','LANDMARKNAME','UNITTYPE','UNITID','PLACENAME','ZIPCODE','ZIP4','STATE','SCHOOLDIST','SCHOOLDISTNO','IMPROVED','CNTASSDVALUE','LNDVALUE','IMPVALUE','FORESTVALU','ESTFMKVALUE','NETPRPTA','GRSPRPTA','PROPCLASS','AUXCLASS','ASSDACRES','DEEDACRES','GISACRES','CONAME','PARCELFIPS','PARCELSRC']
# FROM V2.0.0 (For V4 call) TOOL: inputNameList = ['isSearchable','isFinal','county','inFC','outDir','outName','outSummaryDir','outINIDir','subName','subEmail','condoModel','inCert','isNameRedact','redactPolicy','zoningGenType','zoningGenFC','zoningShoreType','zoningShoreFC','zoningAirType','zoningAirFC','PLSSType','PLSSFC','RightOfWayType','RightOfWayFC','RoadStreetCenterlineType','RoadStreetCenterlineFC','HydroLineType','HydroLineFC','HydroPolyType','HydroPolyFC','AddressesType','AddressesFC','BuildingBuildingFootprintType','BuildingBuildingFootprintFC','LandUseType','LandUseFC','ParksOpenSpaceType','ParksOpenSpaceFC','TrailsType','TrailsFC','OtherRecreationType','OtherRecreationFC','certifiedBy','PLSSOtherDigitalFile']
inputNameList = ['isSearchable','isFinal','county','inFC','outDir','outName','outINIDir','subName','subEmail','condoModel','inCert','isNameRedact','redactPolicy','zoningGenType','zoningGenFC','zoningShoreType','zoningShoreFC','zoningAirType','zoningAirFC','PLSSType','PLSSFC','RightOfWayType','RightOfWayFC','RoadStreetCenterlineType','RoadStreetCenterlineFC','HydroLineType','HydroLineFC','HydroPolyType','HydroPolyFC','AddressesType','AddressesFC','BuildingBuildingFootprintType','BuildingBuildingFootprintFC','LandUseType','LandUseFC','ParksOpenSpaceType','ParksOpenSpaceFC','TrailsType','TrailsFC','OtherRecreationType','OtherRecreationFC','certifiedBy','PLSSOtherDigitalFile']
inputDict = collections.OrderedDict()
i = 0
for inputName in inputNameList:
    if inputName == 'isSearchable':
        inputDict[inputName] = 'true' # this parameter is no longer a user input because all data is searchable format
    else:
        inputDict[inputName] = arcpy.GetParameterAsText(i)
        i += 1

#Run version check
inputDict['version'] = 'V4.0.0'
try:
	arcpy.AddMessage('Checking Tool Version...')
	currVersion = urllib2.urlopen('http://www.sco.wisc.edu/parcels/tools/Validation/validation_version.txt').read()
	if inputDict['version'] == currVersion:
		arcpy.AddMessage('Tool up to date.')
	else:
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		arcpy.AddMessage("!!!!!!!!!!Error tool not up to date!!!!!!!!!!")
		arcpy.AddMessage("Please download the latest version of the tool at")
		arcpy.AddMessage("http://www.sco.wisc.edu/parcels/tools/")
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		exit()
except Exception:
	arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	arcpy.AddMessage("Check the change log at http://www.sco.wisc.edu/parcels/tools/")
	arcpy.AddMessage("to make sure the latest version of the tool is installed before submitting")

#Create summary object
summary = Summary()

base = os.path.dirname(os.path.abspath(__file__))

if inputDict['isSearchable'] == 'true':

	#Load files for current domain lists
	#streetNames = [line.strip() for line in open(os.path.join(base, '..\data\V3_StreetName_Simplified.txt'), 'r')] #street name list
	streetTypes = [line.strip() for line in open(os.path.join(base, '..\data\V5_StreetType_Simplified.txt'), 'r')] #street types domain list
	unitIdTypes = [line.strip() for line in open(os.path.join(base, '..\data\V5_UnitId_Simplified.txt'),'r')] #unitid domain list
	unitTypes = [line.strip() for line in open(os.path.join(base, '..\data\V5_UnitType_Simplified.txt'),'r')] #unit type domain list
	lsadDomains = [line.strip() for line in open(os.path.join(base, '..\data\LSAD_Simplified.txt'),'r')] #lsad domain list
	taxRollYears = [line.strip() for line in open(os.path.join(base, '..\data\V5_TaxRollYears.txt'),'r')] #taxroll years to test (past,expected,future1,future2)
	suffixDomains = [line.strip() for line in open(os.path.join(base, '..\data\V5_SuffixDomains_Simplified.txt'),'r')] #suffix domain list
	prefixDomains = [line.strip() for line in open(os.path.join(base, '..\data\V5_PrefixDomains_Simplified.txt'),'r')] #prefix domain list
	pinSkips = [line.strip() for line in open(os.path.join(base, '..\data\V5_PinSkips.txt'),'r')] #list of non-parcelid values found in field to ignore when checking for dups (and use in other functions)

	reader = csv.reader(open(os.path.join(base, '..\data\school_district_codes.csv'),'rU')) #school district code list (csv has been updated for V5/2018 school districts)
	schoolDist_nameNo_dict = {}
	schoolDist_noName_dict = {}
	for row in reader:
		k,v = row
		schoolDist_noName_dict[k] = v
		schoolDist_nameNo_dict[v] = k

	reader = csv.reader(open(os.path.join(base,'..\data\CoNameFips.csv'),'rU')) #CONAME and FIPS list
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

	#Call all pre-cursor test functions
	Error.checkCRS(totError, output_fc_temp)
	Error.checkSchema(totError, output_fc_temp, parcelSchemaReq, fieldListPass)
	Error.checkCodedDomains(totError, inputDict['inFC'])

	#Adding new fields for error reporting.  We can change names, lenght, etc...
	arcpy.AddMessage("Adding Error Fields")
	arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 1000)
	arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 1000)
	arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 1000)
	arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 1000)

	#Create update cursor then use it to iterate through records in feature class
	arcpy.AddMessage("Testing the data for various attribute error types.")
	with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:
		for row in cursor:
			#Construct the Parcel object for the row
			currParcel = Parcel(row, fieldNames)

			#Execute in-cursor error tests
			totError,currParcel = Error.checkGeometricQuality(totError,currParcel, pinSkips)

			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"addnum","address", True)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"parcelfips","general", False)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"zipcode","address", True)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"zip4","address", True)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"cntassdvalue","tax",True)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"lndvalue","tax",True)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"impvalue","tax",True)
			totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"mflvalue","tax",True)
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
			totError,currParcel = Error.checkDomainString(totError,currParcel,"placename","general",True,lsadDomains)
			totError,currParcel = Error.checkDomainString(totError,currParcel,"suffix","address",True, suffixDomains)
            #totError,currParcel = Error.badChars(totError,currParcel,fieldNames,fieldNamesBadChars,'general')
			totError,currParcel = Error.trYear(totError,currParcel,"taxrollyear","parcelid","tax",False,pinSkips,taxRollYears)
			totError,currParcel = Error.taxrollYrCheck(totError,currParcel,"taxrollyear","tax",False,pinSkips,taxRollYears)
			totError,currParcel = Error.streetNameCheck(totError,currParcel,"streetname","siteadress","address",True,stNameDict,inputDict['county'])
			totError,currParcel = Error.zipCheck(totError,currParcel,"zipcode","address",True)
			totError,currParcel = Error.zip4Check(totError,currParcel,"zip4","address",True)
			#totError,currParcel = Error.impCheck(totError,currParcel,"improved","impvalue","tax")

			totError,currParcel = Error.totCheck(totError,currParcel,"impvalue","cntassdvalue","lndvalue","tax")

			#EXAMPLE FUNCTION # totError,currParcel = Error.reallyBadChars(totError,currParcel,fieldNames,fieldNamesBadChars,'general')
			totError,currParcel = Error.checkRedundantID(totError,currParcel,'taxparcelid','parcelid',True,'general')
			totError,currParcel = Error.postalCheck(totError,currParcel,'pstladress','general',pinSkips,'taxrollyear','parcelid',badPstladdSet, taxRollYears)
			totError,currParcel = Error.auxPropCheck(totError,currParcel,'propclass','auxclass','taxrollyear','parcelid', pinSkips,'tax', copDomains, auxDomains, taxRollYears)
			#arcpy.AddMessage('On record:'+ str(currParcel.objectid))
			totError,currParcel = Error.totalAssdValueCheck(totError,currParcel,'cntassdvalue','lndvalue','impvalue','tax')
			totError,currParcel = Error.fairMarketCheck(totError,currParcel,'propclass','auxclass','estfmkvalue','tax')
			totError,currParcel = Error.mfLValueCheck(totError,currParcel,'mflvalue','auxclass','tax')
			totError,currParcel = Error.auxclassTaxrollCheck (totError,currParcel,'auxclass', 'tax')
			totError,currParcel = Error.matchContrib(totError,currParcel,"coname","parcelfips","parcelsrc",county_nameNo_dict,county_noName_dict,False,"general")
			totError,currParcel = Error.netVsGross(totError,currParcel,"netprpta","grsprpta","tax")
			totError,currParcel = Error.schoolDistCheck(totError,currParcel,"parcelid","schooldist","schooldistno",schoolDist_noName_dict,schoolDist_nameNo_dict,"tax",pinSkips,"taxrollyear")
			totError,currParcel = Error.mflLndValueCheck(totError,currParcel,"lndvalue","mflvalue","tax")
			totError,currParcel = Error.fieldCompleteness(totError,currParcel,fieldNames,fieldListPass,CompDict)
			#totError,currParcel = Error.fieldCompletenessComparison(totError,currParcel,fieldNames,fieldListPass,v3CompDict,getattr(LegacyCountyStats, (inputDict['county'].replace(" ","_").replace(".",""))+"LegacyDict"))
			totError,currParcel = Error.propClassCntCheck(totError,currParcel,"propclass","cntassdvalue","tax")
			#End of loop, finalize errors with the writeErrors function, then clear parcel
			currParcel.writeErrors(row,cursor, fieldNames)
			currParcel = None

	totError = Error.fieldCompletenessComparison(totError,fieldNames,fieldListPass,CompDict,getattr(LegacyCountyStats, (inputDict['county'].replace(" ","_").replace(".",""))+"LegacyDict"))

	if totError.geometryNotChecked == False:
		Error.ctyExtentCentCheck(totError, inputDict['inFC'], ctyCentroidDict)

	if totError.geometryNotValidated == True:
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		arcpy.AddMessage("THE GEOMETRY OF THIS FEATURE CLASS WAS NOT VALIDATED  \n")
		arcpy.AddMessage("THE FEATURE CLASS IS ABOUT " + str(totError.xyShift) + " METERS DISPLACED FROM DATA SUBMITTED LAST YEAR. \n")
		arcpy.AddMessage("THIS ISSUE IS INDICATIVE OF A RE-PROJECTION ERROR. \n ")
		arcpy.AddMessage("PLEASE MAKE NEEDED ALTERATIONS TO THE FEATURE CLASS AND RUN THE TOOL AGAIN.\n")
		arcpy.AddMessage("CHECK THE DOCUMENTATION: http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf Section 2 \n" )
		arcpy.AddMessage("CONTACT THE PARCEL TEAM AT SCO WITH QUESTIONS ABOUT THIS ISSUE.\n")
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		sys.exit()

		#Write the ini file if final
	if inputDict['isFinal'] == 'true':
		summary.explainCertComplete(inputDict['inCert'])
		summary.fieldConstraints(totError)
		summary.writeIniFile(inputDict,totError)
	if inputDict['isFinal'] == 'false':
		# Write all summary errors to file
		outSummaryJSON = os.path.join(base, '..\summary\summary.js') # full (hard coded) path to the output .json
		outSummaryPage = os.path.join(base, '..\summary\\validation.html') # full (hard coded) path to the Validation Summary Page (escape \v with a \\)
		outSummaryDir = os.path.join(base, '..\summary') # full (hard coded) path to the Validation Summary directory
		Summary.writeSummaryTxt(summary,outSummaryDir,inputDict['outName'],totError,outSummaryPage,outSummaryJSON)

		#Write feature class from memory back out to hard disk
		arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,inputDict['outDir'],inputDict['outName'])
		arcpy.AddMessage("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		arcpy.AddMessage("TEST RUN COMPLETE\n")
		arcpy.AddMessage("REVIEW THE VALIDATION SUMMARY PAGE (" + outSummaryPage.replace("\script\..","") + ") FOR A SUMMARY OF THE POTENTIAL ISSUES FOUND.\n")
		arcpy.AddMessage("REVIEW AND CORRECT IF NECESSARY, THE OUPUT PARCEL FEATURE CLASS.  RECORD-SPECIFIC ERRORS CAN BE FOUND IN THE FOUR COLUMNS ADDED TO THE END OF THE OUTPUT FEATURE CLASS.\n")
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

	arcpy.AddMessage("General Errors: " + str(totError.generalErrorCount))
	arcpy.AddMessage("Geometric Errors: " + str(totError.geometricErrorCount))
	arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
	arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))


'''#Export
else:
	totError = Error(inputDict['inExportGeometryFC'],inputDict['county'])
	summary.writeIniFile(inputDict,totError)'''
