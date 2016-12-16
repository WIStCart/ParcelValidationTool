import arcpy
from Parcel import Parcel
# TODO
# 1) Write exceptions on the function itself, per function. 
#		a) Include errors in-line with the row (just like all other errors)      
# 		b) try/catch/throw 
# 		c) apply exceptions in last step of writing the function - to prevent from accidentally escaping errors that we can test for.
#		d) For more: http://pro.arcgis.com/en/pro-app/arcpy/get-started/error-handling-with-python.htm
#		e) About error codes: http://pro.arcgis.com/en/pro-app/tool-reference/appendices/understanding-geoprocessing-tool-errors-and-warnings.htm

class Error:

	def __init__(self):
		self.generalErrorCount = 0
		self.geometricErrorCount = 0
		self.addressErrorCount = 0
		self.taxErrorCount = 0
		self.attributeFileErrors = []
		self.geometricFileErrors = []

	#Check if the coordinate reference system is consistent with that of the parcel initiative (Error object, feature class)
	def checkCRS(Error,featureClass):
		try:
			desc = arcpy.Describe(featureClass)
			spatialReference = desc.spatialReference
			# Test for the Polygon feature class against the parcel project's, shape type, projection name, and units.
			if desc.shapeType != "Polygon":
				Error.geometricFileErrors.append("The feature class should be of polygon type instead of: " + desc.shapeType)
			if spatialReference.name != "NAD_1983_HARN_Wisconsin_TM":
				Error.geometricFileErrors.append("The feature class should be 'NAD_1983_HARN_Wisconsin_TM' instead of: " + spatialReference.name + " Please follow this documentation: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf to project native data to the Statewide Parcel CRS")
			return Error
		except: # using generic error handling because we don't know what errors to expect yet.
			Error.geometricFileErrors.append("The feature class's coordinate reference system could not be validated. Please ensure that the feature class is projected to the Statewide Parcel CRS. This documentation may be of use in projecting the dataset: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf.")
			return Error

	#Check if text value is a valid number(Error object, Parcel object, field to test, type of error to classify this as, are <Null>s are considered errors?)
	def checkNumericTextValue(Error,Parcel,field,errorType,acceptNull): 
		try:
			stringToTest = getattr(Parcel,field)
			if stringToTest is not None:
				if stringToTest.isdigit():
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Error on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
			else:
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the" + field.upper() + "field. Please inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check if duplicates exist within an entire field(Error object, Parcel object, field to test, type of error to classify this as, are <Null>s are considered errors?, list of strings that are expected to be duplicates (to ignore), running list of strings to test against)  
	def checkIsDuplicate(Error,Parcel,field,errorType,acceptNull,ignoreList,testList):
		try:
			stringToTest = getattr(Parcel,field)
			if stringToTest is not None:
				if stringToTest in ignoreList:
					pass
				else:
					if stringToTest in testList:
						getattr(Parcel,errorType + "Errors").append("Appears to be a duplicate value in " + field.upper())
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					else:
						testList.append(stringToTest)
				return (Error, Parcel)
			else:
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check to see if a domain string is within a list (good) otherwise report to user it isn't found..
	def checkDomainString(Error,Parcel,field,errorType,acceptNull,testList):
		try:
			stringToTest = getattr(Parcel,field)
			if stringToTest is not None:
				if stringToTest in testList:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " not in acceptable domain list.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
			else:
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			arcpy.AddMessage("Hitting except statement")
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)


	#Will contain get, set, display methods

	#Any other total error report data will go here