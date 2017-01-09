import arcpy
from Parcel import Parcel
from Error import Error
from Summary import Summary
import os
import re
import csv

#Tool inputs
in_fc = arcpy.GetParameterAsText(0)  #input feature class
outDir = arcpy.GetParameterAsText(1)  #output directory location
outName = arcpy.GetParameterAsText(2)  #output feature class name
outDirTxt = arcpy.GetParameterAsText(3)  #output directory error summary .txt file

#Run Original checks
totError = Error(in_fc)

#reading in csv of StreetNames
streetNames = [line.strip() for line in open('C:\WorkSpace\V3_Working\V3ValidationTool\V2_StreetName_Simplified.txt', 'r')]

#list of field names 
fieldNames = ["OID@","SHAPE@","STATEID","PARCELID","TAXPARCELID","PARCELDATE","TAXROLLYEAR",
"OWNERNME1","OWNERNME2","PSTLADRESS","SITEADRESS","ADDNUMPREFIX","ADDNUM","ADDNUMSUFFIX","PREFIX","STREETNAME",
"STREETTYPE","SUFFIX","LANDMARKNAME","UNITTYPE","UNITID","PLACENAME","ZIPCODE","ZIP4","STATE","SCHOOLDIST",
"SCHOOLDISTNO","IMPROVED","CNTASSDVALUE","LNDVALUE","IMPVALUE","FORESTVALUE","ESTFMKVALUE","NETPRPTA","GRSPRPTA",
"PROPCLASS","AUXCLASS","ASSDACRES","DEEDACRES","GISACRES","CONAME","LOADDATE","PARCELFIPS","PARCELSRC",
"SHAPE@LENGTH","SHAPE@AREA","SHAPE@XY","GeneralElementErrors","AddressElementErrors","TaxrollElementErrors","GeometricElementErrors"]

#bad characters dictionary
fieldNamesBadChars = {
"PARCELID": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")"],
"TAXPARCELID": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")"],
"PARCELDATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\-"],
"TAXROLLYEAR": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',"\-"],
"OWNERNME1": ["\n","\r"],
"OWNERNME2": ["\n","\r"],
"PSTLADRESS": ["\n","\r"],
"SITEADRESS": ["\n","\r"],
"ADDNUMPREFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ADDNUM": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ADDNUMSUFFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"PREFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"STREETNAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","!","*","~","(",")"],
"STREETTYPE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"SUFFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"LANDMARKNAME": ["\n","\r"],
"UNITTYPE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"UNITID": ["\n","\r","$","^","=","<",">","@","%","&","?","`","!","*","~","(",")","\\",'/',','],
"PLACENAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ZIPCODE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ZIP4": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"STATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"SCHOOLDIST": ["\n","\r","$","^","=","<",">","@","#","%","&","?","!","*","~","(",")","\\",'/',','],
"SCHOOLDISTNO": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"IMPROVED": ["\n","\r","$","^","=","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"CNTASSDVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"LNDVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"IMPVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"FORESTVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"ESTFMKVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"NETPRPTA": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"GRSPRPTA": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"PROPCLASS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/','.',"\-"],
"AUXCLASS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/','.',"\-"],
"ASSDACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"DEEDACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"GISACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"CONAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"LOADDATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")",',','.','\-'],
"PARCELFIPS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"PARCELSRC": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"]
}

#list of non-parcelid values found in field to ignore when checking for dups
pinSkips = ["ALLEY","CANAL","CE","CONDO","CREEK","CTH","CTH C","CTH G","CTH H","CTH H","GAP","HYDRO","LAKE","LCE","MARSH",
"MOUND","NIR","NOPID","OL","OTHER","OUT","PARK","PIER","POND","PVT","RIVER","ROAD","ROW","RR","RVR","RW","STATE","STH","TBD",
"TOA","TOB","TOF","TOJ","TOL","TOM","TOWN","TRAIL","TRIBE","UNK","USH","WALK","WATER","WELL","WET","WPS","WVIC"]

#testing prefix domain list
prefixDomains = ["CTH", "STH", "USH", "W CTH", "S CTH", "E CTH", "N CTH", "W STH", "S STH", "E STH", "N STH", "W USH", "S USH", "E USH", "N USH", "N", "E", "S", "W"]

#testing suffix domain list
suffixDomains = ["N", "E", "S", "W"]

#taxroll years to test (past,expected,future1,future2)
taxRollYears = ['2015','2016','2017','2018']

#acceptable COP domains
copDomains = ['1','2','3','4','5','6','7','5M']

#acceptable AUXCOP domains
auxDomins = ['W1','W2','W3','W4','W5','W6','W7','W8','X1','X2','X3','X4']



#lists for collecting parcelids and taxparcelids for checking for dups
uniquePinList = []
uniqueTaxparList = []

#Copy feature class, add new fields for error reporting
arcpy.AddMessage("Writing to Memory")
output_fc_temp = os.path.join("in_memory", "WORKING")
arcpy.AddMessage(output_fc_temp)
arcpy.Delete_management("in_memory")
dynamic_workspace = "in_memory"
arcpy.FeatureClassToFeatureClass_conversion(in_fc,dynamic_workspace, "WORKING")

#Adding new fields for error reporting.  We can change names, lenght, etc...
arcpy.AddMessage("Adding Error Fields")
arcpy.AddField_management(output_fc_temp,"GeneralElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"AddressElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"TaxrollElementErrors", "TEXT", "", "", 1000)
arcpy.AddField_management(output_fc_temp,"GeometricElementErrors", "TEXT", "", "", 1000)

#Call all pre-cursor test functions
totError = Error.checkCRS(totError, output_fc_temp)

#Create update cursor then use it to iterate through records in feature class
arcpy.AddMessage("Testing the data for various attribute error types.")
with arcpy.da.UpdateCursor(output_fc_temp, fieldNames) as cursor:	
	for row in cursor:
		#Construct the Parcel object for the row
		currParcel = Parcel(row, fieldNames)
		#Execute in-cursor error tests
		totError,currParcel = Error.checkGeometricQuality(totError,currParcel)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"addnum","address", True) 
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"parcelfips","general", False)
		#totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"taxrollyear","tax", False)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"zipcode","address", True)
		totError,currParcel = Error.checkNumericTextValue(totError,currParcel,"zip4","address", True)
		totError,currParcel = Error.checkIsDuplicate(totError,currParcel,"parcelid","general", True, pinSkips, uniquePinList)
		totError,currParcel = Error.checkIsDuplicate(totError,currParcel,"taxparcelid","general", True, pinSkips, uniqueTaxparList)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"prefix","address",True, prefixDomains)
		totError,currParcel = Error.checkDomainString(totError,currParcel,"suffix","address",True, suffixDomains)
		totError,currParcel = Error.trYear(totError,currParcel,"taxrollyear","parcelid","tax",False,pinSkips,taxRollYears)
		totError,currParcel = Error.streetNameCheck(totError,currParcel,"streetname","siteadd","address",True,streetNames)
		totError,currParcel = Error.zipCheck(totError,currParcel,"zipcode","address",True)
		totError,currParcel = Error.impCheck(totError,currParcel,"improved","impvalue","tax")
		totError,currParcel = Error.badChars(totError,currParcel,fieldNames,fieldNamesBadChars,'general')
		totError,currParcel = Error.classOfPropCheck(totError,currParcel,'propclass',copDomains,'tax',True)
		totError,currParcel = Error.classOfPropCheck(totError,currParcel,'auxclass',auxDomins,'tax',True)
		#End of loop, finalize errors with the writeErrors function, then clear parcel
		currParcel.writeErrors(row,cursor, fieldNames)
		currParcel = None

# Write all summary-type errors to file via the Summary class
summaryTxt = Summary()
Summary.writeSummaryTxt(summaryTxt,outDirTxt,outName,totError)

# User messages (for testing):
arcpy.AddMessage("General Errors: " + str(totError.generalErrorCount))
arcpy.AddMessage("Geometric Errors: " + str(totError.geometricErrorCount))
arcpy.AddMessage("Address Errors: " + str(totError.addressErrorCount))
arcpy.AddMessage("Tax Errors: " + str(totError.taxErrorCount))

#Write feature class from memory back out to hard disk
arcpy.FeatureClassToFeatureClass_conversion(output_fc_temp,outDir,outName)
