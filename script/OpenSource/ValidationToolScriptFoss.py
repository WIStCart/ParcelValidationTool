import re, csv, collections
from Parcel import Parcel
from ErrorFoss import Error
from SummaryFoss import Summary
import sys
from sys import exit
from LegacyCountyStats import *
import LegacyCountyStats
from externalDicts import *
import os
from time import perf_counter
#import fiona; fiona.supported_drivers
#import fiona
from osgeo import gdal, ogr, osr
import pandas as pd
import geopandas as gpd

	
	
def validation_tool_run_all(inputDict):
	
	base = os.path.dirname (os.path.abspath(__file__))

	start = perf_counter()
	#inputNameList = ['isFinal','county','inFC','outDir','outName','outINIDir','subName','subEmail','condoModel','inCert','isNameReact','redactPolicy','zoningGenType','zoningGenFC','zoningShoreType','zoningShoreFC','zoningAirType','zoningAirFC','PLSSType','PLSSFC','RightOfWayType','RightOfWayFC','RoadStreetCenterlineType','RoadStreetCenterlineFC','HydroLineType','HydroLineFC','HydroPolyType','HydroPolyFC','AddressesType','AddressesFC','BuildingBuildingFootprintType','BuildingBuildingFootprintFC','LandUseType','LandUseFC','ParksOpenSpaceType','ParksOpenSpaceFC','TrailsType','TrailsFC','OtherRecreationType','OtherRecreationFC','certifiedBy','PLSSOtherDigitalFile']

	# Current tool version number & function that checks to ensure running most current version available
	inputDict['version'] = 'V7.0.1'
	Error.versionCheck(inputDict['version'])

	#Creates schooldist name/number key value pair dictionaries
	#(csv has been updated for V8/2021 school districts) 
	reader = csv.reader(open(base + '\data\school_district_codes.csv','rU')) 
	schoolDist_nameNo_dict = {}
	schoolDist_noName_dict = {}
	for row in reader:
		k,v = row
		schoolDist_noName_dict[k] = v
		schoolDist_nameNo_dict[v] = k

	#Creates CONAME/FIPS key value pair dictinaries
	reader = csv.reader(open(base + '\data\CoNameFips.csv','rU'))
	county_nameNo_dict = {}
	county_noName_dict = {}
	for row in reader:
		k,v = row
		county_nameNo_dict[k] = v
		county_noName_dict[v] = k

	## datasource and layer name
	inFC_gdb = os.path.split (inputDict['inFC'])[0]
	inFC_name = os.path.normpath(inputDict['inFC']).split(os.path.sep)[-1]

	### reading with gdal/ogr 
	datasource = ogr.GetDriverByName('FileGDB').Open(inFC_gdb, 0)
	###  get layer/feature class from the datasource i.e., geodatabase 
	inFC_layer = [ly for ly in datasource if ly.GetName() == inFC_name][0]

	#Create Summary and Error objects
	summary = Summary()
	totError = Error(inFC_layer,inputDict['county'])
	CurrCompDict = CompDict.copy()  ## start with a fresh copy of the completeness dictionary 

	#to store up to 10 parcel id to restore when checking that mflvalue <> landvalue
	parcelidList_MFL = []

	#lists for collecting parcelids and taxparcelids for checking for dups
	uniquePinList = []
	uniqueTaxparList = []
		
	# list for collecting unique and repeated parceldates 
	uniqueDates = []
	sameDates = []

	#Copy feature class, add new fields for error reporting
	#print(output_fc_temp )
	#dynamic_workspace =  "in_memory
	
	### call a driver for memory to write/copy a layer to memory
	print("    Writing to Memory\n")
	mem_driver=ogr.GetDriverByName('MEMORY')
	mem_ds=mem_driver.CreateDataSource('in_memory')
	mem_driver.Open('in_memory',1)  ## open/returns the datasource object
	output_fc_temp = mem_ds.CopyLayer( inFC_layer, 'temp', ['OVERWRITE=YES'])
	inFC_layer = None
	datasource = None

	# TODO: check out why this doesn't work
	#Check if the coordinate reference system is consistent with that of the parcel initiative
	Error.checkCRS( totError, output_fc_temp)  #c_inFC)
	#check input fc to ensure schema meets requirements.  If not, alert to missing/excess fields
	##  Error.checkSchema(totError, output_fc_temp, parcelSchemaReq, fieldListPass)
	Error.checkSchema(totError, output_fc_temp, parcelSchemaReq, fieldListPass)
	#Ensure no coded domains exist -- NOT DONE YET, CHECK IF THIS IS NECESSARY YET
	# Error.checkCodedDomains(totError, inputDict['inFC'])
	
	#Adding new fields for error reporting.  We can change names, lenght, etc...
	print ("\n    Adding error Fields\n\n")
	### creating error fields 
	field_GeneralElementErrors = ogr.FieldDefn("GeneralElementErrors", ogr.OFTString)
	field_GeneralElementErrors.SetWidth(1000)
	output_fc_temp.CreateField(field_GeneralElementErrors)
	field_AddressElementErrors = ogr.FieldDefn("AddressElementErrors", ogr.OFTString)
	field_AddressElementErrors.SetWidth(1000)
	output_fc_temp.CreateField(field_AddressElementErrors)
	field_TaxrollElementErrors = ogr.FieldDefn("TaxrollElementErrors", ogr.OFTString)
	field_TaxrollElementErrors.SetWidth(1000)
	output_fc_temp.CreateField(field_TaxrollElementErrors)
	field_GeometricElementErrors = ogr.FieldDefn("GeometricElementErrors", ogr.OFTString)
	field_GeometricElementErrors.SetWidth(1000)
	output_fc_temp.CreateField(field_GeometricElementErrors)

	print ("    Begining to test "+ inFC_name  +" Parcels data for various attribute error types \n\n") 
	print ("    The process may take a few minutes, please, don't close this window \n\n") 
	
	###############  IT WORKS TO THIS POINT EXCEPT FOR THE CRS AND GEOM
	#Create update cursor then use it to iterate through records in feature class
	
	
	for row in output_fc_temp:  #.iterrows():    # use the fieldNames list from the External Dictionary
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
		
		totError,currParcel = Error.fieldCompleteness(totError,currParcel,fieldNames,fieldListPass,CurrCompDict)
		
		Error.checkBadChars (totError)   #check for checking '<Null>', NULL, etc values
		#End of loop, finalize errors with the writeErrors function, then clear parcel
		
		currParcel.writeErrors(row, fieldNames)
		output_fc_temp.SetFeature(row)  #update feature class (datasource) with errorTypes
		#row = None

		currParcel = None

	totError = Error.fieldCompletenessComparison(totError,fieldNames,fieldListPass,CurrCompDict, getattr(LegacyCountyStats, (inputDict['county'].replace(" ","_").replace(".",""))+"LegacyDict"))
	
	## creates a statistics table for calculating number of repeated parceldates 		
	# output_stats_table_temp = os.path.join("in_memory", "WORKING_STATS")
	parcelDatelist = [row.GetField("PARCELDATE") for row in output_fc_temp ]
	pDatadf = pd.DataFrame(parcelDatelist)
	uniqueParcelDates = pDatadf.value_counts( normalize = True)   #frequency of parceldate values

	for row in uniqueParcelDates.values:
		#print( float(row[1])/float(totError.recordTotalCount) * 100)
		if row is not None and row * 100 >= 25.0: #max_uniform_parceldate :
			totError.uniqueparcelDatePercent = row * 100
	
	# populate the error field:TaxrollElementErrors for mflLnd errors
	if totError.mflLnd > 10:  
		totError.taxErrorCount += 10
		item = ''
		#	for row in cursor:
		for row in output_fc_temp:       #.iterrows():
			for parcelid in parcelidList_MFL:
				if row.GetField("PARCELID") == parcelid: # change from hard-code to column name
					totError.flags_dict['mflvalueCheck'] += 1
					if row.GetField("TaxrollElementErrors") is not None:
						item = "  | " + " MFLVALUE should not equal LNDVALUE in most cases.  Please correct this issue and refer to the submission documentation for further clarification as needed."
					else:
						item = "MFLVALUE should not equal LNDVALUE in most cases.  Please correct this issue and refer to the submission documentation for further clarification as needed."
					row.SetField("TaxrollElementErrors", item)   #row[48] += item
					output_fc_temp.SetFeature(row)

	totError.ErrorSum =  totError.generalErrorCount + totError.geometricErrorCount + totError.addressErrorCount + totError.taxErrorCount

	if totError.geometryNotChecked == False:
		Error.ctyExtentCentCheck(totError, output_fc_temp, ctyCentroidDict)

	if totError.geometryNotValidated == True:
		print("  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		print("  THE GEOMETRY OF THIS FEATURE CLASS WAS NOT VALIDATED  \n")
		print("  THE FEATURE CLASS IS ABOUT " + str(totError.xyShift) + " METERS DISPLACED FROM DATA SUBMITTED LAST YEAR. \n")
		# print("  THIS ISSUE IS INDICATIVE OF A RE-PROJECTION ERROR. \n ")
		# print("  PLEASE MAKE NEEDED ALTERATIONS TO THE FEATURE CLASS AND RUN THE TOOL AGAIN.\n")
		# print("  CHECK THE DOCUMENTATION: http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf Section 2 \n" )
		print("  CONTACT THE PARCEL TEAM AT SCO WITH QUESTIONS ABOUT THIS ISSUE.\n")
		print("  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
		#exit()
		sys.tracebacklimit = 0
		raise NameError("\n     FEATURE CLASS GEOMETRY NOT VALIDATED")
		
		#Write the ini file if final
	if inputDict['isFinal'] == 'finalModeSelected':   #  'true':
		#summary.explainCertComplete(inputDict['inCert'])
		summary.fieldConstraints(totError)
		summary.createFGDBs (inputDict, taxRollYears)
		summary.writeIniFile(inputDict,totError)


	if inputDict['isFinal'] == 'testModeSelected':    #'false'
		# Write all summary errors to file
		outSummaryJSON = base + '\summary\summary.js' # full (hard coded) path to the output .json
		outSummaryPage = base + '\summary\\validation.html' # full (hard coded) path to the Validation Summary Page (escape \v with a \\)
		outSummaryDir = base + '\summary' # full (hard coded) path to the Validation Summary directory

		summary.writeSummaryTxt(outSummaryDir,inputDict['outName'],totError,outSummaryPage,outSummaryJSON)
		
		#Write feature class from memory back out to hard disk
	
		#print ( "driver: FILEGDB")
		#print ( inputDict['outName'])
		
		out_driv = ogr.GetDriverByName('FileGDB')
		#try:
		out_ds = out_driv.Open(inputDict['outDir'], 1)
		outlayer = out_ds.CopyLayer (output_fc_temp, inputDict['outName'], 
						['OVERWRITE=YES', 'METHOD=SKIP', 'OGR_ORGANIZE_POLYGONS=SKIP'] ) 
		#delete layers and datasources
		
		output_fc_temp = None
		mem_ds = None
		outlayer = None
		out_ds = None
		#except:
		#	print ( " driver failed")
		
		print("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		print("  TEST RUN COMPLETE\n")

		if  totError.uniqueparcelDatePercent >= 25.0: 
			# print("  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			print("    " + str(round ( totError.uniqueparcelDatePercent,2)) + "% OF ALL RECORDS CONTAIN THE SAME PARCELDATE VALUE " )
				#OF " + uniform_date )
			print("    REVIEW SUBMISSION DOCUMENTATION AND SET TO <Null> IF NECESSARY.\n")
			# print("  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			pass
		# print("  REVIEW THE VALIDATION SUMMARY PAGE (" + outSummaryPage.replace("\script\..","") + ") FOR A SUMMARY OF THE POTENTIAL ISSUES FOUND.\n")
		# print("  REVIEW AND CORRECT IF NECESSARY, THE OUPUT PARCEL FEATURE CLASS.  RECORD-SPECIFIC ERRORS CAN BE FOUND IN THE FOUR COLUMNS ADDED TO THE END OF THE OUTPUT FEATURE CLASS:\n")
		# print("	" + inputDict['outDir'] + "\\" + inputDict['outName']  + "\n")
		# print("  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
	print("  General Errors:   " + str(totError.generalErrorCount))
	print("  Geometric Errors: " + str(totError.geometricErrorCount))
	print("  Address Errors:   " + str(totError.addressErrorCount))
	print("  Tax Errors:       " + str(totError.taxErrorCount))
	print("  -------------------")
	print("  Error Sum:        " + str(totError.ErrorSum) + "\n")
	if totError.ErrorSum == 0:
		# print("   GREAT JOB, NO ERRORS!!!!!!! \n")
		pass
	
	print ("	DONE!!!\n")
	end  = perf_counter()
	print (f'    Elapse time: { end - start: .2f} seconds')
	