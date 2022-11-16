import arcpy, collections
from Parcel import Parcel
from LegacyCountyStats import *
import json
import webbrowser
from ConfigParser import ConfigParser
import os
import sys

class Summary:

	def __init__(self):
		pass #placeholder

	def writeSummaryTxt(Summary,outDirTxt,outName,totError,outPage,outJSON):
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
					#'IMPROVED':  str(totError.comparisonDict["IMPROVED"]),
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
			Summary.errorSummaryFile = open(outDirTxt + "/" + outName + "_ValidationSummary.txt","w")
			("Creating Validation Summary here: " + outDirTxt + "/" + outName + "_ValidationSummary.txt")
			Summary.errorSummaryFile.write(outDirTxt + "\\" + outName + "_ValidationSummary.txt" + "\n")
			Summary.errorSummaryFile.write("Validation Summary Table: " + "\n")
			Summary.errorSummaryFile.write("This validation summary table contains an overview of any errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary." + "\n\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			Summary.errorSummaryFile.write("* In-line errors\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			Summary.errorSummaryFile.write("The following lines summarized the element-specific errors that were found while validating your parcel dataset.  The stats below are meant as a means of reviewing the output.  Please see the GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields to address these errors individually.\n")
			Summary.errorSummaryFile.write("	General Errors: " + str(totError.generalErrorCount) + "\n")
			Summary.errorSummaryFile.write("	Geometric Errors: " + str(totError.geometricErrorCount) + "\n")
			Summary.errorSummaryFile.write("	Address Errors: " + str(totError.addressErrorCount) + "\n")
			Summary.errorSummaryFile.write("	Tax Errors: " + str(totError.taxErrorCount) + "\n")
			Summary.errorSummaryFile.write("	------------------\n")
			Summary.errorSummaryFile.write("	ERROR SUM: " + str(totError.ErrorSum ) + "\n")
			if totError.ErrorSum == 0:
				Summary.errorSummaryFile.write("\n	GREAT JOB, NO ERRORS!!!!!! \n")
			Summary.errorSummaryFile.write("\n\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			Summary.errorSummaryFile.write("* Uniform ParcelDate:\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			if totError.uniqueparcelDatePercent >= 97.0:
				Summary.errorSummaryFile.write( str(round (totError.uniqueparcelDatePercent,2)) + "% of all records contain the same PARCELDATE value\n")
				Summary.errorSummaryFile.write("Review submission documentation and set <Null> if necessary.\n\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			Summary.errorSummaryFile.write("* Broad-level errors:\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			Summary.errorSummaryFile.write("The following lines explain any broad geometric errors that were found while validating your parcel dataset."+ "\n")
			if len(totError.geometricPlacementErrors) != 0:
				for geometricErrorMessage in totError.geometricPlacementErrors:
					Summary.errorSummaryFile.write("	Geometric Misplacement Flag: " + str(geometricErrorMessage) + "\n")
					Validation_JSON["broadLevelErrors"]['Geometric_Misplacement_Flag'].append(str(geometricErrorMessage))
			if len(totError.geometricFileErrors) != 0:
				for geometricErrorMessage in totError.geometricFileErrors:
					Summary.errorSummaryFile.write("	Geometric File Error: " + str(geometricErrorMessage) + "\n")
					Validation_JSON["broadLevelErrors"]['Geometric_File_Error'].append(str(geometricErrorMessage))
			if (len(totError.geometricFileErrors) == 0) and (len(totError.geometricPlacementErrors) == 0):
				Summary.errorSummaryFile.write("	*No broad-level geometric errors found!" + "\n")
				Validation_JSON["broadLevelErrors"]['Geometric_File_Error'].append("None")
				Validation_JSON["broadLevelErrors"]['Geometric_Misplacement_Flag'].append("None")
			Summary.errorSummaryFile.write("\n\n")
			Summary.errorSummaryFile.write("Percentage of records with various Taxroll Years" + "\n")
			Summary.errorSummaryFile.write("	Previous Taxroll Year: " + str(round((float(totError.trYearPast / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			Summary.errorSummaryFile.write("	Expected Taxroll Year: " + str(round((float(totError.trYearExpected / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			Summary.errorSummaryFile.write("	Future Taxroll Years: " + str(round((float(totError.trYearFuture / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			Summary.errorSummaryFile.write("	Other Taxroll Years: " + str(round((float(totError.trYearOther / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n")
			Summary.errorSummaryFile.write("\n\n")
			Summary.errorSummaryFile.write("Records missing CONAME, PARCELFIPS, or PARCELSOURCE" + "\n")
			Summary.errorSummaryFile.write("	Missing CONAME: " + str(totError.coNameMiss) + "\n")
			Summary.errorSummaryFile.write("	Missing PARCELFIPS: " + str(totError.fipsMiss) + "\n")
			Summary.errorSummaryFile.write("	Missing PARCELSRC: " + str(totError.srcMiss) + "\n\n")
			Summary.errorSummaryFile.write("If any of the above values are greater than 0, please add missing values.  These 3 fields should be populated for all records submitted.\n\n\n")
			Summary.errorSummaryFile.write("BELOW IS A COMPARISON OF COMPLETENESS VALUES FROM YOUR PREVIOUS PARCEL SUBMISSION AND THIS CURRENT SUBMISSION.\n")
			Summary.errorSummaryFile.write("-->If the value shown is a seemingly large negative number, please verify that all data was joined correctly and no data was lost during processing.\n")
			Summary.errorSummaryFile.write("-->Note: This does not necessarily mean your data is incorrect, we just want to highlight large discrepancies that could indicate missing or incorrect data.\n\n")
			Summary.errorSummaryFile.write("          FIELD     DIFFERENCE\n")
			Summary.errorSummaryFile.write("         ------     ----------\n")
			Summary.errorSummaryFile.write("       PARCELID:  " + str(totError.comparisonDict["PARCELID"]) + '\n')
			Summary.errorSummaryFile.write("    TAXPARCELID:  " + str(totError.comparisonDict["TAXPARCELID"]) + '\n')
			Summary.errorSummaryFile.write("     PARCELDATE:  " + str(totError.comparisonDict["PARCELDATE"]) + '\n')
			Summary.errorSummaryFile.write("    TAXROLLYEAR:  " + str(totError.comparisonDict["TAXROLLYEAR"]) + '\n')
			Summary.errorSummaryFile.write("      OWNERNME1:  " + str(totError.comparisonDict["OWNERNME1"]) + '\n')
			Summary.errorSummaryFile.write("      OWNERNME2:  " + str(totError.comparisonDict["OWNERNME2"]) + '\n')
			Summary.errorSummaryFile.write("     PSTLADRESS:  " + str(totError.comparisonDict["PSTLADRESS"]) + '\n')
			Summary.errorSummaryFile.write("     SITEADRESS:  " + str(totError.comparisonDict["SITEADRESS"]) + '\n')
			Summary.errorSummaryFile.write("   ADDNUMPREFIX:  " + str(totError.comparisonDict["ADDNUMPREFIX"]) + '\n')
			Summary.errorSummaryFile.write("         ADDNUM:  " + str(totError.comparisonDict["ADDNUM"]) + '\n')
			Summary.errorSummaryFile.write("   ADDNUMSUFFIX:  " + str(totError.comparisonDict["ADDNUMSUFFIX"]) + '\n')
			Summary.errorSummaryFile.write("         PREFIX:  " + str(totError.comparisonDict["PREFIX"]) + '\n')
			Summary.errorSummaryFile.write("     STREETNAME:  " + str(totError.comparisonDict["STREETNAME"]) + '\n')
			Summary.errorSummaryFile.write("     STREETTYPE:  " + str(totError.comparisonDict["STREETTYPE"]) + '\n')
			Summary.errorSummaryFile.write("         SUFFIX:  " + str(totError.comparisonDict["SUFFIX"]) + '\n')
			Summary.errorSummaryFile.write("   LANDMARKNAME:  " + str(totError.comparisonDict["LANDMARKNAME"]) + '\n')
			Summary.errorSummaryFile.write("       UNITTYPE:  " + str(totError.comparisonDict["UNITTYPE"]) + '\n')
			Summary.errorSummaryFile.write("         UNITID:  " + str(totError.comparisonDict["UNITID"]) + '\n')
			Summary.errorSummaryFile.write("      PLACENAME:  " + str(totError.comparisonDict["PLACENAME"]) + '\n')
			Summary.errorSummaryFile.write("        ZIPCODE:  " + str(totError.comparisonDict["ZIPCODE"]) + '\n')
			Summary.errorSummaryFile.write("           ZIP4:  " + str(totError.comparisonDict["ZIP4"]) + '\n')
			Summary.errorSummaryFile.write("     SCHOOLDIST:  " + str(totError.comparisonDict["SCHOOLDIST"]) + '\n')
			Summary.errorSummaryFile.write("   SCHOOLDISTNO:  " + str(totError.comparisonDict["SCHOOLDISTNO"]) + '\n')
			#Summary.errorSummaryFile.write("       IMPROVED:  " + str(totError.comparisonDict["IMPROVED"]) + '\n')
			Summary.errorSummaryFile.write("   CNTASSDVALUE:  " + str(totError.comparisonDict["CNTASSDVALUE"]) + '\n')
			Summary.errorSummaryFile.write("       LNDVALUE:  " + str(totError.comparisonDict["LNDVALUE"]) + '\n')
			Summary.errorSummaryFile.write("       IMPVALUE:  " + str(totError.comparisonDict["IMPVALUE"]) + '\n')
			Summary.errorSummaryFile.write("       MFLVALUE:  " + str(totError.comparisonDict["MFLVALUE"]) + '\n')
			Summary.errorSummaryFile.write("    ESTFMKVALUE:  " + str(totError.comparisonDict["ESTFMKVALUE"]) + '\n')
			Summary.errorSummaryFile.write("       NETPRPTA:  " + str(totError.comparisonDict["NETPRPTA"]) + '\n')
			Summary.errorSummaryFile.write("       GRSPRPTA:  " + str(totError.comparisonDict["GRSPRPTA"]) + '\n')
			Summary.errorSummaryFile.write("      PROPCLASS:  " + str(totError.comparisonDict["PROPCLASS"]) + '\n')
			Summary.errorSummaryFile.write("       AUXCLASS:  " + str(totError.comparisonDict["AUXCLASS"]) + '\n')
			Summary.errorSummaryFile.write("      ASSDACRES:  " + str(totError.comparisonDict["ASSDACRES"]) + '\n')
			Summary.errorSummaryFile.write("      DEEDACRES:  " + str(totError.comparisonDict["DEEDACRES"]) + '\n')
			Summary.errorSummaryFile.write("       GISACRES:  " + str(totError.comparisonDict["GISACRES"]) + '\n')
			Summary.errorSummaryFile.write("         CONAME:  " + str(totError.comparisonDict["CONAME"]) + '\n')
			Summary.errorSummaryFile.write("     PARCELFIPS:  " + str(totError.comparisonDict["PARCELFIPS"]) + '\n')
			Summary.errorSummaryFile.write("      PARCELSRC:  " + str(totError.comparisonDict["PARCELSRC"]) + '\n')
			Summary.errorSummaryFile.write("\n\n\n* Within: " + outDirTxt + "\\" + outName  + "\n")
			Summary.errorSummaryFile.write("************************************************************************\n")
			Summary.errorSummaryFile.close()
			# outJSON - # full (hard coded) path to the output .json file summary.js
			with open(outJSON, 'w') as outfile:
				outfile.write("var testValues = ")
				json.dump(Validation_JSON, outfile)
		except Exception as e:
			arcpy.AddMessage("  !!!!!!!!!!Error writing summary file!!!!!!!!!!")
			arcpy.AddMessage(str(e))
		webbrowser.open(outPage, new=2)

	def writeIniFile(self,inputDict,totError):
		arcpy.AddMessage("\n")
		arcpy.AddMessage("  Creating .ini file")
		config = ConfigParser()
		config = ConfigParser(allow_no_value=True)
		config.add_section('PARAMETERS')
		for key in inputDict.keys():
			if key != 'inCert':
				config.set('PARAMETERS',key,inputDict[key])

		if inputDict['isSearchable'] == 'true':
			config.add_section('ERROR COUNTS')
			config.set('ERROR COUNTS','General',totError.generalErrorCount)
			config.set('ERROR COUNTS','Geometric',totError.geometricErrorCount)
			config.set('ERROR COUNTS','Address',totError.addressErrorCount)
			config.set('ERROR COUNTS','Tax',totError.taxErrorCount)
			config.set('ERROR COUNTS','-------------------')
			config.set('ERROR COUNTS','Error Sum',totError.ErrorSum)
			if totError.ErrorSum == 0:
				config.set('ERROR COUNTS','    GREAT JOB, NO ERRORS!!!!!!!')
			config.add_section('PARCELDATE FLAG')
			if totError.uniqueparcelDatePercent >= 97.0:
				config.set('PARCELDATE FLAG', 'Uniform ParcelDate', str(round (totError.uniqueparcelDatePercent,2)) )
			if totError.uniqueparcelDatePercent < 97.0:
				config.set('PARCELDATE FLAG','  GREAT JOB, NO UNIFORM PARCELDATE!' )			
			config.add_section('PERCENT TAXROLL YEAR')
			config.set('PERCENT TAXROLL YEAR','Previous',round((float(totError.trYearPast / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2))
			config.set('PERCENT TAXROLL YEAR','Expected',round((float(totError.trYearExpected / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2))
			config.set('PERCENT TAXROLL YEAR','Future',round((float(totError.trYearFuture / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2))
			config.set('PERCENT TAXROLL YEAR','Other',round((float(totError.trYearOther / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2))
			config.add_section('MISSING RECORDS')
			config.set('MISSING RECORDS','CONAME',totError.coNameMiss)
			config.set('MISSING RECORDS','PARCELFIPS',totError.fipsMiss)
			config.set('MISSING RECORDS','PARCELSOURCE',totError.srcMiss)

			config.add_section('COMPARISON COMPLETENESS')
			for field in totError.comparisonDict.keys():
				if field != 'state' or field != 'loaddate':
					config.set('COMPARISON COMPLETENESS',field,totError.comparisonDict[field])

			config.add_section('EXPLAIN CERTIFY')
			explain_certify = inputDict['inCert']
			config.set('EXPLAIN CERTIFY','Explained Error Number', '\n' + explain_certify['explainedErrorsNumber'])
			config.set('EXPLAIN CERTIFY','Notice Of New StreetName', '\n' + explain_certify['noticeOfNewStreetName'])
			config.set('EXPLAIN CERTIFY','Notice Of New NonParcels IDs', '\n' + explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'])
			config.set('EXPLAIN CERTIFY','Notice Of Missing Data Omissions', '\n' + explain_certify['noticeOfMissingDataOmissions'])
			config.set('EXPLAIN CERTIFY','Notice Of Error Sum Unsolvable', '\n' + explain_certify['noticeErrorsSumsUnresolvable'])
			config.set('EXPLAIN CERTIFY','Other', '\n' + explain_certify['noticeOther'])
		
		try:
			#Write out .ini file
			with open(inputDict['outINIDir']+'/'+inputDict['county'] +'.ini','w') as configFile:
				config.write(configFile)
				#with open(inputDict['inCert'],'r') as certFile:
				#	for line in certFile:
						#configFile.write(line)
			arcpy.AddMessage("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			arcpy.AddMessage("  Wrote .ini file to "+inputDict['outINIDir'])
			arcpy.AddMessage("\n")
			arcpy.AddMessage("  ------>  .ini FILE CREATION COMPLETE!   <------\n\n")
			#arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
		except Exception as e:
			arcpy.AddMessage("  !!!!!!!!!!Error writing .ini file!!!!!!!!!!")
			arcpy.AddMessage(str(e))

	def explainCertComplete(self,explain_certify):
		#arcpy.AddMessage(explain_certify)
		if (explain_certify['noticeOfNewStreetName'] == '' or explain_certify['noticeOfNewStreetName'] == "Enter new Street Names here, or None if no Values exist") \
			    and (explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'] == ''  or explain_certify['noticeOfNewNonParcelFeaturePARCELIDs'] ==  "Enter new Non-Parcel Feature Parcel IDs, or None if no Values exist") \
				and (explain_certify['noticeOfMissingDataOmissions'] == '' or explain_certify['noticeOfMissingDataOmissions'] == "Enter omission information here, or None if no omissions exist") \
				and (explain_certify['noticeErrorsSumsUnresolvable'] == '' or explain_certify['noticeErrorsSumsUnresolvable'] == "Enter number of Unresolvable errors, or None if no Values exist"):
				
			arcpy.AddMessage("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			arcpy.AddMessage("     IMMEDIATE ISSUE REQUIRING ATTENTION")
			arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			arcpy.AddMessage("  IT DOESN'T APPEAR THAT YOU FULLY FILLED OUT THE EXPLAIN-CERTIFY INFORMATION REQUIRED FOR SUBMISSION.\n\n")
			arcpy.AddMessage("  PLEASE FILL OUT THIS INFORMATION IN IT'S ENTIRETY AND RE-RUN THE TOOL IN FINAL MODE.")
			arcpy.AddMessage("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			sys.tracebacklimit = 0
			raise NameError("\n     EXPLAIN-CERTIFY FORM INCOMPLETE")
  			#exit()
		else:
			pass 	
		
		

	def fieldConstraints(self,totError):
		if totError.coNameMiss > 0 or totError.fipsMiss > 0 or totError.srcMiss > 0:
			arcpy.AddMessage("\n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			arcpy.AddMessage("     IMMEDIATE ISSUE REQUIRING ATTENTION")
			arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			arcpy.AddMessage("  ONE OF THE FOLLOWING FIELDS: CONAME, PARCELSRC or PARCELFIPS ARE NOT FULLY POPULATED.\n\n")
			arcpy.AddMessage("  THESE FIELDS SHOULD BE POPULATED FOR EVERY RECORD IN THE SUMBITTED PARCEL FEATURE CLASS.\n\n")
			arcpy.AddMessage("  PLEASE ENSURE THESE FIELDS ARE POPULATED FOR ALL RECORDS AND RE-RUN THE TOOL IN FINAL MODE.")
			arcpy.AddMessage("n\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
			sys.tracebacklimit = 0
			raise NameError("\n     CONAME, PARCELSRC or PARCELFIPS NOT FULLY POPULATED")
			#exit()

			
	
	def createFGDBs (self, inputDict, taxRollYears):
		other_fc_list = ['zoningGenFC', 'zoningShoreFC','zoningAirFC', 'PLSSFC','RightOfWayFC','RoadStreetCenterlineFC','HydroLineFC','HydroPolyFC','AddressesFC','BuildingBuildingFootprintFC','LandUseFC','ParksOpenSpaceFC','TrailsFC','OtherRecreationFC']
		year = taxRollYears[2]
		inFC = inputDict['inFC']
		outPath = inputDict['outINIDir']  #folder for .ini, fgdbs and other plss files
		parcel_gdb = inputDict['county'] + '_PARCELS.gdb' 
		other_gdb =  inputDict['county'] + '_OTHER.gdb'
		redactPolicy = inputDict['redactPolicy']
		plssOtherDigitalFile = inputDict['PLSSOtherDigitalFile']
		
		#also need to check if the plss files is in other format
		#and the html or document with the names 

		if os.path.exists(outPath):
			arcpy.AddMessage("  Creating PARCEL and OTHER geodatabases\n")
			#creating PARCELS AND OTHER geodatabases
			if arcpy.Exists(os.path.join(outPath, other_gdb)):
				arcpy.Delete_management (os.path.join(outPath, other_gdb))

			if arcpy.Exists( os.path.join(outPath, parcel_gdb)):
				arcpy.Delete_management (os.path.join(outPath, parcel_gdb))
			
			def writePlssFile (outPath, plssOtherDigitalFile, other_gdb, year):
				""" If plss file is different"""
				import shutil			
				import os.path
		
				plss_file = plssOtherDigitalFile.split('/')
				plss_file_name = plss_file[len(plss_file)-1]
				destination = outPath + '/' + plss_file_name 
				extension = plss_file_name.split('.')[-1]
	
				if extension != 'shp':	
					if not os.path.isfile(destination):
						shutil.copy(plssOtherDigitalFile, destination)
						arcpy.AddMessage("\n\n")
						arcpy.AddMessage("  Wrote PLSS file to "+ destination)
						arcpy.AddMessage("\n")
						arcpy.AddMessage("  ------>  PLSS FILE COPIED SUCCESSFULLY!  <------\n")
						#arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
					else:
						pass     #print("\n\n  PLSS file already existed.\n")
				else:   # for shape files use arcpy
					if arcpy.Exists(plssOtherDigitalFile):   #double check that the shapefile exists
						desc = arcpy.Describe(plssOtherDigitalFile)
						if  hasattr(desc, "dataType") and desc.dataType == "ShapeFile":
							plss_path = outPath + '/' + other_gdb
							plss_name = '/PLSS_' + year 
							#print ( plss_path + plss_name )
							if arcpy.Exists (plss_path + plss_name):	
								arcpy.Delete_management(plss_path + plss_name)
							arcpy.FeatureClassToFeatureClass_conversion(plssOtherDigitalFile, plss_path, plss_name)
							arcpy.AddMessage("\n\n")
							arcpy.AddMessage("  Wrote PLSS file to "+ plss_path + plss_name)
							arcpy.AddMessage("\n")
							arcpy.AddMessage("  ------>  PLSS FILE COPIED SUCCESSFULLY!  <------\n")




			### create Parcels gdb	
			if inputDict['inFC'] != '':
				parcel_Dir = arcpy.CreateFileGDB_management(outPath, parcel_gdb)
				arcpy.FeatureClassToFeatureClass_conversion(inFC, parcel_Dir,"PARCELS")

			#Create fgdb for other layers				
			# append inFeatures list other features provided in the GUI
			inFeatures = []
			for fc in other_fc_list:  
				if inputDict[fc] != '' and  (arcpy.Exists(inputDict[fc])):
					#matching  fc with it name:
					if fc == 'zoningGenFC':
						fc_name = '/GENERAL_' + year
					elif fc ==  'zoningShoreFC':
						fc_name = '/SHORELAND_' + year
					elif fc == 'zoningAirFC':
						fc_name = '/AIRPORT_' + year
					elif fc == 'PLSSFC':
						fc_name =  '/PLSS_' + year
					elif fc == 'RightOfWayFC':
						fc_name = '/ROW_' + year
					elif fc ==  'RoadStreetCenterlineFC':
						fc_name = '/ROADS_' + year
					elif fc ==  'HydroLineFC':
						fc_name = '/HYDRO_' + year + '_LINE'
					elif fc == 'HydroPolyFC':
						fc_name = '/HYDRO_' + year + '_POLY'
					elif fc == 'AddressesFC': 
						fc_name = '/ADDRESSES_' + year
					elif fc == 'BuildingBuildingFootprintFC':
						fc_name = '/BUILDINGS_' + year
					elif fc == 'LandUseFC':
						fc_name = '/LANDUSE_' + year
					elif fc == 'ParksOpenSpaceFC':
						fc_name = '/PARKS_' + year 
					elif fc == 'TrailsFC':
						fc_name = '/TRAILS_' + year
					elif fc == 'OtherRecreationFC':
						fc_name = '/RECREATION_' + year	
					inFeatures.append( [inputDict[fc],  fc_name])  # list with Feat classes with their new neme 

			if inFeatures != []:
				other_Dir = arcpy.CreateFileGDB_management(outPath, other_gdb)
				for oLFC in inFeatures:
					arcpy.FeatureClassToFeatureClass_conversion(oLFC[0], other_Dir, oLFC[1])
			if (inputDict['PLSSType'] != '' and inputDict['PLSSType'] == 'Maintained by county as other digital format'):
				#need to check for shapefile 
				if inFeatures == []:  #if no other layers existed
					other_Dir = arcpy.CreateFileGDB_management(outPath, other_gdb)
				writePlssFile ( outPath, plssOtherDigitalFile, other_gdb, year)
			

			arcpy.AddMessage("  ------>  GEODATABASES CREATION COMPLETE!  GREAT WORK!!  <------\n\n\n")
			arcpy.AddMessage("  SUBMISSIONS WITHOUT .ini WILL NOT BE ACCEPTED!\n")
			arcpy.AddMessage("  ZIP UP THE .ini FILE, THE PARCEL FILE GEODATABASE, THE OTHER_LAYERS FILE GEODATABASE, AND SUBMIT TO THE LTSB Geodata Collector,\n") 
			arcpy.AddMessage("  at  https://geodatacollector.legis.wisconsin.gov/")
			arcpy.AddMessage("\n  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")