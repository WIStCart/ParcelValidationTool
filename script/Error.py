import arcpy
import math
from Parcel import Parcel
import re

class Error:

	def __init__(self,featureClass,coName):
		self.coName = coName
		self.generalErrorCount = 0
		self.geometricErrorCount = 0
		self.addressErrorCount = 0
		self.taxErrorCount = 0
		self.comparisonDict = {}
		self.attributeFileErrors = []
		self.geometricFileErrors = []
		self.geometricPlacementErrors = ["Several parcel geometries appear to be spatially misplaced when comparing them against last year's parcel geometries. This issue is indicative of a re-projection error. Please see the following documentation: http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf section #2, for advice on how to project native data to the Statewide Parcel CRS."]
		self.pinSkipCount = 0
		self.trYearPast = 0
		self.trYearExpected = 0
		self.trYearFuture = 0
		self.trYearOther = 0
		self.coNameMiss = 0
		self.fipsMiss = 0
		self.srcMiss = 0
		self.netMoreGrsCnt = 0
		self.recordIterationCount = 0;
		self.recordTotalCount = int(arcpy.GetCount_management(featureClass).getOutput(0)) # Total number of records in the feature class
		self.checkEnvelopeInterval = math.trunc(self.recordTotalCount / 10) # Interval value used to apply 10 total checks on records at evenly spaced intervals throughout the dataset.
		self.nextEnvelopeInterval = self.checkEnvelopeInterval

	# Test records throughout the dataset to ensure that polygons exist within an actual county envelope ("Waukesha" issue or the "Lake Michigan" issue). 
	def checkGeometricQuality(self,Parcel):
		#arcpy.AddMessage(self.nextEnvelopeInterval)
		#arcpy.AddMessage(self.recordIterationCount)
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
		try:
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
						arcpy.AddMessage("Parcel geometry validated.")
						return "Valid"
					else:
						arcpy.AddMessage("Parcel geometry not yet validated, will attempt another record.")
						return "Not Confirmed"
			# Call it valid If the query returns no features (failure to return features would not be caused by a misalignment) 
			return "Valid" 
		except:
			# Call it valid if an error happens (error would not be caused by a misalignment)
			return "Valid"
		return "Valid"

	def testParcelGeometry(self,Parcel):
		# Test for null geometries or other oddities 
		try:
			geom = Parcel.shape
			xCent = geom.centroid.X
			yCent = geom.centroid.Y
		except:
			Parcel.geometricErrors.append("Corrupt Geometry: The feature's geometry could not be accessed.")
			self.geometricErrorCount += 1
		try:
			areaP = Parcel.shapeArea
			lengthP = Parcel.shapeLength
			if areaP < 0.01:
				Parcel.geometricErrors.append("Sliver Polygon: AREA")
				self.geometricErrorCount += 1
			if lengthP < 0.01:
				Parcel.geometricErrors.append("Sliver Polygon: LENGTH")
				self.geometricErrorCount += 1
			if (areaP/lengthP) < 0.01:
				Parcel.geometricErrors.append("Sliver Polygon: AREA/LENGTH")
				self.geometricErrorCount += 1				
		except:
			Parcel.geometricErrors.append("Corrupt Geometry: The feature's area and/or length could not be accessed.")
			self.geometricErrorCount += 1
		return self,Parcel

	#Check if the coordinate reference system is consistent with that of the parcel initiative (Error object, feature class)
	def checkCRS(Error,featureClass):
		try:
			var = True
			shape = True
			coord = True
			desc = arcpy.Describe(featureClass)
			spatialReference = desc.spatialReference
			# Test for the Polygon feature class against the parcel project's, shape type, projection name, and units.
			if desc.shapeType != "Polygon":
				#Error.geometricFileErrors.append("The feature class should be of polygon type instead of: " + desc.shapeType)
				var = False
				shape = False
			if spatialReference.name != "NAD_1983_HARN_Wisconsin_TM":
				#Error.geometricFileErrors.append("The feature class should be 'NAD_1983_HARN_Wisconsin_TM' instead of: " + spatialReference.name + " Please follow this documentation: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf to project native data to the Statewide Parcel CRS")
				var = False
				coord = False
			#return Error
			if var == False:
				arcpy.AddMessage("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
				arcpy.AddMessage("   IMMEDIATE ERROR REQUIRING ATTENTION")
				arcpy.AddMessage("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
				if shape == False:
					arcpy.AddMessage("THE FEATURE CLASS SHOULD BE OF POLYGON TYPE INSTEAD OF: " + desc.shapeType.upper() + "\n")
					arcpy.AddMessage("PLEASE MAKE NEEDED ALTERATIONS TO THE FEATURE CLASS AND RUN THE TOOL AGAIN.\n")
					arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
					exit()
				if coord == False:
					arcpy.AddMessage("THE FEATURE CLASS SHOULD BE 'NAD_1983_HARN_Wisconsin_TM' INSTEAD OF: " + spatialReference.name + "\n")
					arcpy.AddMessage("PLEASE FOLLOW THIS DOCUMENTATION: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf TO PROJECT NATIVE DATA TO THE STATEWIDE PARCEL CRS\n")
					arcpy.AddMessage("PLEASE MAKE NEEDED ALTERATIONS TO THE FEATURE CLASS AND RUN THE TOOL AGAIN.\n")
					arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
					exit()
		except: # using generic error handling because we don't know what errors to expect yet.
			arcpy.AddMessage("The feature class's coordinate reference system could not be validated. Please ensure that the feature class is projected to the Statewide Parcel CRS. This documentation may be of use in projecting the dataset: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf.")
			exit()

	#Check if text value is a valid number(Error object, Parcel object, field to test, type of error to classify this as, are <Null>s are considered errors?)
	def checkNumericTextValue(Error,Parcel,field,errorType,acceptNull): 
		try:
			stringToTest = getattr(Parcel,field)
			if stringToTest is not None:
				try:
					int(stringToTest)
				except ValueError:
					try:
						float(stringToTest)
					except ValueError:
						getattr(Parcel,errorType + "Errors").append("Value in " + field.upper() + " doesn't appear to be a numeric value.")
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
			if field == 'placename':
				if stringToTest is not None:
					if any(substring in stringToTest for substring in testList):
						pass
					else:
						getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " doesn't contain required LSAD descriptor.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					return (Error,Parcel)
			else:
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
					getattr(Parcel,errorType + "Errors").append(field.upper() + " is Null but " + siteAddField.upper() + " is populated.  Please ensure elements are in the appropriate field.")
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
			imprTest = getattr(Parcel,field)
			impValue = getattr(Parcel,impValField)
			if imprTest == None and impValue == None:
				pass
			elif (imprTest == None and impValue is not None) or (imprTest is not None and impValue is None):
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " doesn't correspond with 'IMPVALUE' for this record - please verify.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			elif (imprTest.upper() == 'NO' and float(impValue) <>  0):
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " doesn't correspond with 'IMPVALUE' for this record - please verify.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			elif (imprTest.upper() == 'YES' and float(impValue) <= 0):
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " doesn't correspond with 'IMPVALUE' for this record - please verify.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCounty") + 1)
			return (Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occured with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error,Parcel)

	#checking strings for unacceptable chars including /n, /r, etc...
	def badChars(Error,Parcel,fieldNamesList,charDict,errorType):
		try:
			for f in fieldNamesList:
				if f in charDict:
					testRegex = str(charDict[f]).replace(",",'').replace("'","").replace('"','').replace(" ","")
					stringToTest = str(getattr(Parcel,f.lower()))
					if stringToTest is not None:
						if re.search(testRegex,stringToTest) is not None:
							getattr(Parcel,errorType + "Errors").append("Bad characters found in " + f.upper())
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + f.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)
		
	#checking strings for unacceptable chars including /n, /r, etc...
	def reallyBadChars(Error,Parcel,fieldNamesList,charDict,errorType):
		arcpy.AddMessage("Testing reallyBadChars()")
		arcpy.AddMessage(str(getattr(Parcel,"ownernme1"))) # The most explicit way of accessing an attribute on parcel. We use the below example as a way of making the functions more flexible - with this strategy, they can test different character lists against different fields.
		arcpy.AddMessage(str(getattr(Parcel,fieldNamesList[7].lower()))) # externalDicts.py/fieldNames is passed as fieldNamesList for this function (ownername1 is in the 8th position)
		arcpy.AddMessage(str(Parcel.ownernme1)) # The another explicit way of accessing an attribute on parcel
		try:
			for f in fieldNamesList:
				#arcpy.AddMessage(str(getattr(Parcel,f.lower()))) # similar to the above, access the attribute value of the fieldname "f"
				if f in charDict:
					testRegex = str(charDict[f]).replace(",",'').replace("'","").replace('"','').replace(" ","")
					stringToTest = str(getattr(Parcel,f.lower()))
					if stringToTest is not None:
						if re.search(testRegex,stringToTest) is not None:
							getattr(Parcel,errorType + "Errors").append("Bad characters found in " + f.upper())
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + f.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking taxparcelID and parcelID for redundancy
	def checkRedundantID(Error,Parcel,taxField,parcelField,acceptNull,errorType):
		try:
			taxIDToTest = getattr(Parcel,taxField)
			parcelIDToTest = getattr(Parcel,parcelField)
			#check redundancy; if none, continue
			if taxIDToTest is None and parcelIDToTest is None:
				pass
			elif taxIDToTest == parcelIDToTest:
				getattr(Parcel, errorType + "Errors").append("Redundant information in " + taxField.upper() + " and " + parcelField.upper() + " fields.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			else:
				pass
			return (Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + taxField.upper() + "or" + parcelField.upper() + " fields. Please inspect these fields' values.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check for PROP/AUX value existing when expected and then check existing values for dups and for values not in expected domain lists...(Makes classOfPropCheck fcn obsolete)
	def auxPropCheck(Error,Parcel,propField,auxField,yearField,pinField,ignoreList,errorType,copDomainList,auxDomainList):
		try:
			year = getattr(Parcel,yearField)
			pinToTest = getattr(Parcel,pinField)
			copToTest = getattr(Parcel,propField)
			auxToTest = getattr(Parcel,auxField)
			testListCop = []
			testListAux = []
			if pinToTest in ignoreList or pinToTest is None:
				pass
			else:
				if year is not None and int(year) > 2017:
					pass
				if copToTest is None and auxToTest is None:
					getattr(Parcel,errorType + "Errors").append("Both the " + propField.upper() + " and " + auxField.upper() + " field are <Null> and a value is expected.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				if copToTest is not None:
					checkVal = copToTest.split(",")
					for val in checkVal:
						if val.strip() not in copDomainList:
							getattr(Parcel,errorType + "Errors").append("A value provided in " + propField.upper() + " field is not in acceptable domain list.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						elif val.strip() in testListCop:
							getattr(Parcel,errorType + "Errors").append("Duplicate values exist in " + propField.upper() + " field.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						else:
							testListCop.append(val.strip())
				if auxToTest is not None:
					checkAuxVal = auxToTest.split(",")
					for val in checkAuxVal:
						if val.strip() not in auxDomainList:
							getattr(Parcel,errorType + "Errors").append("A value provided in " + auxField.upper() + " field is not in acceptable domain list.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						elif val.strip() in testListAux:
							getattr(Parcel,errorType + "Errors").append("Duplicate values exist in " + auxField.upper() + " field.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						else:
							testListAux.append(val.strip())
			return(Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("!!!!!!An unknown issue occurred with the " + propField.upper() + " and/or " + auxField.upper() + " field. Please manually inspect these field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking ESTFMKVALUE field against PROPCLASS field for erroneous null values when PROPCLASS of 4 is present with another value
 	def fairMarketCheck(Error,Parcel,propClass,estFmkValue,errorType):
 		try:
			propClassTest = str(getattr(Parcel,propClass)).replace(" ","")
			estFmkValueTest = getattr(Parcel,estFmkValue)
			if estFmkValueTest is None:
				if re.search('4,', propClassTest) is not None:
					getattr(Parcel, errorType + "Errors").append("Unexpected information in " + estFmkValue.upper() + " field based off value in  " + propClass.upper() + " field.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				elif re.search(',4', propClassTest) is not None:
					getattr(Parcel, errorType + "Errors").append("Unexpected information in " + estFmkValue.upper() + " field based off value in  " + propClass.upper() + " field.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				else:
					pass
				return(Error,Parcel)

 		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + propClass.upper() + "or" + estFmkValue.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	# FUNCTION NO LONGER USED. checking propclass and auxclass for acceptable domains and duplicate values
	def classOfPropCheck(Error,Parcel,field,domainList,errorType,acceptNull):
		try:
			arcpy.AddMessage("hello")
			stringToTest = getattr(Parcel,field)
			testList = []
			if stringToTest is not None:
				checkVal = stringToTest.split(",")
				for val in checkVal:
					if field == 'propclass':
						if val.strip() not in domainList:
							getattr(Parcel,errorType + "Errors").append("A value provided in " + field.upper() + " field is not in acceptable domain list.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						elif val.strip() in testList:
							getattr(Parcel,errorType + "Errors").append("Duplicate values exist in " + field.upper() + " field.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						else:
							testList.append(val.strip())
					else:
						if val.strip() not in domainList:
							getattr(Parcel,errorType + "Errors").append("A value provided in " + field.upper() + " field is not in AUXCLASS domain list. Please ensure mappings for these values are provided in the 'Explain/Certification' box of submission form.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						elif val.strip() in testList:
							getattr(Parcel,errorType + "Errors").append("Duplicate values exist in " + field.upper() + " field.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						else:
							testList.append(val.strip())
				return(Error,Parcel)
			else:
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Null Found on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking CONAME, PARCELFIPS and PARCELSRC fields to ensure they match expected and meet domain requirements
	def matchContrib(Error,Parcel,coNamefield,fipsfield,srcfield,coNameDict,coNumberDict,errorType,acceptNull):
		try:
			coNameToTest = getattr(Parcel,coNamefield)
			fipsToTest = getattr(Parcel,fipsfield)
			srcToTest = getattr(Parcel,srcfield)
			if coNameToTest is not None:
				if coNameToTest != Error.coName:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + coNamefield.upper() + " field does not match expected county name.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			else:
				if acceptNull:
					pass
				else:
					Error.coNameMiss += 1
			if fipsToTest is not None:
				try: 
					if fipsToTest != coNameDict[Error.coName]:
						getattr(Parcel,errorType + "Errors").append("The value provided in " + fipsfield.upper() + " field does not match submitting county fips.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				except:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + srcfield.upper() + " field does not appear to meet required domains.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			else:
				if acceptNull:
					pass
				else:
					Error.fipsMiss += 1
			if srcToTest is not None:
				try:
					if srcToTest != coNumberDict[coNameDict[Error.coName]]:
						getattr(Parcel,errorType + "Errors").append("The value provided in " + srcfield.upper() + " field does not match submitting county name.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				except:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + fipsfield.upper() + " field does not appear to meet required domains.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			else:
				if acceptNull:
					pass
				else:
					Error.srcMiss += 1
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking values provided in SCHOOLDISTNO and SCHOOLDIST field to ensure they are in our domain list and represent the same school dist (if both provided)
	def schoolDistCheck(Error,Parcel,pinField,schDistField,schDistNoField,schNoNameDict,schNameNoDict,errorType,ignoreList):
		try:
			schNo = getattr(Parcel,schDistNoField)
			schNa = getattr(Parcel,schDistField)
			pinToTest = getattr(Parcel,pinField)
			if schNo is not None and schNa is not None:
				schNa = schNa.replace("SCHOOL DISTRICT", "").replace("SCHOOL DISTIRCT", "").replace("SCHOOL DIST","").replace("SCHOOL DIST.", "").replace("SCH DIST", "").replace("SCHOOL", "").replace("SCH D OF", "").replace("SCH", "").replace("SD", "").strip()
				try:
					if schNo != schNameNoDict[schNa] or schNa != schNoNameDict[schNo]:
						getattr(Parcel,errorType + "Errors").append("The values provided in " + schDistNoField.upper() + " and " + schDistField.upper() + " field do not match. Please verify values are in acceptable domain list.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				except:
					getattr(Parcel,errorType + "Errors").append("One or both of the values in the SCHOOLDISTNO field or SCHOOLDIST field are not in the acceptable domain list. Please verify values.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error,Parcel)
			if schNo is None and schNa is not None:
				schNa = schNa.replace("SCHOOL DISTRICT", "").replace("SCHOOL DISTIRCT", "").replace("SCHOOL DIST","").replace("SCHOOL DIST.", "").replace("SCH DIST", "").replace("SCHOOL", "").replace("SCH D OF", "").replace("SCH", "").replace("SD", "").strip()
				if schNa not in schNameNoDict:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + schDistField.upper() + " is not within the acceptable domain list. Please verify value.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			if schNa is None and schNo is not None:
				if schNo not in schNoNameDict or len(schNo) != 4:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + schDistNoField.upper() + " is not within the acceptable domain list or is not 4 digits long as expected. Please verify value.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			if schNo is None and schNa is None and pinToTest not in ignoreList:
				getattr(Parcel,errorType + "Errors").append("Both the " + schDistNoField.upper() + " &  the " + schDistField.upper() + " are <Null> and a value is expected.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + schDistField.upper() + " or " + schDistNoField.upper() + " field. Please manually inspect this field's value.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	def fieldCompleteness(Error,Parcel,fieldList,passList,v3Dict):
		for field in fieldList:
			if field.upper() in passList:
				pass
			else:
				stringToTest = getattr(Parcel,field.lower())
				if stringToTest is None:
					pass
				else:
					if stringToTest is not None or stringToTest != '':
						v3Dict[field] = v3Dict[field]+1
		return(Error,Parcel)


	def fieldCompletenessComparison(Error,Parcel,fieldList,passList,currentStatDict,previousStatDict):
		for field in fieldList:
			if field.upper() in passList:
				pass
			else:
				Error.comparisonDict[field] = currentStatDict[field] - previousStatDict[field]
		return(Error,Parcel)


	#checkSchemaFunction
	def checkSchema(Error,inFc,schemaType,fieldPassLst):
		fieldList = arcpy.ListFields(inFc)
		realFieldList = []
		fieldDictNames = {}
		incorrectFields = []
		excessFields = []
		missingFields = []
		var = True

		arcpy.AddMessage("Checking for all appropriate fields in " + str(inFc) + "...")

		for field in fieldList:
			fieldDictNames[field.name] = [[field.type],[field.length]]

		#if error fields already exits, delete them
		for field in fieldList:
			if field.name == 'GeneralElementErrors':
				arcpy.DeleteField_management(inFc, ['GeneralElementErrors','AddressElementErrors','TaxrollElementErrors','GeometricElementErrors'])

		for field in fieldDictNames:
			if field.upper() not in fieldPassLst:
				if field not in schemaType.keys():
					excessFields.append(field)
					var = False
				elif fieldDictNames[field][0][0] not in schemaType[field][0] or fieldDictNames[field][1][0] not in schemaType[field][1]:
					incorrectFields.append(field)
					var = False
				else:
					missingFields = [i for i in schemaType.keys() if i not in fieldDictNames.keys()]
					if len(missingFields) > 0:
						var = False

		if var == False:	
			arcpy.AddMessage("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			arcpy.AddMessage("   IMMEDIATE ERROR REQUIRING ATTENTION")
			arcpy.AddMessage("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			arcpy.AddMessage("A NUMBER OF FIELDS DO NOT MEET THE PARCEL OR ZONING SCHEMA REQUIREMENTS.\n")
			if len(incorrectFields) > 0:
				arcpy.AddMessage("THE PROBLEMATIC FIELDS INCLUDE: (" + str(incorrectFields).strip("[").strip("]").replace('u','') + ")\n")
				arcpy.AddMessage("------->> PLEASE CHECK TO MAKE SURE THE NAMES, DATA TYPES, AND LENGTHS MATCH THE SCHEMA REQUIREMENTS.\n")
			if len(excessFields) > 0:
				arcpy.AddMessage("THE EXCESS FIELDS INCLUDE: (" + str(excessFields).strip("[").strip("]").replace('u','') + ")\n")
				arcpy.AddMessage("------->> PLEASE REMOVED FIELDS THAT ARE NOT IN THE PARCEL ATTRIBUTE SCHEMA.\n")
			if len(missingFields) > 0:
				arcpy.AddMessage("THE MISSING FIELDS INCLUDE: (" + str(missingFields).strip("[").strip("]").replace('u','') + ")\n")
				arcpy.AddMessage("------->> PLEASE ADD FIELDS THAT ARE NOT IN THE PARCEL ATTRIBUTE SCHEMA.\n")
			arcpy.AddMessage("PLEASE MAKE NEEDED ALTERATIONS TO THESE FIELDS AND RUN THE TOOL AGAIN.\n")
			arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			exit()


	#check for valid postal address
	def postalCheck (Error,Parcel,PostalAd,errorType,ignoreList,taxYear,pinField):
		try:
			address = getattr(Parcel,PostalAd)
			year = getattr(Parcel, taxYear)
			pinToTest = getattr(Parcel,pinField)
			if address is None:
				pass
			else:
				if year is not None:
					if int(year) <= 2017:
						if 'UNAVAILABLE' in address or 'ADDRESS' in address or 'ADDDRESS' in address or 'UNKNOWN' in address or ' 00000' in address or 'PHASE' in address or 'NULL' in address or 'NONE' in address or 'MAIL EXEMPT' in address or 'TAX EX' in address or 'UNASSIGNED' in address or 'N/A' in address:
						#arcpy.AddMessage(address)
							getattr(Parcel,errorType + "Errors").append("A value provided in the " + PostalAd.upper() + " field may contain an incomplete address. Please verify the value is correct or set to <Null> if complete address is unknown.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						else:
							pass
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the PSTLADRESS field.  Please manually inspect this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)



	#check for instances of net > gross
	def netVsGross(Error,Parcel,netField,grsField,errorType):
		try:
			netIn = getattr(Parcel,netField)
			grsIn = getattr(Parcel,grsField)
			if netIn is not None and grsIn is not None:
				if float(grsIn) >= float(netIn):
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("The NETPRPTA value is greater than the GRSPRPTA value.  See Validation_and_Submission_Tool_Guide.pdf for further information.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					Error.netMoreGrsCnt += 1
				return (Error,Parcel)
			else:
				pass
			return (Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the NETPRPTA or GRSPRPTA field.  Please manually inspect the values in these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

