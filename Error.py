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

	def testCheckNum(Error,Parcel):
		if Parcel.addnum:
			if Parcel.addnum.isdigit():
				Parcel.addressErrors.append("All Digits")
			else:
				Parcel.addressErrors.append("Error")
				Error.addressErrorCount += 1
			return (Error, Parcel)
		else:
			Parcel.addressErrors.append("All Digits")
			return (Error, Parcel)
	#Check if text value is a valid number(Error object, Parcel object, field to test, type of error to classify this as, are <Null>s are considered errors?)  
	def checkNumericTextValue(Error,Parcel,field,errorType,acceptNull): 
		try:
			stringToTest = getattr(Parcel,field)
			if stringToTest is not None:
				if stringToTest.isdigit():
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Error on " + field)
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
			else:
				if acceptNull == False:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field)
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the" + field + "field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)

	#Check if duplicates exist within an entire field(Error object, Parcel object, field to test, type of error to classify this as, are <Null>s are considered errors?)  
	def checkIsDuplicate(Error,Parcel,field,errorType,acceptNull,ignoreList,testList):
		stringToTest = getattr(Parcel,field)
		if stringToTest is not None:
			if stringToTest in ignoreList:
				pass
			else:
				if stringToTest in testList:
					getattr(Parcel,errorType + "Errors").append("Appears to be a duplicate value in " + field)
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				else:
					testList.append(stringToTest)
			return (Error, Parcel)
		else:
			if acceptNull == False:
				pass
			else:
				getattr(Parcel,errorType + "Errors").append("Null Found on " + field)
		return (Error, Parcel)
		#test comment

	#Will contain get, set, display methods

	#Any other total error report data will go here
