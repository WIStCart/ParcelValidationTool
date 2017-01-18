import arcpy
import _97V2dict
# TODO:
# 1) ...

class Summary:

	def __init__(self):
		pass #placeholder

	def writeSummaryTxt(Summary,outDirTxt,outName,totError):
		#Write general error report to .txt
		Summary.errorSummaryFile = open(outDirTxt + "/" + outName + "_ValidationSummary.txt","w")
		arcpy.AddMessage("Creating Validation Summary here: " + outDirTxt + "/" + outName + "_ValidationSummary.txt")
		Summary.errorSummaryFile.write(outDirTxt + "\\" + outName + "_ValidationSummary.txt" + "\n")
		Summary.errorSummaryFile.write("Validation Summary Table: " + "\n")
		Summary.errorSummaryFile.write("This validation summary table contains an overview of any errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary." + "\n\n")
		Summary.errorSummaryFile.write("************************************************************************\n")
		Summary.errorSummaryFile.write("In-line errors - The following lines summarize the element-specific errors that were found while validating your parcel dataset. The stats below are meant as a means of reviewing the output. Please see the " + "GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields in the output feature class to address these errors individually."+ "\n")
		Summary.errorSummaryFile.write("	General Errors: " + str(totError.generalErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Geometric Errors: " + str(totError.geometricErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Address Errors: " + str(totError.addressErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Tax Errors: " + str(totError.taxErrorCount) + "\n")
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
		Summary.errorSummaryFile.write("-->If there is a large discrepancy between the values (mainly a large decrease in number of populated values, please ensure data wasn't missed/lost in processing.\n\n")
		Summary.errorSummaryFile.write("				V2 Stats						V3 Stats						Difference \n")





		Summary.errorSummaryFile.write("\n\n\n* Within: " + outDirTxt + "\\" + outName  + "\n") 
		Summary.errorSummaryFile.write("************************************************************************\n")
		Summary.errorSummaryFile.write("In-line errors - The following lines explain any broad geometric errors that were found while validating your parcel dataset."+ "\n")
		if len(totError.geometricPlacementErrors) != 0:
			for geometricErrorMessage in totError.geometricPlacementErrors:
				Summary.errorSummaryFile.write("	General geometric error: " + str(geometricErrorMessage) + "\n")
		if len(totError.geometricFileErrors) != 0:
			for geometricErrorMessage in totError.geometricFileErrors:
				Summary.errorSummaryFile.write("	General geometric error: " + str(geometricErrorMessage) + "\n")
		if (len(totError.geometricFileErrors) == 0) and (len(totError.geometricPlacementErrors) == 0):
			Summary.errorSummaryFile.write("	*No broad-level geometric errors found!" + "\n")