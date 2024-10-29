import arcpy,os,re,csv,collections,urllib2
from Parcel import Parcel
from Error import Error
from Summary import Summary
from sys import exit
import LegacyCountyStats
from externalDicts import *
import os

base = os.path.dirname(os.path.abspath(__file__))
inputDict = collections.OrderedDict()

#Collect tool inputs
inputNameList = ['isFinal','county','inFC','outDir','outName','outINIDir','subName','subEmail','condoModel','inCert','isNameRedact','redactPolicy','zoningGenType','zoningGenFC','zoningShoreType','zoningShoreFC','zoningAirType','zoningAirFC','PLSSType','PLSSFC','RightOfWayType','RightOfWayFC','RoadStreetCenterlineType','RoadStreetCenterlineFC','HydroLineType','HydroLineFC','HydroPolyType','HydroPolyFC','AddressesType','AddressesFC','BuildingBuildingFootprintType','BuildingBuildingFootprintFC','LandUseType','LandUseFC','ParksOpenSpaceType','ParksOpenSpaceFC','TrailsType','TrailsFC','OtherRecreationType','OtherRecreationFC','certifiedBy','PLSSOtherDigitalFile']

i = 0
for inputName in inputNameList:
    inputDict[inputName] = arcpy.GetParameterAsText(i)
    i += 1

# Current tool version number & function that checks to ensure running most current version available
inputDict['version'] = 'V6.0.0'
Error.versionCheck(inputDict['version'])

#Creates schooldist name/number key value pair dictionaries
#(csv has been updated for V8/2021 school districts) 
reader = csv.reader(open(os.path.join(base, '..\data\school_district_codes.csv'),'rU')) 
schoolDist_nameNo_dict = {}
schoolDist_noName_dict = {}
for row in reader:
	k,v = row
	schoolDist_noName_dict[k] = v
	schoolDist_nameNo_dict[v] = k

#Creates CONAME/FIPS key value pair dictinaries
reader = csv.reader(open(os.path.join(base,'..\data\CoNameFips.csv'),'rU'))
county_nameNo_dict = {}
county_noName_dict = {}
for row in reader:
	k,v = row
	county_nameNo_dict[k] = v
	county_noName_dict[v] = k

#Create summary object
summary = Summary()

#Create error object
totError = Error(inputDict['inFC'],inputDict['county'])

#to store up to 10 parcel id to restore when checking that mflvalue <> landvalue
parcelidList_MFL = []

#lists for collecting parcelids and taxparcelids for checking for dups
uniquePinList = []
uniqueTaxparList = []

# list for collecting unique and repeated parceldates 
uniqueDates = []
sameDates = []

#Copy feature class, add new fields for error reporting
arcpy.AddMessage("Writing to Memory\n")
output_fc_temp = os.path.join("in_memory", "WORKING")
#arcpy.AddMessage(output_fc_temp)
arcpy.Delete_management("in_memory")
#dynamic_workspace = "in_memory"
arcpy.FeatureClassToFeatureClass_conversion(inputDict['inFC'],"in_memory", "WORKING")

#Call all pre-cursor test functions
#Check if the coordinate reference system is consistent with that of the parcel initiative
Error.checkCRS(totError, output_fc_temp)
#check input fc to ensure schema meets requirements.  If not, alert to missing/excess fields
Error.checkSchema(totError, output_fc_temp, parcelSchemaReq, fieldListPass)
#Ensure no coded domains exist
Error.checkCodedDomains(totError, inputDict['inFC'])

#Adding new fields for error reporting.  We can change names, lenght, etc...
arcpy.AddMessage("Adding Error Fields\n")
arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 1000)


#Create update cursor then use it to iterate through records in feature class
arcpy.AddMessage("Testing the data for various attribute error types.\n")

with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:
	for row in cursor:
		#Construct the Parcel object for the row
		currParcel = Parcel(row, fieldNames)

		#Execute in-cursor error tests
		#EXAMPLE FUNCTION # totError,currParcel = Error.reallyBadChars(totError,currParcel,fieldNames,fieldNamesBadChars,'general')
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
		totError,currParcel = Error.checkDomainString(totError,currParcel,"unittype","address",True,unitType)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"unitid","address",True,unitId)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"placename","general",True,lsadDomains)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"suffix","address",True, suffixDomains)
		totError,currParcel = Error.trYear(totError,currParcel,"taxrollyear","parcelid","tax",False,pinSkips,taxRollYears)
		totError,currParcel = Error.taxrollYrCheck(totError,currParcel,"taxrollyear","tax",False,pinSkips,taxRollYears)
		totError,currParcel = Error.streetNameCheck(totError,currParcel,"streetname","siteadress","address",True,stNameDict,inputDict['county'])
		totError,currParcel = Error.zipCheck(totError,currParcel,"zipcode","address",True)
		totError,currParcel = Error.zip4Check(totError,currParcel,"zip4","address",True)
		totError,currParcel = Error.totCheck(totError,currParcel,"impvalue","cntassdvalue","lndvalue","tax")
		totError,currParcel = Error.checkRedundantID(totError,currParcel,'taxparcelid','parcelid',True,'general')
		totError,currParcel = Error.postalCheck(totError,currParcel,'pstladress','general',pinSkips,'taxrollyear','parcelid',badPstladdSet, taxRollYears)
		totError,currParcel = Error.auxPropCheck(totError,currParcel,'propclass','auxclass','taxrollyear','parcelid', pinSkips,'tax', copDomains, auxDomains, taxRollYears)
		totError,currParcel = Error.totalAssdValueCheck(totError,currParcel,'cntassdvalue','lndvalue','impvalue','tax')
		totError,currParcel = Error.fairMarketCheck(totError,currParcel,'propclass','auxclass','estfmkvalue','tax')
		totError,currParcel = Error.mfLValueCheck(totError,currParcel,'mflvalue','auxclass','tax')
		totError,currParcel = Error.mflLndValueCheck(totError,currParcel,"parcelid",parcelidList_MFL,"lndvalue","mflvalue","tax")
		totError,currParcel = Error.auxclassFullyX4Check (totError,currParcel,'auxclass','propclass','tax')
		totError,currParcel = Error.matchContrib(totError,currParcel,"coname","parcelfips","parcelsrc",county_nameNo_dict,county_noName_dict,False,"general")
		totError,currParcel = Error.netVsGross(totError,currParcel,"netprpta","grsprpta","tax")
		totError,currParcel = Error.schoolDistCheck(totError,currParcel,"parcelid","schooldist","schooldistno",schoolDist_noName_dict,schoolDist_nameNo_dict,"tax",pinSkips,"taxrollyear")
		totError,currParcel = Error.propClassNetGrosCheck(totError,currParcel,"propclass","auxclass","netprpta","grsprpta","tax")
		totError,currParcel = Error.propClassCntCheck(totError,currParcel,"propclass","auxclass","cntassdvalue","tax")
		totError,currParcel = Error.fieldCompleteness(totError,currParcel,fieldNames,fieldListPass,CompDict)
		Error.checkBadChars (totError)

		#End of loop, finalize errors with the writeErrors function, then clear parcel
		currParcel.writeErrors(row,cursor, fieldNames)
		currParcel = None

totError = Error.fieldCompletenessComparison(totError,fieldNames,fieldListPass,CompDict,getattr(LegacyCountyStats, (inputDict['county'].replace(" ","_").replace(".",""))+"LegacyDict"))

## creates a statistics table for calculating number of repeated parceldates 
total = totError.recordTotalCount
output_stats_table_temp = os.path.join("in_memory", "WORKING_STATS")
arcpy.Statistics_analysis(output_fc_temp, output_stats_table_temp, [["parceldate", "COUNT"]], "parceldate")
uniform_date = ''
with arcpy.da.SearchCursor(output_stats_table_temp, ["parceldate", "COUNT_parceldate"]) as cursor:
	for row in cursor:
		#arcpy.AddMessage( float(row[1])/float(totError.recordTotalCount) * 100)
		if row[0] is not None and float(row[1])/float(totError.recordTotalCount) * 100 >= 97.0: #max_uniform_parceldate :
			uniform_date  = row[0]
			#totError.generalErrorCount += 1
			totError.uniqueparcelDatePercent = float(row[1])/float(totError.recordTotalCount) * 100
			
# populate the error field:TaxrollElementErrors
if totError.mflLnd > 10:  
	totError.taxErrorCount += 10
	item = ''
	with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:
		for row in cursor:
			for parcelid in parcelidList_MFL:
				if row[3] == parcelid:
					totError.flags_dict['mflvalueCheck'] += 1
					if row[48] is not None:
						item = "  | " + " MFLVALUE should not equal LNDVALUE in most cases.  Please correct this issue and refer to the submission documentation for further clarification as needed."
					else:
						item = "MFLVALUE should not equal LNDVALUE in most cases.  Please correct this issue and refer to the submission documentation for further clarification as needed."
					row[48] += item
			cursor.updateRow(row)
	del (cursor)


totError.ErrorSum =  totError.generalErrorCount + totError.geometricErrorCount + totError.addressErrorCount + totError.taxErrorCount

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

	if  totError.uniqueparcelDatePercent >= 97.0: 
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		arcpy.AddMessage( str(round ( totError.uniqueparcelDatePercent,2)) + "% OF ALL RECORDS CONTAIN THE SAME PARCELDATE VALUE OF " + uniform_date )
		arcpy.AddMessage("REVIEW SUBMISSION DOCUMENTATION AND SET TO <Null> IF NECESSARY.\n")
		arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
	arcpy.AddMessage("REVIEW THE VALIDATION SUMMARY PAGE (" + outSummaryPage.replace("\script\..","") + ") FOR A SUMMARY OF THE POTENTIAL ISSUES FOUND.\n")
	arcpy.AddMessage("REVIEW AND CORRECT IF NECESSARY, THE OUPUT PARCEL FEATURE CLASS.  RECORD-SPECIFIC ERRORS CAN BE FOUND IN THE FOUR COLUMNS ADDED TO THE END OF THE OUTPUT FEATURE CLASS.\n")
	arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

arcpy.AddMessage("General Errors: " + str(totError.generalErrorCount))
arcpy.AddMessage("Geometric Errors: " + str(totError.geometricErrorCount))
arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))
arcpy.AddMessage("-------------------")
arcpy.AddMessage("Error Sum: " + str(totError.ErrorSum) + "\n")
if totError.ErrorSum == 0:
	arcpy.AddMessage(" GREAT JOB, NO ERRORS!!!!!!! \n")

