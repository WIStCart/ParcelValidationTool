import arcpy, collections
from configparser import ConfigParser

class Summary:

	def __init__(self):
		pass #placeholder

	def writeSummaryTxt(Summary,outDirTxt,outName,totError):
		#Write general error report to .txt
		Summary.errorSummaryFile = open(outDirTxt + "/" + outName + "_ValidationSummary.txt","w")
		("Creating Validation Summary here: " + outDirTxt + "/" + outName + "_ValidationSummary.txt")
		Summary.errorSummaryFile.write(outDirTxt + "\\" + outName + "_ValidationSummary.txt" + "\n")
		Summary.errorSummaryFile.write("Validation Summary Table: " + "\n")
		Summary.errorSummaryFile.write("This validation summary table contains an overview of any errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary." + "\n\n")
		Summary.errorSummaryFile.write("************************************************************************\n")
		Summary.errorSummaryFile.write("* In-line errors:  (Specific errors written in-line within output feature class: " + str(outDir + outName) + ")\n")
		Summary.errorSummaryFile.write("************************************************************************\n")
		Summary.errorSummaryFile.write("The following lines summarized the element-specific errors that were found while validating your parcel dataset.  The stats below are meant as a means of reviewing the output.  Please see the GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields to address these errors individually.\n")
		Summary.errorSummaryFile.write("	General Errors: " + str(totError.generalErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Geometric Errors: " + str(totError.geometricErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Address Errors: " + str(totError.addressErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Tax Errors: " + str(totError.taxErrorCount) + "\n")
		Summary.errorSummaryFile.write("\n\n")
		Summary.errorSummaryFile.write("************************************************************************\n")
		Summary.errorSummaryFile.write("* Broad-level errors:")
		Summary.errorSummaryFile.write("************************************************************************\n")
		Summary.errorSummaryFile.write("The following lines explain any broad geometric errors that were found while validating your parcel dataset."+ "\n")
		if len(totError.geometricPlacementErrors) != 0:
			for geometricErrorMessage in totError.geometricPlacementErrors:
				Summary.errorSummaryFile.write("	General geometric error: " + str(geometricErrorMessage) + "\n")
		if len(totError.geometricFileErrors) != 0:
			for geometricErrorMessage in totError.geometricFileErrors:
				Summary.errorSummaryFile.write("	General geometric error: " + str(geometricErrorMessage) + "\n")
		if (len(totError.geometricFileErrors) == 0) and (len(totError.geometricPlacementErrors) == 0):
			Summary.errorSummaryFile.write("	*No broad-level geometric errors found!" + "\n")
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
		Summary.errorSummaryFile.write("-->If the value shown is a negative number greater than <insert number here>, please verify that all data was joined correctly and no data was lost during processing.\n")
		Summary.errorSummaryFile.write("-->Note: This does not necessarily mean your data is incorrect, we just want to highlight large discrepancies that could indicate missing or incorrect data.\n\n")
		Summary.errorSummaryFile.write("		FIELD   	DIFFERENCE\n")
		Summary.errorSummaryFile.write("		------		----------\n")
		Summary.errorSummaryFile.write("	   PARCELID: 	" + str(totError.comparisonDict["PARCELID"]) + '\n')
		Summary.errorSummaryFile.write("	TAXPARCELID: 	" + str(totError.comparisonDict["TAXPARCELID"]) + '\n')
		Summary.errorSummaryFile.write("	 PARCELDATE: 	" + str(totError.comparisonDict["PARCELDATE"]) + '\n')
		Summary.errorSummaryFile.write("	TAXROLLYEAR: 	" + str(totError.comparisonDict["TAXROLLYEAR"]) + '\n')
		Summary.errorSummaryFile.write("	  OWNERNME1: 	" + str(totError.comparisonDict["OWNERNME1"]) + '\n')
		Summary.errorSummaryFile.write("	  OWNERNME2: 	" + str(totError.comparisonDict["OWNERNME2"]) + '\n')
		Summary.errorSummaryFile.write("	 PSTLADRESS: 	" + str(totError.comparisonDict["PSTLADRESS"]) + '\n')
		Summary.errorSummaryFile.write("	 SITEADRESS: 	" + str(totError.comparisonDict["SITEADRESS"]) + '\n')
		Summary.errorSummaryFile.write("   ADDNUMPREFIX: 	" + str(totError.comparisonDict["ADDNUMPREFIX"]) + '\n')
		Summary.errorSummaryFile.write("		 ADDNUM: 	" + str(totError.comparisonDict["ADDNUM"]) + '\n')
		Summary.errorSummaryFile.write("   ADDNUMSUFFIX: 	" + str(totError.comparisonDict["ADDNUMSUFFIX"]) + '\n')
		Summary.errorSummaryFile.write("		 PREFIX: 	" + str(totError.comparisonDict["PREFIX"]) + '\n')
		Summary.errorSummaryFile.write("	 STREETNAME: 	" + str(totError.comparisonDict["STREETNAME"]) + '\n')
		Summary.errorSummaryFile.write("	 STREETTYPE: 	" + str(totError.comparisonDict["STREETTYPE"]) + '\n')
		Summary.errorSummaryFile.write("		 SUFFIX: 	" + str(totError.comparisonDict["SUFFIX"]) + '\n')
		Summary.errorSummaryFile.write("   LANDMARKNAME: 	" + str(totError.comparisonDict["LANDMARKNAME"]) + '\n')
		Summary.errorSummaryFile.write("	   UNITTYPE: 	" + str(totError.comparisonDict["UNITTYPE"]) + '\n')
		Summary.errorSummaryFile.write("		 UNITID: 	" + str(totError.comparisonDict["UNITID"]) + '\n')
		Summary.errorSummaryFile.write("	  PLACENAME: 	" + str(totError.comparisonDict["PLACENAME"]) + '\n')
		Summary.errorSummaryFile.write("		ZIPCODE: 	" + str(totError.comparisonDict["ZIPCODE"]) + '\n')
		Summary.errorSummaryFile.write("		   ZIP4: 	" + str(totError.comparisonDict["ZIP4"]) + '\n')
		Summary.errorSummaryFile.write("	 SCHOOLDIST: 	" + str(totError.comparisonDict["SCHOOLDIST"]) + '\n')
		Summary.errorSummaryFile.write("   SCHOOLDISTNO: 	" + str(totError.comparisonDict["SCHOOLDISTNO"]) + '\n')
		Summary.errorSummaryFile.write("	   IMPROVED: 	" + str(totError.comparisonDict["IMPROVED"]) + '\n')
		Summary.errorSummaryFile.write("   CNTASSDVALUE: 	" + str(totError.comparisonDict["CNTASSDVALUE"]) + '\n')
		Summary.errorSummaryFile.write("	   LNDVALUE: 	" + str(totError.comparisonDict["LNDVALUE"]) + '\n')
		Summary.errorSummaryFile.write("	   IMPVALUE: 	" + str(totError.comparisonDict["IMPVALUE"]) + '\n')
		Summary.errorSummaryFile.write("	FORESTVALUE: 	" + str(totError.comparisonDict["FORESTVALUE"]) + '\n')
		Summary.errorSummaryFile.write("	ESTFMKVALUE: 	" + str(totError.comparisonDict["ESTFMKVALUE"]) + '\n')
		Summary.errorSummaryFile.write("	   NETPRPTA: 	" + str(totError.comparisonDict["NETPRPTA"]) + '\n')
		Summary.errorSummaryFile.write("	   GRSPRPTA: 	" + str(totError.comparisonDict["GRSPRPTA"]) + '\n')
		Summary.errorSummaryFile.write("	  PROPCLASS: 	" + str(totError.comparisonDict["PROPCLASS"]) + '\n')
		Summary.errorSummaryFile.write("	   AUXCLASS: 	" + str(totError.comparisonDict["AUXCLASS"]) + '\n')
		Summary.errorSummaryFile.write("	  ASSDACRES: 	" + str(totError.comparisonDict["ASSDACRES"]) + '\n')
		Summary.errorSummaryFile.write("	  DEEDACRES: 	" + str(totError.comparisonDict["DEEDACRES"]) + '\n')
		Summary.errorSummaryFile.write("	   GISACRES: 	" + str(totError.comparisonDict["GISACRES"]) + '\n')
		Summary.errorSummaryFile.write("		 CONAME: 	" + str(totError.comparisonDict["CONAME"]) + '\n')
		Summary.errorSummaryFile.write("	 PARCELFIPS: 	" + str(totError.comparisonDict["PARCELFIPS"]) + '\n')
		Summary.errorSummaryFile.write("	  PARCELSRC: 	" + str(totError.comparisonDict["PARCELSRC"]) + '\n')
		Summary.errorSummaryFile.write("\n\n\n* Within: " + outDirTxt + "\\" + outName  + "\n") 
		Summary.errorSummaryFile.write("************************************************************************\n")
		

	def writeIniFile(self,inputDict,totError):
		arcpy.AddMessage("Creating .ini file")
		config = ConfigParser()
		config.add_section('PARAMETERS')
		for key in inputDict.keys():
			config.set('PARAMETERS',key,inputDict[key])

		if inputDict['isSearchable'] == 'true':
			config.add_section('ERROR COUNTS')
			config.set('ERROR COUNTS','General',totError.generalErrorCount)
			config.set('ERROR COUNTS','Geometric',totError.geometricErrorCount)
			config.set('ERROR COUNTS','Address',totError.addressErrorCount)
			config.set('ERROR COUNTS','Tax',totError.taxErrorCount)
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
		try: 
			#Write out .ini file
			with open(inputDict['outSummaryDir']+'/'+inputDict['county']+'_'+inputDict['outName']+'.ini','w') as configfile:
				config.write(configfile)
		except:
			arcpy.AddMessage("Error writing .ini file")