import arcpy
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
		Summary.errorSummaryFile.write("	Other Taxroll Years: " + str(round((float(totError.trYearOther / float((totError.recordTotalCount - totError.pinSkipCount)))*100),2)) + "%\n\n")
		Summary.errorSummaryFile.write("* Within: " + outDirTxt + "\\" + outName  + "\n") 
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