import arcpy
import math
from Parcel import Parcel
# TODO
# 1) Write exceptions on the function itself, per function. 
#		a) Include errors in-line with the row (just like all other errors)      
# 		b) try/catch/throw 
# 		c) apply exceptions in last step of writing the function - to prevent from accidentally escaping errors that we can test for.
#		d) For more: http://pro.arcgis.com/en/pro-app/arcpy/get-started/error-handling-with-python.htm
#		e) About error codes: http://pro.arcgis.com/en/pro-app/tool-reference/appendices/understanding-geoprocessing-tool-errors-and-warnings.htm

class Error:

	def __init__(self,featureClass):
		self.generalErrorCount = 0
		self.geometricErrorCount = 0
		self.addressErrorCount = 0
		self.taxErrorCount = 0
		self.attributeFileErrors = []
		self.geometricFileErrors = []
		self.geometricPlacementErrors = ["Several parcel geometries appear to be spatially misplaced when comparing them against last year's parcel geometries. This issue is indicative of a re-projection error. Please see the following documentation: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf for advice on how to project native data to the Statewide Parcel CRS."]
		#other class variables
		self.pinSkipCount = 0
		self.trYearPast = 0
		self.trYearExpected = 0
		self.trYearFuture = 0
		self.trYearOther = 0
		self.recordIterationCount = 0;
		self.recordTotalCount = int(arcpy.GetCount_management(featureClass).getOutput(0)) # Total number of records in the feature class
		self.checkEnvelopeInterval = math.trunc(self.recordTotalCount / 10) # Interval value used to apply 10 total checks on records at evenly spaced intervals throughout the dataset.
		self.nextEnvelopeInterval = self.checkEnvelopeInterval

	# Test records throughout the dataset to ensure that polygons exist within an actual county envelope ("Waukesha" issue or the "Lake Michigan" issue). 
	def checkGeometricQuality(self,Parcel):
		if self.nextEnvelopeInterval == self.recordIterationCount:
			countyEnvelope = self.testCountyEnvelope(Parcel)
			if countyEnvelope == "Valid": # would mean that the "Waukesha" issue or the "Lake Michigan" issue does not exist in this dataset.
				self.nextEnvelopeInterval = 4000000
				self.geometricPlacementErrors = []
			else:
				self.nextEnvelopeInterval = self.nextEnvelopeInterval + self.checkEnvelopeInterval
		self,Parcel = self.testParcelGeometry(Parcel)
		self.recordIterationCount += 1
		return (self, Parcel)
	
	# Will test the row against LTSB's feature service to identify if the feature is in the correct location.   
	def testCountyEnvelope(self,Parcel):
		# For sake of saving time while developing, am setting this function to auto-return "Valid" because it takes about 1 min to execute each of these tests.
		'''
		baseURL = "http://mapservices.legis.wisconsin.gov/arcgis/rest/services/WLIP/PARCELS/FeatureServer/0/query"
		where = str(Parcel.parcelid)
		query = "?f=json&where=UPPER(PARCELID)%20=%20UPPER(%27{}%27)&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=OBJECTID%2CPARCELID%2CTAXPARCELID%2CCONAME%2CPARCELSRC&outSR=3071&resultOffset=0&resultRecordCount=10000".format(where)
		fsURL = baseURL + query
		arcpy.AddMessage(fsURL)
		fs = arcpy.FeatureSet()
		fs.load(fsURL)
		with arcpy.da.UpdateCursor(fs,["SHAPE@XY"]) as cursorLTSB:
			for rowLTSB in cursorLTSB:
				v2x = round(rowLTSB[0][0],2)
				v1x = round(Parcel.shapeXY[0],2)
				v2y = round(rowLTSB[0][1],2)
				v1y = round(Parcel.shapeXY[1],2)
				if (v2x == v1x) and (v2y == v1y):
					return "Valid"
				else:
					return "Not Confirmed"
		'''
		return "Valid"

	def testParcelGeometry(self,Parcel):
		# Test for null geometries or other oddities 
		try:
			geom = Parcel.shape
			xCent = geom.centroid.X
			yCent = geom.centroid.Y
		except:
			Parcel.geometricErrors.append("The error observed is indicative of a corrupt parcel geometry. See <SITE> for detail on how to troubleshoot.")
			self.geometricErrorCount =+ 1
		try:
			areaP = Parcel.shapeArea
			lengthP = Parcel.shapeLength
			if areaP < 0.01:
				Parcel.geometricErrors.append("Short sliver polygon: AREA = " + str(areaP))
				self.geometricErrorCount =+ 1
			if lengthP < 0.01:
				Parcel.geometricErrors.append("Polygon below threshold size: LENGTH = " + str(lengthP))
				self.geometricErrorCount =+ 1
			if (areaP/lengthP) < 0.01:
				Parcel.geometricErrors.append("Long sliver polygon: AREA/LENGTH = " + str(areaP/lengthP))
				self.geometricErrorCount =+ 1				
		except:
			Parcel.geometricErrors.append("The error observed is indicative of a corrupt parcel geometry. See <SITE> for detail on how to troubleshoot.")
			self.geometricErrorCount =+ 1
		return self,Parcel

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
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check to see if taxroll year provided is what expected, old, future or other value (which we plan to ask for explaination in submission form...)
	def trYear(Error,Parcel,field,pinField,errorType,acceptNull,ignoreList,acceptYears):
		try:
			stringToTest = getattr(Parcel,field)
			pinToTest = getattr(Parcel,pinField)
			if stringToTest is not None:
				if stringToTest == acceptYears[0]:
					Error.trYearPast += 1
				elif stringToTest == acceptYears[1]:
					Error.trYearExpected += 1
				elif stringToTest == acceptYears[2] or stringToTest == acceptYears[3]:
					Error.trYearFuture += 1
				else:
					Error.trYearOther += 1
				return (Error, Parcel)
			else:
				if acceptNull:
					pass
				else:
					if pinToTest in ignoreList:
						Error.pinSkipCount += 1
					else:
						getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper() + " field and value is expected.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)



	#Check to see if street name provided is within a list created from V2.
	def streetNameCheck(Error,Parcel,field,siteAddField,errorType,acceptNull,stnamelist):
		try:
			stringToTest = getattr(Parcel,field)
			siteAddToTest = getattr(Parcel,siteAddField)
			if stringToTest is not None:
				if stringToTest in stnamelist:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not appear in list created from V2 data. Please verify this value is correct.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return(Error, Parcel)
			else:
				if siteAddToTest is not None and stringToTest is None:
					getattr(Parcel,errorType + "Errors").append(field.upper() + " is Null, but " + siteAddField.upper() + " is populated.  Please ensure elements are in the appropriate field.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return(Error, Parcel)
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper() + " field and value is expected.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)


	#verify that the values provided in the zip field are 5 digits in length and begin with a '5'.
	def zipCheck(Error,Parcel,field,errorType,acceptNull):
		try:
			stringToTest = getattr(Parcel,field)
			if stringToTest is not None:
				if len(stringToTest) == 5 and stringToTest[0] == '5':
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " is either not 5 digits long or does not appear to be a Wisconsin zipcode.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return(Error,Parcel)
			else:
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper() + " field and value is expected.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)


	#Verify that value in Improved field is correct based on value provided in Impvalue field...
	#We may want/need to tweak the logic in here depending on how strictly we enforce the value of <Null> allowed in Impvalue field (i.e. Only for non-tax parcels or allow either 0 or <Null>)
	def impCheck(Error,Parcel,field,impValField,errorType):
		try:
			stringToTest = getattr(Parcel,field)
			impvalue = getattr(Parcel,impValField)
			if stringToTest == None and impvalue == None:
				pass
			elif stringToTest == 'NO' and impvalue == 0:
				pass
			elif stringToTest == 'YES' and impvalue > 0:
				pass
			else:
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not correspond with 'IMPVALUE' observed for this record.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)



	#Will contain get, set, display methods

	#Any other total error report data will go here