import arcpy

class Summary:

	def __init__(self):
		pass

	def writeSummaryTxt(Summary,outDirTxt,outName,totError):
		#Write general error report
		Summary.errorSummaryFile = open(outDirTxt + "/" + outName + "_ValidationSummary.txt","w")
		arcpy.AddMessage("Creating Validation Summary here: " + outDirTxt + "/" + outName + "_ValidationSummary.txt")
		Summary.errorSummaryFile.write(outDirTxt + "\\" + outName + "_ValidationSummary.txt" + "\n")
		Summary.errorSummaryFile.write("Validation Summary Table: " + "\n")
		Summary.errorSummaryFile.write("This validation summary table contains an overview of any errors found by the Parcel Validation Tool. Please review the contents of this file and make changes to your parcel dataset as necessary." + "\n\n")
		Summary.errorSummaryFile.write("In-line errors - The following lines summarize the element-specific errors that were found while validating your parcel dataset. The stats below are meant as a means of reviewing the output. Please see the " + "GeneralElementErrors, AddressElementErrors, TaxrollElementErrors, and GeometricElementErrors fields in the output feature class to address these errors individually."+ "\n")
		Summary.errorSummaryFile.write("	General Errors: " + str(totError.genErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Geometric Errors: " + str(totError.geomErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Address Errors: " + str(totError.addressErrorCount) + "\n")
		Summary.errorSummaryFile.write("	Tax Errors: " + str(totError.taxErrorCount) + "\n")
		Summary.errorSummaryFile.write("* Within: " + outDirTxt + "\\" + outName  + "\n")
