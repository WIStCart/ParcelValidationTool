import collections
from Parcel import Parcel
from LegacyCountyStats import *
import json
import webbrowser
#from .ConfigParser import ConfigParser
import configparser
import os
import sys
import osgeo
from osgeo import ogr

class Summary:

	def __init__(self):
		pass #placeholder

		'''
		print (outSummaryDir)
		print (outSummaryPage)
		print (outSummaryJSON)
		'''

	def writeSummaryTxt(self,outDirTxt,outName,totError,outPage,outJSON):
		try:
			Validation_JSON = {
				'County_Info':{
					'CO_NAME': totError.coName,
					'Total_Records': totError.recordTotalCount,
					'Legacy': eval((totError.coName).replace(" ","_") + "LegacyDict")
				},
				'inLineErrors':{
					'General_Errors': str(totError.generalErrorCount),
					'Geometric_Errors': str(totError.geometricErrorCount),
					'Address_Errors': str(totError.addressErrorCount),
					'Tax_Errors': str(totError.taxErrorCount),
					'Error_Sum': str(totError.ErrorSum)
				},
				'broadLevelErrors':{
					'Geometric_Misplacement_Flag':[],
					'Geometric_File_Error':[],
					'Coded_Domain_Fields': ', '.join(totError.codedDomainfields)
				},
				'Tax_Roll_Years_Pcnt':{
					'Previous_Taxroll_Year':  str(round((float(totError.trYearPast / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)),
					'Expected_Taxroll_Year':  str(round((float(totError.trYearExpected / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)),
					'Future_Taxroll_Years':  str(round((float(totError.trYearFuture / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)),
					'Other_Taxroll_Years':  str(round((float(totError.trYearOther / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2))
				},
				'Records_Missing':{
					'Missing_CONAME': str(totError.coNameMiss),
					'Missing_PARCELFIPS': str(totError.fipsMiss),
					'Missing_PARCELSRC': str(totError.srcMiss)
				},
				'Unique_ParcelDate':{
					'Pcnt_Unique_Parceldate': str(round (totError.uniqueparcelDatePercent,2))
				},
				'Fields_Diffs':{
					'PARCELID':  str(totError.comparisonDict["PARCELID"]),
					'TAXPARCELID':  str(totError.comparisonDict["TAXPARCELID"]),
					'PARCELDATE':  str(totError.comparisonDict["PARCELDATE"]),
					'TAXROLLYEAR':  str(totError.comparisonDict["TAXROLLYEAR"]),
					'OWNERNME1':  str(totError.comparisonDict["OWNERNME1"]),
					'OWNERNME2':  str(totError.comparisonDict["OWNERNME2"]),
					'PSTLADRESS':  str(totError.comparisonDict["PSTLADRESS"]),
					'SITEADRESS':  str(totError.comparisonDict["SITEADRESS"]),
					'ADDNUMPREFIX':  str(totError.comparisonDict["ADDNUMPREFIX"]),
					'ADDNUM':  str(totError.comparisonDict["ADDNUM"]),
					'ADDNUMSUFFIX':  str(totError.comparisonDict["ADDNUMSUFFIX"]),
					'PREFIX':  str(totError.comparisonDict["PREFIX"]),
					'STREETNAME':  str(totError.comparisonDict["STREETNAME"]),
					'STREETTYPE':  str(totError.comparisonDict["STREETTYPE"]),
					'SUFFIX':  str(totError.comparisonDict["SUFFIX"]),
					'LANDMARKNAME':  str(totError.comparisonDict["LANDMARKNAME"]),
					'UNITTYPE':  str(totError.comparisonDict["UNITTYPE"]),
					'UNITID':  str(totError.comparisonDict["UNITID"]),
					'PLACENAME':  str(totError.comparisonDict["PLACENAME"]),
					'ZIPCODE':  str(totError.comparisonDict["ZIPCODE"]),
					'ZIP4':  str(totError.comparisonDict["ZIP4"]),
					'SCHOOLDIST':  str(totError.comparisonDict["SCHOOLDIST"]),
					'SCHOOLDISTNO':  str(totError.comparisonDict["SCHOOLDISTNO"]),
					'CNTASSDVALUE':  str(totError.comparisonDict["CNTASSDVALUE"]),
					'LNDVALUE':  str(totError.comparisonDict["LNDVALUE"]),
					'IMPVALUE':  str(totError.comparisonDict["IMPVALUE"]),
					'MFLVALUE':  str(totError.comparisonDict["MFLVALUE"]),
					'ESTFMKVALUE':  str(totError.comparisonDict["ESTFMKVALUE"]),
					'NETPRPTA':  str(totError.comparisonDict["NETPRPTA"]),
					'GRSPRPTA':  str(totError.comparisonDict["GRSPRPTA"]),
					'PROPCLASS':  str(totError.comparisonDict["PROPCLASS"]),
					'AUXCLASS':  str(totError.comparisonDict["AUXCLASS"]),
					'ASSDACRES':  str(totError.comparisonDict["ASSDACRES"]),
					'DEEDACRES':  str(totError.comparisonDict["DEEDACRES"]),
					'GISACRES':  str(totError.comparisonDict["GISACRES"]),
					'CONAME':  str(totError.comparisonDict["CONAME"]),
					'PARCELFIPS':  str(totError.comparisonDict["PARCELFIPS"]),
					'PARCELSRC':  str(totError.comparisonDict["PARCELSRC"])
					}
			}
			self.errorSummaryFile = open(outDirTxt + "/" + outName + "_ValidationSummary.txt","w")
			("Creating Validation Summary here: " + outDirTxt + "/" + outName + "_ValidationSummary.txt")
			self.errorSummaryFile.write(outDirTxt + "\\" + outName + "_ValidationSummary.txt" + "\n")
			self.errorSummaryFile.write("Validation Summary Table: " + "\n")
			self.errorSummaryFile.write("This validation summary table contains an overview of any errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary." + "\n\n")
			self.errorSummaryFile.write("************************************************************************\n")
			self.errorSummaryFile.write("* In-line errors\n")
			self.errorSummaryFile.write("************************************************************************\n")
			self.errorSummaryFile.write("The following lines summarized the element-specific errors that were found while validating your parcel dataset.  The stats below are meant as a means of reviewing the output.  Please see the GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields to address these errors individually.\n")
			self.errorSummaryFile.write("	General Errors: " + str(totError.generalErrorCount) + "\n")
			self.errorSummaryFile.write("	Geometric Errors: " + str(totError.geometricErrorCount) + "\n")
			self.errorSummaryFile.write("	Address Errors: " + str(totError.addressErrorCount) + "\n")
			self.errorSummaryFile.write("	Tax Errors: " + str(totError.taxErrorCount) + "\n")
			self.errorSummaryFile.write("	------------------\n")
			self.errorSummaryFile.write("	ERROR SUM: " + str(totError.ErrorSum ) + "\n")
			if totError.ErrorSum == 0:
				self.errorSummaryFile.write("\n	GREAT JOB, NO ERRORS!!!!!! \n")
			self.errorSummaryFile.write("\n\n")
			self.errorSummaryFile.write("************************************************************************\n")
			self.errorSummaryFile.write("* Uniform ParcelDate:\n")
			self.errorSummaryFile.write("************************************************************************\n")
			if totError.uniqueparcelDatePercent >= 51.0:
				self.errorSummaryFile.write( str(round (totError.uniqueparcelDatePercent,2)) + "% of all records contain the same PARCELDATE value\n")
				self.errorSummaryFile.write("Review submission documentation and set <Null> if necessary.\n\n")
			self.errorSummaryFile.write("************************************************************************\n")
			self.errorSummaryFile.write("* Broad-level errors:\n")
			self.errorSummaryFile.write("************************************************************************\n")
			self.errorSummaryFile.write("The following lines explain any broad geometric errors that were found while validating your parcel dataset."+ "\n")
			if len(totError.geometricPlacementErrors) != 0:
				for geometricErrorMessage in totError.geometricPlacementErrors:
					self.errorSummaryFile.write("	Geometric Misplacement Flag: " + str(geometricErrorMessage) + "\n")
					Validation_JSON["broadLevelErrors"]['Geometric_Misplacement_Flag'].append(str(geometricErrorMessage))
			if len(totError.geometricFileErrors) != 0:
				for geometricErrorMessage in totError.geometricFileErrors:
					self.errorSummaryFile.write("	Geometric File Error: " + str(geometricErrorMessage) + "\n")
					Validation_JSON["broadLevelErrors"]['Geometric_File_Error'].append(str(geometricErrorMessage))
			if (len(totError.geometricFileErrors) == 0) and (len(totError.geometricPlacementErrors) == 0):
				self.errorSummaryFile.write("	*No broad-level geometric errors found!" + "\n")
				Validation_JSON["broadLevelErrors"]['Geometric_File_Error'].append("None")
				Validation_JSON["broadLevelErrors"]['Geometric_Misplacement_Flag'].append("None")
			self.errorSummaryFile.write("\n\n")
			self.errorSummaryFile.write("Percentage of records with various Taxroll Years" + "\n")
			self.errorSummaryFile.write("	Previous Taxroll Year: " + str(round((float(totError.trYearPast / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			self.errorSummaryFile.write("	Expected Taxroll Year: " + str(round((float(totError.trYearExpected / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			self.errorSummaryFile.write("	Future Taxroll Years: " + str(round((float(totError.trYearFuture / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			self.errorSummaryFile.write("	Other Taxroll Years: " + str(round((float(totError.trYearOther / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			self.errorSummaryFile.write("\n\n")
			self.errorSummaryFile.write("Records missing CONAME, PARCELFIPS, or PARCELSOURCE" + "\n")
			self.errorSummaryFile.write("	Missing CONAME: " + str(totError.coNameMiss) + "\n")
			self.errorSummaryFile.write("	Missing PARCELFIPS: " + str(totError.fipsMiss) + "\n")
			self.errorSummaryFile.write("	Missing PARCELSRC: " + str(totError.srcMiss) + "\n\n")
			self.errorSummaryFile.write("If any of the above values are greater than 0, please add missing values.  These 3 fields should be populated for all records submitted.\n\n\n")
			self.errorSummaryFile.write("BELOW IS A COMPARISON OF COMPLETENESS VALUES FROM YOUR PREVIOUS PARCEL SUBMISSION AND THIS CURRENT SUBMISSION.\n")
			self.errorSummaryFile.write("-->If the value shown is a seemingly large negative number, please verify that all data was joined correctly and no data was lost during processing.\n")
			self.errorSummaryFile.write("-->Note: This does not necessarily mean your data is incorrect, we just want to highlight large discrepancies that could indicate missing or incorrect data.\n\n")
			self.errorSummaryFile.write("          FIELD     DIFFERENCE\n")
			self.errorSummaryFile.write("         ------     ----------\n")
			self.errorSummaryFile.write("       PARCELID:  " + str(totError.comparisonDict["PARCELID"]) + '\n')
			self.errorSummaryFile.write("    TAXPARCELID:  " + str(totError.comparisonDict["TAXPARCELID"]) + '\n')
			self.errorSummaryFile.write("     PARCELDATE:  " + str(totError.comparisonDict["PARCELDATE"]) + '\n')
			self.errorSummaryFile.write("    TAXROLLYEAR:  " + str(totError.comparisonDict["TAXROLLYEAR"]) + '\n')
			self.errorSummaryFile.write("      OWNERNME1:  " + str(totError.comparisonDict["OWNERNME1"]) + '\n')
			self.errorSummaryFile.write("      OWNERNME2:  " + str(totError.comparisonDict["OWNERNME2"]) + '\n')
			self.errorSummaryFile.write("     PSTLADRESS:  " + str(totError.comparisonDict["PSTLADRESS"]) + '\n')
			self.errorSummaryFile.write("     SITEADRESS:  " + str(totError.comparisonDict["SITEADRESS"]) + '\n')
			self.errorSummaryFile.write("   ADDNUMPREFIX:  " + str(totError.comparisonDict["ADDNUMPREFIX"]) + '\n')
			self.errorSummaryFile.write("         ADDNUM:  " + str(totError.comparisonDict["ADDNUM"]) + '\n')
			self.errorSummaryFile.write("   ADDNUMSUFFIX:  " + str(totError.comparisonDict["ADDNUMSUFFIX"]) + '\n')
			self.errorSummaryFile.write("         PREFIX:  " + str(totError.comparisonDict["PREFIX"]) + '\n')
			self.errorSummaryFile.write("     STREETNAME:  " + str(totError.comparisonDict["STREETNAME"]) + '\n')
			self.errorSummaryFile.write("     STREETTYPE:  " + str(totError.comparisonDict["STREETTYPE"]) + '\n')
			self.errorSummaryFile.write("         SUFFIX:  " + str(totError.comparisonDict["SUFFIX"]) + '\n')
			self.errorSummaryFile.write("   LANDMARKNAME:  " + str(totError.comparisonDict["LANDMARKNAME"]) + '\n')
			self.errorSummaryFile.write("       UNITTYPE:  " + str(totError.comparisonDict["UNITTYPE"]) + '\n')
			self.errorSummaryFile.write("         UNITID:  " + str(totError.comparisonDict["UNITID"]) + '\n')
			self.errorSummaryFile.write("      PLACENAME:  " + str(totError.comparisonDict["PLACENAME"]) + '\n')
			self.errorSummaryFile.write("        ZIPCODE:  " + str(totError.comparisonDict["ZIPCODE"]) + '\n')
			self.errorSummaryFile.write("           ZIP4:  " + str(totError.comparisonDict["ZIP4"]) + '\n')
			self.errorSummaryFile.write("     SCHOOLDIST:  " + str(totError.comparisonDict["SCHOOLDIST"]) + '\n')
			self.errorSummaryFile.write("   SCHOOLDISTNO:  " + str(totError.comparisonDict["SCHOOLDISTNO"]) + '\n')
			self.errorSummaryFile.write("   CNTASSDVALUE:  " + str(totError.comparisonDict["CNTASSDVALUE"]) + '\n')
			self.errorSummaryFile.write("       LNDVALUE:  " + str(totError.comparisonDict["LNDVALUE"]) + '\n')
			self.errorSummaryFile.write("       IMPVALUE:  " + str(totError.comparisonDict["IMPVALUE"]) + '\n')
			self.errorSummaryFile.write("       MFLVALUE:  " + str(totError.comparisonDict["MFLVALUE"]) + '\n')
			self.errorSummaryFile.write("    ESTFMKVALUE:  " + str(totError.comparisonDict["ESTFMKVALUE"]) + '\n')
			self.errorSummaryFile.write("       NETPRPTA:  " + str(totError.comparisonDict["NETPRPTA"]) + '\n')
			self.errorSummaryFile.write("       GRSPRPTA:  " + str(totError.comparisonDict["GRSPRPTA"]) + '\n')
			self.errorSummaryFile.write("      PROPCLASS:  " + str(totError.comparisonDict["PROPCLASS"]) + '\n')
			self.errorSummaryFile.write("       AUXCLASS:  " + str(totError.comparisonDict["AUXCLASS"]) + '\n')
			self.errorSummaryFile.write("      ASSDACRES:  " + str(totError.comparisonDict["ASSDACRES"]) + '\n')
			self.errorSummaryFile.write("      DEEDACRES:  " + str(totError.comparisonDict["DEEDACRES"]) + '\n')
			self.errorSummaryFile.write("       GISACRES:  " + str(totError.comparisonDict["GISACRES"]) + '\n')
			self.errorSummaryFile.write("         CONAME:  " + str(totError.comparisonDict["CONAME"]) + '\n')
			self.errorSummaryFile.write("     PARCELFIPS:  " + str(totError.comparisonDict["PARCELFIPS"]) + '\n')
			self.errorSummaryFile.write("      PARCELSRC:  " + str(totError.comparisonDict["PARCELSRC"]) + '\n')
			self.errorSummaryFile.write("\n\n\n* Within: " + outDirTxt + "\\" + outName  + "\n")
			self.errorSummaryFile.write("************************************************************************\n")
			self.errorSummaryFile.close()
			# outJSON - # full (hard coded) path to the output .json file summary.js
			with open(outJSON, 'w') as outfile:
				outfile.write("var testValues = ")
				json.dump(Validation_JSON, outfile)
		except Exception as e:
			# print("  !!!!!!!!!!Error writing summary file!!!!!!!!!!")
			# print(str(e))
			pass
		webbrowser.open(outPage, new=2)

	def writeIniFile(self,inputDict,totError):
		# print("\n")
		# print("  Creating .ini file")
		config = configparser.ConfigParser() 
		config = configparser.ConfigParser(allow_no_value=True)
		config.add_section('PARAMETERS')
		for key in inputDict.keys():
			if key != 'inCert':
				config.set('PARAMETERS',key,inputDict[key])

		if inputDict['isSearchable'] == 'true':
			config.add_section('ERROR COUNTS')
			config.set('ERROR COUNTS','General', str(totError.generalErrorCount))
			config.set('ERROR COUNTS','Geometric',str(totError.geometricErrorCount))
			config.set('ERROR COUNTS','Address', str(totError.addressErrorCount))
			config.set('ERROR COUNTS','Tax', str(totError.taxErrorCount))
			config.set('ERROR COUNTS','-------------------')
			config.set('ERROR COUNTS','Error Sum', str(totError.ErrorSum))
			if totError.ErrorSum == 0:
				config.set('ERROR COUNTS','    GREAT JOB, NO ERRORS!!!!!!!')
			config.add_section('PARCELDATE FLAG')
			if totError.uniqueparcelDatePercent >= 25.0:
				config.set('PARCELDATE FLAG', 'Uniform ParcelDate', str(round (totError.uniqueparcelDatePercent,2)) )
			if totError.uniqueparcelDatePercent < 25.0:
				config.set('PARCELDATE FLAG','  GREAT JOB, NO UNIFORM PARCELDATE!' )			
			config.add_section('PERCENT TAXROLL YEAR')
			config.set('PERCENT TAXROLL YEAR','Previous',str(round((float(totError.trYearPast / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)))
			config.set('PERCENT TAXROLL YEAR','Expected',str(round((float(totError.trYearExpected / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)))
			config.set('PERCENT TAXROLL YEAR','Future', str(round((float(totError.trYearFuture / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)))
			config.set('PERCENT TAXROLL YEAR','Other', str(round((float(totError.trYearOther / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)))
			config.add_section('MISSING RECORDS')
			config.set('MISSING RECORDS','CONAME',totError.coNameMiss)
			config.set('MISSING RECORDS','PARCELFIPS',totError.fipsMiss)
			config.set('MISSING RECORDS','PARCELSOURCE',totError.srcMiss)

			config.add_section('COMPARISON COMPLETENESS')
			for field in totError.comparisonDict.keys():
				if field != 'state' or field != 'loaddate':
					config.set('COMPARISON COMPLETENESS',field,  str(totError.comparisonDict[field]))

			config.add_section('EXPLAIN CERTIFY')
			explain_certify = inputDict['inCert']
			config.set('EXPLAIN CERTIFY','Explained Error Number', '\n' + explain_certify['explainedErrorsNumber'])
			streetName =  explain_certify['noticeOfNewStreetName'].replace("%", "percentage")
			config.set('EXPLAIN CERTIFY','Notice Of New StreetName', '\n' + streetName )        #explain_certify['noticeOfNewStreetName'])
			newNonParcels = explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'].replace("%", "percentage")
			config.set('EXPLAIN CERTIFY','Notice Of New NonParcels IDs', '\n' + newNonParcels ) #explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'])
			omissions = explain_certify['noticeOfMissingDataOmissions'].replace("%", "percentage")
			config.set('EXPLAIN CERTIFY','Notice Of Missing Data Omissions', '\n' + omissions ) # explain_certify['noticeOfMissingDataOmissions'])
			unsolvable = explain_certify['noticeErrorsSumsUnresolvable'].replace("%", "percentage")
			config.set('EXPLAIN CERTIFY','Notice Of Error Sum Unsolvable', '\n' + unsolvable )  #explain_certify['noticeErrorsSumsUnresolvable'])
			other =  explain_certify['noticeOther'].replace("%", "percentage")
			config.set('EXPLAIN CERTIFY','Other', '\n' + other)  #explain_certify['noticeOther'])
		
		county_name = inputDict['county'].replace(' ', '_')
		outPath =  inputDict['outINIDir'] + '/'+ county_name + '_Final_Submission'
	
		try:
			#Write out .ini file
			with open( outPath +'/'+ county_name +'.ini','w') as configFile:
				config.write(configFile)
				#with open(inputDict['inCert'],'r') as certFile:
				#	for line in certFile:
						#configFile.write(line)
			print("    Writing .ini file to " + outPath)
			print("\n")
			print("    ------>  .ini FILE CREATION COMPLETE!  GREAT WORK!!   <------\n\n")
		except Exception as e:
			print("    !!!!!!!!!!Error writing .ini file!!!!!!!!!!")
			print(str(e))
			pass

	def explainCertComplete(self,explain_certify):
		#print(explain_certify)
		if (explain_certify['noticeOfNewStreetName'] == '' or explain_certify['noticeOfNewStreetName'] == "Enter new Street Names here, or None if no Values exist") \
			    and (explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'] == ''  or explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'] ==  "Enter new Non-Parcel Feature Parcel IDs, or None if no Values exist") \
				and (explain_certify['noticeOfMissingDataOmissions'] == '' or explain_certify['noticeOfMissingDataOmissions'] == "Enter omission information here, or None if no omissions exist") \
				and (explain_certify['noticeErrorsSumsUnresolvable'] == '' or explain_certify['noticeErrorsSumsUnresolvable'] == "Enter number of Unresolvable errors, or None if no Values exist"):

			# print("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			# print("     IMMEDIATE ISSUE REQUIRING ATTENTION")
			# print("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			# print("  IT DOESN'T APPEAR THAT YOU FULLY FILLED OUT THE EXPLAIN-CERTIFY INFORMATION REQUIRED FOR SUBMISSION.\n\n")
			# print("  PLEASE FILL OUT THIS INFORMATION IN IT'S ENTIRETY AND RE-RUN THE TOOL IN FINAL MODE.")
			# print("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			# print("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			sys.tracebacklimit = 0
			raise NameError("\n     EXPLAIN-CERTIFY FORM INCOMPLETE")
		else:
			pass 	
		
	def fieldConstraints(self,totError):
		if totError.coNameMiss > 0 or totError.fipsMiss > 0 or totError.srcMiss > 0:
			print("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			print("    IMMEDIATE ISSUE REQUIRING ATTENTION")
			print("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			print("    ONE OF THE FOLLOWING FIELDS: CONAME, PARCELSRC or PARCELFIPS ARE NOT FULLY POPULATED.\n\n")
			print("    THESE FIELDS SHOULD BE POPULATED FOR EVERY RECORD IN THE SUMBITTED PARCEL FEATURE CLASS.\n\n")
			print("    PLEASE ENSURE THESE FIELDS ARE POPULATED FOR ALL RECORDS AND RE-RUN THE TOOL IN FINAL MODE.")
			print("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			sys.tracebacklimit = 0
			raise NameError("\n     CONAME, PARCELSRC or PARCELFIPS NOT FULLY POPULATED")
			#exit()
			
	
	def createFGDBs (self, inputDict, taxRollYears):
		import shutil			
		import os.path

		other_fc_list = ['zoningGenFC', 'zoningShoreFC','zoningAirFC', 'PLSSFC','RightOfWayFC','RoadStreetCenterlineFC','HydroLineFC','HydroPolyFC','AddressesFC','BuildingBuildingFootprintFC','LandUseFC','ParksOpenSpaceFC','TrailsFC','OtherRecreationFC']
		year = taxRollYears[2]
		inFC = inputDict['inFC']
		county_name = inputDict['county'].replace(' ', '_')
		#print (county_name)
		county_outPath = inputDict['outINIDir']  #folder for .ini, fgdbs and other plss files
		outPath =  inputDict['outINIDir']  + '/'+ county_name + '_Final_Submission'
		
		parcel_gdb = county_name + '_PARCELS.gdb'   #eg., VERNON_PARCELS.gdb
		other_gdb =  county_name + '_OTHER.gdb'		#eg., VERNON_OTHER.gdb	
		redactPolicy = inputDict['redactPolicy']
		plssOtherDigitalFile = inputDict['PLSSOtherDigitalFile']

		try:
			os.makedirs(outPath, exist_ok = True)
			#print("\n    Output Directory '%s' created successfully" %outPath)
		except OSError as error:
			print("\n    Directory can not be created")

		#also need to check if the plss files is in other format 
		if os.path.exists(outPath):
    	
			print("\n    Creating PARCEL and OTHER geodatabases\n")
			otherGDBPath  = os.path.join(outPath, other_gdb)
			parcelGDBPath = os.path.join(outPath, parcel_gdb)
			
			# creating PARCELS AND OTHER geodatabases
			# ### create Parcels gdb	
			if inputDict['inFC'] != '':			
				
				inFC_gdb = os.path.split (inputDict['inFC'])[0]
				inFC_name = os.path.normpath(inputDict['inFC']).split(os.path.sep)[-1]
				### open input datasource again 
				datasource = ogr.GetDriverByName('OpenFileGDB').Open(inFC_gdb, 0)
				###  get layer/feature class from the datasource i.e., geodatabase 
				inFC_layer = [ly for ly in datasource if ly.GetName() == inFC_name][0]
				### new geodatabase 
				fgdb_drv = ogr.GetDriverByName("OpenFileGDB")	
				if os.path.exists(parcelGDBPath):
					print( "deleting parcel gdb:  \n\n")
					fgdb_drv.DeleteDataSource(parcelGDBPath)
				pds = fgdb_drv.CreateDataSource( parcelGDBPath)
				pds.CopyLayer (inFC_layer, 'PARCELS', ['OVERWRITE=YES', 'METHOD=SKIP', 'OGR_ORGANIZE_POLYGONS=SKIP']) 
				pds = None 
				inFC_layer = None
				datasource = None
				
			def writePlssFile (outPath, plssOtherDigitalFile, ods, year):
				""" If plss file is in different format"""

				def copyFields (inLayer, outLayer):
					"""Copy inLayer Fields to the output Layer"""
					inLayerDefn = inLayer.GetLayerDefn()
					for i in range(inLayerDefn.GetFieldCount()):
					    outLayer.CreateField(inLayerDefn.GetFieldDefn(i))

				def copyAtributes (inFeature, outFeature):
					"""Copy attributes from inFeature to outFeature with same fields"""
					for i in range(inFeature.GetFieldCount()):
						fieldName = inFeature.GetFieldDefnRef(i).GetName()
						outFeature.SetField(fieldName, inFeature.GetField(fieldName))

				plss_file = plssOtherDigitalFile.split('/')
				plss_file_name = plss_file[len(plss_file)-1]
				destination = outPath + '/' + county_name + '_' + year + '_' + plss_file_name 
				extension = plss_file_name.split('.')[-1]

				if extension != 'shp':	#copy a plss file like text, or excel, csv 
					if not os.path.isfile(destination):
						shutil.copy(plssOtherDigitalFile, destination)
						print("\n\n    Wrote PLSS file to "+ destination)
						print("\n\n    ------>  PLSS FILE COPIED SUCCESSFULLY!  <------\n")
						# print("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
					else:
						pass     #print("\n\n  PLSS file already existed.\n")
				else:   
					# double check that the shapefile exists
					if os.path.exists(plssOtherDigitalFile):
						
						if (plssOtherDigitalFile.lower().endswith('.shp')):
							plss_gdb_path = outPath + '/' + other_gdb
							plss_fc_name = county_name + '_PLSS_' + year
														
							shp_drv  =  ogr.GetDriverByName("ESRI Shapefile")  
							# open users plss shape file datasource
							ds = shp_drv.Open(plssOtherDigitalFile, 1)
							#ds = ogr.Open(plssOtherDigitalFile, update=True)
							plss_lyr = ds.GetLayer()

							### we need to create a new layer with same crs and point geom in the othergdb to copy the shapefile
							crs = plss_lyr.GetSpatialRef()
							outLayer = ods.CreateLayer(plss_fc_name, crs, geom_type=ogr.wkbPoint)
							### then it can be copied into the datasource of the othergdb
							## First, copy field definitions	
							copyFields (plss_lyr, outLayer)

							# Now, populate the new layer. 
							# Get the output layer Feature Definition
							outLayerDefn = outLayer.GetLayerDefn()
							### for each point, copy the atributes i.e, field values
							for inFeature in plss_lyr:
								# Create output features
								outFeature = ogr.Feature(outLayerDefn)
								# Copy the field values from input Layer to output Layer
								copyAtributes (inFeature, outFeature)
								## copy geometry -- point geometry
								outFeature.SetGeometry(inFeature.GetGeometryRef().Clone()) 
								inFeature = None
								# Add new feature to output Layer
								outLayer.CreateFeature(outFeature)
								outFeature = None
								
							print("\n\n    Wrote PLSS file to "+ plss_gdb_path +"/"+ plss_fc_name)
							print("\n    ------>  PLSS FILE COPIED SUCCESSFULLY!  <------\n")
							plss_lyr = None
							ds = None
			# end of writePlssFile function

			#Create Other gdb		
			# append inFeatures-list other features provided in the GUI
			inFeatures = []
			coName = county_name
			for fc in other_fc_list:  
				if inputDict[fc] != '' :
					#matching  fc with it name:
					if fc == 'zoningGenFC':
						fc_name = coName + '_GENERAL_' + year
					elif fc ==  'zoningShoreFC':
						fc_name = coName + '_SHORELAND_' + year
					elif fc == 'zoningAirFC':
						fc_name = coName + '_AIRPORT_' + year
					elif fc == 'PLSSFC':
						fc_name = coName + '_PLSS_' + year
					elif fc == 'RightOfWayFC':
						fc_name = coName + '_ROW_' + year
					elif fc ==  'RoadStreetCenterlineFC':
						fc_name = coName + '_ROADS_' + year
					elif fc ==  'HydroLineFC':
						fc_name = coName + '_HYDRO_' + year + '_LINE'
					elif fc == 'HydroPolyFC':
						fc_name = coName + '_HYDRO_' + year + '_POLY'
					elif fc == 'AddressesFC': 
						fc_name = coName + '_ADDRESSES_' + year
					elif fc == 'BuildingBuildingFootprintFC':
						fc_name = coName + '_BUILDINGS_' + year
					elif fc == 'LandUseFC':
						fc_name = coName + '_LANDUSE_' + year
					elif fc == 'ParksOpenSpaceFC':
						fc_name = coName + '_PARKS_' + year 
					elif fc == 'TrailsFC':
						fc_name = coName +  '_TRAILS_' + year
					elif fc == 'OtherRecreationFC':
						fc_name = coName + '_RECREATION_' + year	
					inFeatures.append( [inputDict[fc],  fc_name])  # list with Feat classes with their new neme 

			ofgdb_drv = ogr.GetDriverByName("FileGDB")			
			## creates gdb for the other layers (ods)
			if os.path.exists(otherGDBPath):
				print( "    deleting other gdb:  \n\n")
				ofgdb_drv.DeleteDataSource(otherGDBPath)				
			ods = ofgdb_drv.CreateDataSource( otherGDBPath)
		
			if inFeatures != []:
				#ofgdb_drv.Open( otherGDBPath, 1)  #not sure if this is needed
				for oLFC in inFeatures: 
					# driver for the user features 
					of_drv = ogr.GetDriverByName("FileGDB")  
					# open other fgdb -- we cannot assume that all the fc are store in the same gdb, so I have to open the/a gdb for each fc
					## read other layer from input 
					o_gdb  = os.path.split (oLFC[0])[0]
					oFC_name = os.path.normpath(oLFC[0]).split(os.path.sep)[-1]
					of_ds = of_drv.Open( o_gdb , 0)
					of_lyr = [ly for ly in of_ds if ly.GetName() == oFC_name][0]

					layerDefinition = of_lyr.GetLayerDefn()
					# inLayerIDColname = of_lyr.GetFIDColumn() ## returns name of objectid/fid
					###  check that the fields are not duplicated ids
					###  if they are remove the "ID" characters from the fieldname
					
					### Check for 3D Multi Polygon 3D Measured Point
					#geomtype = ogr.GeometryTypeToName(of_lyr.GetLayerDefn().GetGeomType())					 
					#if geomtype in ('3D Measured Point'):
						## need to encode this data

					### Check for duplicated objectID 
					for i in range(layerDefinition.GetFieldCount()):
						fieldDefn = layerDefinition.GetFieldDefn(i)
						fieldName = fieldDefn.GetName()
						if fieldName.upper() in ('OBJECTID', 'ID', 'OBJECTID_1') :
							new_name = fieldName.replace( 'ID', '_NUM_')
							fieldDefn.SetName (new_name) 

					## copy the layer into the datasource - the "FileGDB" api can encode ZM point_type
					print ("  ALMOST THERE ") 
					print (ogr.GeometryTypeToName(of_lyr.GetLayerDefn().GetGeomType()))
					ods.CopyLayer (of_lyr, oLFC[1], ['OVERWRITE=YES', 'METHOD=SKIP','OGR_ORGANIZE_POLYGONS=SKIP']) 
					of_lyr = None
					of_ds = None

				#for oLFC in inFeatures:
				#
			if (inputDict['PLSSType'] != '' and inputDict['PLSSType'] == 'Maintained by county as other digital format'):
				#need to check for shapefile or other formats
				writePlssFile ( outPath, plssOtherDigitalFile, ods, year)
			
			ods = None
			print("    ------>  GEODATABASES CREATION COMPLETE!   <------\n\n")
			print("    SUBMISSIONS WITHOUT .ini WILL NOT BE ACCEPTED!\n")
			print("    ZIP UP THE .ini FILE, THE PARCEL FILE GEODATABASE, THE OTHER_LAYERS FILE GEODATABASE, AND SUBMIT TO THE LTSB Geodata Collector,\n") 
			# print("  at  https://geodatacollector.legis.wisconsin.gov/")
			# print("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
		else:
			print (' cannot create gdbs')	