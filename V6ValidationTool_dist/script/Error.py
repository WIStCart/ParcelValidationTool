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
		#self.geometricPlacementErrors = ["Several parcel geometries appear to be spatially misplaced when comparing them against last year's parcel geometries. This issue is indicative of a re-projection error. Please see the following documentation: http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf section #2, for advice on how to project native data to the Statewide Parcel CRS."]
		self.geometricPlacementErrors = []
		self.pinSkipCount = 0
		self.trYearPast = 0
		self.trYearExpected = 0
		self.trYearFuture = 0
		self.trYearOther = 0
		self.coNameMiss = 0
		self.fipsMiss = 0
		self.srcMiss = 0
		self.netMoreGrsCnt = 0
		self.recordIterationCount = 0
		self.recordTotalCount = int(arcpy.GetCount_management(featureClass).getOutput(0)) # Total number of records in the feature class
		self.checkEnvelopeInterval = math.trunc(self.recordTotalCount / 100) # Interval value used to apply 10 total checks on records at evenly spaced intervals throughout the dataset.
		self.nextEnvelopeInterval = self.checkEnvelopeInterval
		self.notConfirmGeomCount = 0 #counts parcels with invalid Geometry
		self.validatedGeomCount = 0 #counts parcels whose geometry is validated
		self.geometryNotValidated = False
		self.geometryNotChecked = True
		self.diffxy = 0
		self.xyShift = 0
		self.codedDomainfields = []

	# Test records throughout the dataset to ensure that polygons exist within an actual county envelope ("Waukesha" issue or the "Lake Michigan" issue).
	def checkGeometricQuality(self,Parcel,ignoreList):
		#arcpy.AddMessage(self.nextEnvelopeInterval)
		#arcpy.AddMessage(self.recordIterationCount)
		if self.nextEnvelopeInterval == self.recordIterationCount:
			if str(Parcel.parcelid).upper() in ignoreList:
				self.nextEnvelopeInterval = self.nextEnvelopeInterval + 1
			else:
				countyEnvelope = self.testCountyEnvelope(Parcel)
				if countyEnvelope == "Valid" and self.validatedGeomCount == 50: # would mean that the "Waukesha" issue or the "Lake Michigan" issue does not exist in this dataset.
					self.nextEnvelopeInterval = 4000000
					if self.notConfirmGeomCount > 0:
						self.xyShift = round((self.diffxy/self.notConfirmGeomCount),2)
					arcpy.AddMessage("Parcel geometry validated.")
					self.geometricPlacementErrors = []
				elif countyEnvelope == "Not Confirmed" and self.notConfirmGeomCount == 50:
					self.nextEnvelopeInterval = 4000000
					self.xyShift = round((self.diffxy/self.notConfirmGeomCount),2)
					#arcpy.AddMessage("couldn't validate")
					if  self.xyShift >= 6:
						self.geometryNotValidated = True
					elif self.xyShift >= 1.2 and self.xyShift < 6:
						arcpy.AddMessage("\n ")
						arcpy.AddMessage("Parcel geometry validated, but several parcel geometries appear to be spatially misplaced by about: " + str(self.xyShift) + " meters. \n" )
						self.geometricPlacementErrors = ["Several parcel geometries appear to be spatially misplaced " + str(self.xyShift) + " meters when comparing them against parcel geometries from last year. This issue is indicative of a re-projection error. Please see the following documentation: http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf section #2, for advice on how to project native data to the Statewide Parcel CRS."]
					else:
						arcpy.AddMessage("\nParcel geometry validated.")
						self.geometricPlacementErrors = []
						#arcpy.AddMessage("Geometry validated -- but several parcels are misplaced: " + str(self.xyShift) + " meters.")
				self.nextEnvelopeInterval = self.nextEnvelopeInterval + self.checkEnvelopeInterval
		elif self.nextEnvelopeInterval < 4000000 and self.nextEnvelopeInterval >= (100 * self.checkEnvelopeInterval):
			if self.validatedGeomCount == 0 and self.notConfirmGeomCount == 0: #no parcel geometry was checked -- likely ParcelIds are different from previous years
				#arcpy.AddMessage("The PARCELID within the dataset may not match the PARCELID submitted the previous year. \n" )
				self.nextEnvelopeInterval = 4000000
				self.geometryNotChecked = False   # flag for county centroid check funcion
			elif self.notConfirmGeomCount  > 0:
				self.nextEnvelopeInterval = 4000000
				self.xyShift = round((self.diffxy/self.notConfirmGeomCount),2)
				arcpy.AddMessage("Several parcel geometries appear to be spatially misplaced by about: " + str(self.xyShift) + " meters." )
				self.geometricPlacementErrors = ["Several parcel geometries appear to be spatially misplaced " + str(self.xyShift) + " meters when comparing them against parcel geometries from last year. This issue is indicative of a re-projection error. Please see the following documentation: http://www.sco.wisc.edu/parcels/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf section #2, for advice on how to project native data to the Statewide Parcel CRS."]
		self,Parcel = self.testParcelGeometry(Parcel)
		self.recordIterationCount += 1
		return (self, Parcel)


	# Will test the row against LTSB's feature service to identify if the feature is in the correct location.
	def testCountyEnvelope(self,Parcel):
		specialchars = ['/', '#', '&']  #this special characters occurs in some ParcelIDs
		charsdict = {'&': '%26', '#': '%23', '/': '%2F'}
		parcelid =  str(Parcel.parcelid).upper()
		for i in specialchars:
			while parcelid is not None and i in parcelid:
				parcelid = parcelid[:parcelid.find(i)] + charsdict[i] + parcelid[parcelid.find(i)+1:]
		try:
			#baseURL = "http://mapservices.legis.wisconsin.gov/arcgis/rest/services/WLIP_V3/V3_Parcels/FeatureServer/0/query"
			baseURL = "http://mapservices.legis.wisconsin.gov/arcgis/rest/services/WLIP/Parcels/FeatureServer/0/query"
			where =  str(Parcel.parcelfips) + parcelid
			query = "?f=json&where=STATEID+%3D+%27{0}%27&geometry=true&returnGeometry=true&spatialRel=esriSpatialRelIntersects&outFields=OBJECTID%2CPARCELID%2CTAXPARCELID%2CCONAME%2CPARCELSRC&outSR=3071&resultOffset=0&resultRecordCount=10000".format(where)
			fsURL = baseURL + query
			#arcpy.AddMessage(fsURL)
			fs = arcpy.FeatureSet()
			fs.load(fsURL)
			#arcpy.AddMessage(where)
			with arcpy.da.UpdateCursor(fs,["SHAPE@XY"]) as cursorLTSB:
				for rowLTSB in cursorLTSB:
					v2x = round(rowLTSB[0][0],2)
					v1x = round(Parcel.shapeXY[0],2)
					v2y = round(rowLTSB[0][1],2)
					v1y = round(Parcel.shapeXY[1],2)
					diffx = v2x - v1x
					diffy = v2y - v1y
					if (v2x == v1x) and (v2y == v1y):
					#if (diffx == 0) and (diffy == 0):
						self.validatedGeomCount += 1
						if (self.validatedGeomCount % 10 == 0):
							arcpy.AddMessage("Checking parcel geometry ...")
						return "Valid"
					else:
						#arcpy.AddMessage("difference x :"  + str(diffx) + ' = ' + str(v2x) + " - " + str(v1x) )
						#arcpy.AddMessage("difference y :"  + str(diffy) + ' = ' + str(v2y) + " - " + str(v1y) )
						diffxy = round(math.sqrt (diffx*diffx + diffy*diffy),2)
						#arcpy.AddMessage("difference xy : %s"  % (str(diffxy)) )
						self.diffxy = self.diffxy + diffxy
						self.notConfirmGeomCount += 1
						if (self.notConfirmGeomCount % 10 == 0):
							arcpy.AddMessage("Parcel geometry not validated yet, will attempt another record.")
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
			Parcel.geometricErrors.append("Corrupt Geometry: The geometry of the feature class could not be accessed.")
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
			Parcel.geometricErrors.append("Corrupt Geometry: The area and/or length of the feature class could not be accessed.")
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
			arcpy.AddMessage("The coordinate reference system of the feature class could not be validated. Please ensure that the feature class is projected to the Statewide Parcel CRS. This documentation may be of use in projecting the dataset: http://www.sco.wisc.edu/images/stories/publications/V2/tools/FieldMapping/Parcel_Schema_Field_Mapping_Guide.pdf.")
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
						getattr(Parcel,errorType + "Errors").append("Value in " + field.upper() + " does not appear to be a numeric value.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
			else:
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("<Null> Found on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the" + field.upper() + "field. Please inspect the value of this field.")
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
					getattr(Parcel,errorType + "Errors").append("<Null> Found on " + field.upper())
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please inspect the value of this field.")
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
						getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not contain required LSAD descriptor.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					return (Error,Parcel)

			elif field == 'unitid' or field == 'unittype':
				if (stringToTest is None) or (stringToTest in testList):
					#arcpy.AddMessage("This value is <Null>... or exists in our list...")
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("The value in " + field.upper() + " is not in standardized domain list. Please standarize/spell out values for affected records.")
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
						getattr(Parcel,errorType + "Errors").append("<Null> Found on " + field.upper())
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
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
					if pinToTest in ignoreList or pinToTest is None:
						Error.pinSkipCount += 1
					else:
						getattr(Parcel,errorType + "Errors").append("Value in " + field.upper() + " is flagged. See schema definition. In most cases; value should be expected year (" + acceptYears[1] + "); or future year (" + acceptYears[2] + ") if new parcel/split.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

		#Verify that all tall roll data is <Null> when the record represent a New Parcel (indicated by a future tax roll year)
	def taxrollYrCheck(Error,Parcel,field,errorType,acceptNull,pinField,acceptYears):
		try:
			taxRollYear = getattr(Parcel,field)
			taxRollFields = {'IMPVALUE': getattr(Parcel, "impvalue"), 'CNTASSDVALUE': getattr(Parcel, "cntassdvalue"),
			'LNDVALUE': getattr(Parcel, "lndvalue"), 'MFLVALUE': getattr(Parcel, "mflvalue"), 'ESTFMKVALUE': getattr(Parcel, "estfmkvalue"),
			'NETPRPTA': getattr(Parcel, "netprpta"), 'GRSPRPTA': getattr(Parcel, "grsprpta"),
			'PROPCLASS': getattr(Parcel, "propclass"), 'AUXCLASS': getattr(Parcel, "auxclass")}
			probFields = []
			if taxRollYear is not None:
				if taxRollYear == acceptYears[2] or taxRollYear == acceptYears[3]:
					for key, val in taxRollFields.iteritems():
						if val is not None:
							probFields.append(key)
					if len(probFields) > 0:
						getattr(Parcel,errorType + "Errors").append("Future Year (" + str(taxRollYear) + ") found and " + " / ".join(probFields) + " field(s) is/are not <Null>. A <Null> value is expected in all tax roll data for records annotated with future tax roll years. Please correct.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				else:  #other years are okay
					pass
				return (Error, Parcel)
			elif acceptNull:  # it is null -> TAXROLLYEAR for parcel splits/new parcels may be <Null>
				pass
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check to see if street name provided is within a list created from V2.
	def streetNameCheck(Error,Parcel,field,siteAddField,errorType,acceptNull,stNameDict,coname):
		try:
			#county = coname
			stringToTest = getattr(Parcel,field)
			siteAddToTest = getattr(Parcel,siteAddField)
			if stringToTest is not None:
				if stringToTest.strip() in stNameDict[coname]:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not appear in list created from data of last year. Please verify this value contains only the STREETNAME and street name is correct.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return(Error, Parcel)
			else:
				if siteAddToTest is not None and stringToTest is None:
					getattr(Parcel,errorType + "Errors").append(field.upper() + " is <Null> but " + siteAddField.upper() + " is populated. Please ensure elements are in the appropriate field.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return(Error, Parcel)
				if acceptNull:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("<Null> Found on " + field.upper() + " field and value is expected.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
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
					getattr(Parcel,errorType + "Errors").append("<Null> Found on " + field.upper() + " field and value is expected.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#verify that the values provided in the zip4 field is 4 characters long
	def zip4Check(Error,Parcel,field,errorType,acceptNull):
		try:
			stringToTest = getattr(Parcel, field)
			if stringToTest is not None:
				if len(stringToTest) == 4:
					pass
				else:
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " is not 4 digits long.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error, Parcel)
			elif acceptNull:
				pass
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return(Error, Parcel)



	#Verify that value in Improved field is correct based on value provided in Impvalue field...
	#We may want/need to tweak the logic in here depending on how strictly we enforce the value of <Null> allowed in Impvalue field (i.e. Only for non-tax parcels or allow either 0 or <Null>)
	def impCheck(Error,Parcel,field,impValField,errorType):
		try:
			imprTest = getattr(Parcel,field)
			impValue = getattr(Parcel,impValField)
			if imprTest == None and impValue == None:
				pass
			elif (imprTest == None and impValue is not None) or (imprTest is not None and impValue is None):
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not correspond with 'IMPVALUE' for this record - please verify.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			elif (imprTest.upper() == 'NO' and float(impValue) <> 0):
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not correspond with 'IMPVALUE' for this record - please verify.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			elif (imprTest.upper() == 'YES' and float(impValue) <= 0):
				getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " does not correspond with 'IMPVALUE' for this record - please verify.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCounty") + 1)
			return (Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occured with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error,Parcel)

	#Verify that CNTASSDVALUE is different to LandValue when ImpValue is greater than zero
	def totCheck (Error,Parcel,field,cntassValue,landValue,errorType):
		try:
			impvalue = getattr(Parcel, field)
			cntassvalue = getattr(Parcel, cntassValue)
			lndvalue =  getattr(Parcel, landValue)
			if impvalue is None and cntassvalue is None and lndvalue is None:
				pass
			elif  (impvalue  is None or float(impvalue) == 0):
				if (cntassvalue is not None and lndvalue is not None) and (float(cntassvalue) == float(lndvalue)):
					#arcpy.AddMessage(impvalue)
					pass
				elif (cntassvalue is not None and lndvalue is not None) and (float(cntassvalue) <> float(lndvalue)):
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " is zero or <Null>. 'CNTASSDVALUE' should be equal to 'LNDVALUE' for this record - please verify.")
					Error.taxErrorCount += 1
			elif (impvalue is not None and float(impvalue) > 0):
				if (cntassvalue is not None and lndvalue is not None) and (float(cntassvalue) > float(lndvalue)) :
					pass
				elif (cntassvalue is not None and lndvalue is not None) and (float(cntassvalue) == float(lndvalue)):
					getattr(Parcel,errorType + "Errors").append("Value provided in " + field.upper() + " is greater than zero. 'CNTASSDVALUE' should not be equal to 'LNDVALUE' for this record - please verify.")
					Error.taxErrorCount += 1
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return(Error,Parcel)



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
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + f.upper() + " field. Please manually inspect the value of this field.")
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
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + f.upper() + " field. Please manually inspect the value of this field.")
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
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + taxField.upper() + "or" + parcelField.upper() + " fields. Please inspect the values of these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check for PROP/AUX value existing when expected and then check existing values for dups and for values not in expected domain lists...(Makes classOfPropCheck fcn obsolete)
	def auxPropCheck(Error,Parcel,propField,auxField,yearField,pinField,ignoreList,errorType,copDomainList,auxDomainList, acceptYears):
		try:
			year = getattr(Parcel,yearField)
			pinToTest = getattr(Parcel,pinField)
			copToTest = getattr(Parcel,propField)
			auxToTest = getattr(Parcel,auxField)
			testListCop = []
			testListAux = []
			if (pinToTest in ignoreList) or (pinToTest is None) or (year is not None and int(year) > int(acceptYears[1])):   #
				pass
			else:
				if copToTest is None and auxToTest is None:
					#arcpy.AddMessage( str(year) + " and " + str(acceptYears[1]) )
					getattr(Parcel,errorType + "Errors").append("The " + propField.upper() + " and " + auxField.upper() + " fields are <Null> and a value is expected for any non-new parcels.")
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
							getattr(Parcel,errorType + "Errors").append("A value provided in " + auxField.upper() + " field is not in AUXCLASS domain list. Standardize values for AUXCLASS domains.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						elif val.strip() in testListAux:
							getattr(Parcel,errorType + "Errors").append("Duplicate values exist in " + auxField.upper() + " field.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
						else:
							testListAux.append(val.strip())
			return(Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("!!!!!!An unknown issue occurred with the " + propField.upper() + " and/or " + auxField.upper() + " field. Please manually inspect the values of these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking ESTFMKVALUE field against PROPCLASS field for erroneous not null values when PROPCLASS of 4, 5, 5M or AUXCLASS field
	# for erroneous not null values when AUXCLASS of x1-x4 or w1-w9 is present with another value
 	def fairMarketCheck(Error,Parcel,propClass,auxClass,estFmkValue,errorType):
 		try:
			propClassTest = str(getattr(Parcel,propClass)).replace(" ","")
			auxClassTest = str(getattr(Parcel,auxClass)).replace(" ","")
			estFmkValueTest = getattr(Parcel,estFmkValue)
			if estFmkValueTest is not None:
				if re.search('4', propClassTest) is not None or re.search('5', propClassTest) is not None:
					getattr(Parcel, errorType + "Errors").append("A <Null> value is expected in " + estFmkValue.upper() + " for properties with PROPCLASS values of 4, 5 and 5M. Correct or verify.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				#elif re.search('W', auxClassTest) is not None or re.search('X', auxClassTest) is not None:
				#	getattr(Parcel, errorType + "Errors").append("A <Null> value is expected in " + estFmkValue.upper() + " field according to value(s) in " + auxClass.upper() + " field.")
				#	setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				else:
					pass
				return(Error,Parcel)

 		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + propClass.upper() + "or" + estFmkValue.upper() + " field. Please manually inspect the values of these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking CONAME, PARCELFIPS and PARCELSRC fields to ensure they match expected and meet domain requirements
	def matchContrib(Error,Parcel,coNamefield,fipsfield,srcfield,coNameDict,coNumberDict,acceptNull,errorType ):
		nullList = ["<Null>", "<NULL>", "NULL", ""]
		try:
			coNameToTest = getattr(Parcel,coNamefield)
			fipsToTest = getattr(Parcel,fipsfield)
			srcToTest = getattr(Parcel,srcfield)
			if coNameToTest is not None:
				if coNameToTest != Error.coName:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + coNamefield.upper() + " field does not match expected county name.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					#Error.coNameMiss += 1
				elif coNameToTest in nullList or coNameToTest.isspace():
					getattr(Parcel,errorType + "Errors").append("The value provided in " + coNamefield.upper() + " field does not match expected county name.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					Error.coNameMiss += 1
			else:
				if acceptNull:
					pass
				else:
					Error.coNameMiss += 1
			if fipsToTest is not None:
				if fipsToTest.upper() != coNameDict[Error.coName]:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + fipsfield.upper() + " field does not match submitting county fips.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					#Error.fipsMiss += 1
				elif fipsToTest in nullList or fipsToTest.find(' ') >= 0:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + fipsfield.upper() + " field does not appear to meet required domains.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					Error.fipsMiss += 1
			else:
				if acceptNull:
					pass
				else:
					Error.fipsMiss += 1
			if srcToTest is not None:
				if srcToTest.upper() != coNumberDict[coNameDict[Error.coName]]:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + srcfield.upper() + " field does not match submitting county name.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					#Error.srcMiss += 1
				elif srcToTest in nullList or srcToTest.isspace():
					getattr(Parcel,errorType + "Errors").append("The value provided in " + srcfield.upper() + " field does not appear to meet required domains.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					Error.srcMiss += 1
			else:
				if acceptNull:
					pass
				else:
					Error.srcMiss += 1
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#checking values provided in SCHOOLDISTNO and SCHOOLDIST field to ensure they are in our domain list and represent the same school dist (if both provided)
	def schoolDistCheck(Error,Parcel,pinField,schDistField,schDistNoField,schNoNameDict,schNameNoDict,errorType,ignoreList,yearField):
		try:
			schNo = getattr(Parcel,schDistNoField)
			schNa = getattr(Parcel,schDistField)
			pinToTest = getattr(Parcel,pinField)
			year = getattr(Parcel,yearField)
			if schNo is not None and schNa is not None:
				'''schNa = schNa.replace("SCHOOL DISTRICT", "").replace("SCHOOL DISTIRCT", "").replace("SCHOOL DIST","").replace("SCHOOL DIST.", "").replace("SCH DIST", "").replace("SCHOOL", "").replace("SCH D OF", "").replace("SCH", "").replace("SD", "").strip()'''
				try:
					if schNo != schNameNoDict[schNa] or schNa != schNoNameDict[schNo]:
						getattr(Parcel,errorType + "Errors").append("The values provided in " + schDistNoField.upper() + " and " + schDistField.upper() + " field do not match. Please verify values are in acceptable domain list.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				except:
					getattr(Parcel,errorType + "Errors").append("One or both of the values in the SCHOOLDISTNO field or SCHOOLDIST field are not in the acceptable domain list. Please verify values.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				return (Error,Parcel)
			if schNo is None and schNa is not None:
				'''schNa = schNa.replace("SCHOOL DISTRICT", "").replace("SCHOOL DISTIRCT", "").replace("SCHOOL DIST","").replace("SCHOOL DIST.", "").replace("SCH DIST", "").replace("SCHOOL", "").replace("SCH D OF", "").replace("SCH", "").replace("SD", "").strip()'''
				if schNa not in schNameNoDict:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + schDistField.upper() + " is not within the acceptable domain list. Please verify value.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			if schNa is None and schNo is not None:
				if schNo not in schNoNameDict or len(schNo) != 4:
					getattr(Parcel,errorType + "Errors").append("The value provided in " + schDistNoField.upper() + " is not within the acceptable domain list or is not 4 digits long as expected. Please verify value.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			if schNo is None and schNa is None and pinToTest not in ignoreList and pinToTest is not None and (year is not None and int(year) <= 2018):
				getattr(Parcel,errorType + "Errors").append("Both the " + schDistNoField.upper() + " &  the " + schDistField.upper() + " are <Null> and a value is expected.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return (Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + schDistField.upper() + " or " + schDistNoField.upper() + " field. Please manually inspect the values of these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	def fieldCompleteness(Error,Parcel,fieldList,passList,CompDict):
		for field in fieldList:
			if field.upper() in passList:
				pass
			else:
				stringToTest = getattr(Parcel,field.lower())
				if stringToTest is None:
					pass
				else:
					if stringToTest is not None or stringToTest != '':
						CompDict[field] = CompDict[field]+1
		return(Error,Parcel)


	def fieldCompletenessComparison(Error,fieldList,passList,currentStatDict,previousStatDict):
		for field in fieldList:
			if field.upper() in passList:
				pass
			else:
				#Error.comparisonDict[field] = currentStatDict[field] - previousStatDict[field]
				Error.comparisonDict[field] = round((100*(currentStatDict[field] - previousStatDict[field])/(Error.recordTotalCount)),2)
		return(Error)


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
			arcpy.AddMessage("CERTAIN FIELDS DO NOT MEET THE PARCEL SCHEMA REQUIREMENTS.\n")
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
	# Error.postalCheck(totError,currParcel,'pstladress','general',pinSkips,'taxrollyear','parcelid',badPstladdSet)
	def postalCheck (Error,Parcel,PostalAd,errorType,ignoreList,taxYear,pinField,badPstladdSet, acceptYears):
		try:
			address = getattr(Parcel,PostalAd)
			year = getattr(Parcel, taxYear)
			pinToTest = getattr(Parcel,pinField)
			if address is None:
				pass
			else:
				if year is not None:
					if int(year) <= int(acceptYears[1]):   #or pinToTest in ignorelist:
						if ('UNAVAILABLE' in address or 'ADDRESS' in address or 'ADDDRESS' in address or 'UNKNOWN' in address or ' 00000' in address or 'NULL' in address or ('NONE' in address and 'HONONEGAH' not in address) or 'MAIL EXEMPT' in address or 'TAX EX' in address or 'UNASSIGNED' in address or 'N/A' in address) or(address in badPstladdSet) :
							getattr(Parcel,errorType + "Errors").append("A value provided in the " + PostalAd.upper() + " field may contain an incomplete address. Please verify the value is correct or set to <Null> if complete address is unknown.")
							setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
							#arcpy.AddMessage(address)
						else:
							pass
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the PSTLADRESS field.  Please manually inspect this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)


	def totalAssdValueCheck(Error,Parcel,cnt,lnd,imp,errorType):
		try:
			cnt = 0.0 if (getattr(Parcel,cnt) is None) else float(getattr(Parcel,cnt))
			lnd = 0.0 if (getattr(Parcel,lnd) is None) else float(getattr(Parcel,lnd))
			imp = 0.0 if (getattr(Parcel,imp) is None) else float(getattr(Parcel,imp))
			if lnd + imp <> cnt:
				getattr(Parcel,errorType + "Errors").append("CNTASSDVALUE is not equal to LNDVALUE + IMPVALUE as expected.  Correct this issue and refer to the submission documentation for futher clarification as needed.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred when comparing your CNTASSDVALUE value to the sum of LNDVALUE and IMPVALUE.  Please manually inspect these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	# parcels with MFLValue should have auxclass of W1-W3 or W5-W9
	def mfLValueCheck(Error, Parcel, mflvalue, auxField, errorType):
		try:
			mflValueTest = getattr(Parcel,mflvalue)
			auxToTest = getattr(Parcel,auxField)

			if mflValueTest is None or float(mflValueTest) == 0.0:
			 	if auxToTest is not None and re.search('W', auxToTest) is not None and re.search('AW', auxToTest) is  None and re.search('W4', auxToTest) is  None:
					getattr(Parcel, errorType + "Errors").append("A <null> value provided in MFLVALUE field does not match the (" + str(auxToTest) + ") AUXCLASS value(s). Refer to submission documentation for verification.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			elif mflValueTest is not None and float(mflValueTest) > 0.0:
				if auxToTest is None:
					getattr(Parcel, errorType + "Errors").append("A <Null> value is expected in the MFLVALUE field according to the AUXCLASS field. Please verify.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				elif re.search('W4', auxToTest) is not None:
					getattr(Parcel, errorType + "Errors").append("MFLVALUE does not include properties with AUXCLASS value of W4. Please verify.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			else:
				pass
			return(Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the MFLVALUE field.  Please manually inspect these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	def mflLndValueCheck(Error,Parcel,lnd,mfl,errorType):
		try:
			lnd = 0.0 if (getattr(Parcel,lnd) is None) else float(getattr(Parcel,lnd))
			mfl = 0.0 if (getattr(Parcel,mfl) is None) else float(getattr(Parcel,mfl))
			if lnd == mfl and (lnd <> 0.0 and mfl <> 0.0):
				getattr(Parcel,errorType + "Errors").append("MFLVALUE should not equal LNDVALUE in most cases.  Please correct this issue and refer to the submission documentation for further clarification as needed.")
				setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
			return(Error,Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the MFLVALUE/LNDVALUE field.  Please manually inspect these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)


	# checks that parcels with auxclass x1-x4  have taxroll values = <null>
	def auxclassTaxrollCheck (Error,Parcel,auxclassField,errorType):
		try:
			auxclass = getattr(Parcel,auxclassField)
			taxRollFields = {'IMPVALUE': getattr(Parcel, "impvalue"), 'CNTASSDVALUE': getattr(Parcel, "cntassdvalue"),
			'LNDVALUE': getattr(Parcel, "lndvalue"), 'MFLVALUE': getattr(Parcel, "mflvalue"),
			'ESTFMKVALUE': getattr(Parcel, "estfmkvalue"),
			'NETPRPTA': getattr(Parcel, "netprpta"), 'GRSPRPTA': getattr(Parcel, "grsprpta")}

			probFields = []
			if auxclass is not None:
				if re.search('X', auxclass) is not None:
					for key, val in taxRollFields.iteritems():
						if val is not None:
							probFields.append(key)
					if len(probFields) > 0:
						getattr(Parcel,errorType + "Errors").append("AUXCLASS (" + str(auxclass) + ") found and " + " / ".join(probFields) + " field(s) is/are not <Null>. A <Null> value is expected in the field(s) for tax exempt parcels. Please correct.")
						setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				else:  #W values are okay
					pass
				return (Error, Parcel)

		except: # using generic error handling because we don't know what errors to expect yet.
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the " + field.upper() + " field. Please manually inspect the value of this field.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	#Check that parcels with propclass values of 1-7 have CNTASSDVALUE > 0
	def propClassCntCheck(Error,Parcel,propClass,cntValue,errorType):
		try:
			cnt = getattr(Parcel,cntValue)
			propClassTest = getattr(Parcel,propClass)
			if cnt is None or float(cnt) == 0:
				if propClassTest in ['1', '2', '3', '4', '5', '5M', '6', '7' ]:
					getattr(Parcel, errorType + "Errors").append("A value greater than zero is expected in CNTASSDVALUE for properties with PROPCLASS of (" + str(propClassTest) + "). Verify value.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
				else:
					pass
			elif cnt is not None and float(cnt) > 0:
				if propClassTest is None:
					getattr(Parcel, errorType + "Errors").append("The value provided in CNTASSDVALUE does not correspond with PROPCLASS value(s) of (" + str(propClassTest) + "). Please verify.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the CNTASSDVALUE field.  Please manually inspect the <Null> value provided in PROPCLASS.")
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
					getattr(Parcel,errorType + "Errors").append("The NETPRPTA value is greater than the GRSPRPTA value.  See Validation_and_Submission_Tool_Guide.pdf for verification.")
					setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
					Error.netMoreGrsCnt += 1
				return (Error,Parcel)
			else:
				pass
			return (Error, Parcel)
		except:
			getattr(Parcel,errorType + "Errors").append("An unknown issue occurred with the NETPRPTA or GRSPRPTA field.  Please manually inspect the values of these fields.")
			setattr(Error,errorType + "ErrorCount", getattr(Error,errorType + "ErrorCount") + 1)
		return (Error, Parcel)

	def checkCodedDomains(Error,featureClass):
		subtypes = arcpy.da.ListSubtypes(featureClass)
		for stcode, stdict in list(subtypes.items()):
			for stkey in list(stdict.keys()):
				if stkey == 'FieldValues':
					fields = stdict[stkey]
					for field, fieldvals in list(fields.items()):
						if fieldvals[1] is not None:
							Error.codedDomainfields.append(field)
		return Error

	#backup geom check function for 100 no parcelid matches...
	def ctyExtentCentCheck(self, infc, centroidDict):
		coname = self.coName
		describeFc = arcpy.Describe(infc)
		xMin = describeFc.extent.XMin
		xMax = describeFc.extent.XMax
		yMin = describeFc.extent.YMin
		yMax = describeFc.extent.YMax

		iNxMid = xMin + ((xMax - xMin)/2)
		iNyMid = yMin + ((yMax - yMin)/2)

		if (centroidDict[coname][0] - 100) <= round(iNxMid,0) <= (centroidDict[coname][0] + 100) and (centroidDict[coname][1] - 100) <= round(iNyMid,0) <= (centroidDict[coname][1] + 100):
			pass
		else:
			arcpy.AddMessage("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			arcpy.AddMessage("THE GEOMETRY OF THIS FEATURE CLASS WAS NOT VALIDATED.  \n")
			arcpy.AddMessage("THIS ISSUE CAN BE INDICATIVE OF A RE-PROJECTION ERROR. \n ")
			arcpy.AddMessage("REMINDER: YOUR DATA SHOULD BE RE-PROJECTED TO NAD_1983_HARN_Wisconsin_TM (Meters) PRIOR TO LOADING DATA INTO THE TEMPLATE FEATURE CLASS.\n")
			arcpy.AddMessage("PLEASE MAKE NEEDED ALTERATIONS TO THE FEATURE CLASS AND RUN THE TOOL AGAIN.\n")
			arcpy.AddMessage("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
			exit()
