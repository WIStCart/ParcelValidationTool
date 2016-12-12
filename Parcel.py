import arcpy
#TODO:
# 1) change the structure of the row to be fieldNames index (e.g. fieldNames.index("GeneralElementErrors")])
# 2) ...

#Parcel class defines a parcel record based on the attribute schema
class Parcel:
	#Class vars go here

	#Initialize a parcel object
	def __init__(self,row,fieldNames):
		self.objectid = row[0]
		self.shape = row[1]
		self.stateid = row[2]
		self.parcelid = row[3]
		self.taxparcelid = row[4]
		self.parceldate = row[5]
		self.taxrollyear = row[6]
		self.ownername1 = row[7]
		self.ownername2 = row[8]
		self.mailadd = row[9]
		self.siteadd = row[10]
		self.addnumprefix = row[11]
		self.addnum = row[fieldNames.index("ADDNUM")]
		self.addnumsuffix = row[13]
		self.prefix = row[14]
		self.streetname = row[15]
		self.streettype = row[16]
		self.suffix = row[17]
		self.landmarkname = row[18]
		self.unittype = row[19]
		self.unitid = row[20]
		self.placename = row[21]
		self.zipcode = row[22]
		self.zip4 = row[23]
		self.state = row[24]
		self.schooldist = row[25]
		self.schooldistno = row[26]
		self.improved = row[27]
		self.cntassdvalue = row[28]
		self.lndvalue = row[29]
		self.impvalue = row[30]
		self.forestvalue = row[31]
		self.estfmkvalue = row[32]
		self.netprpta = row[33]
		self.grsprpta = row[34]
		self.propclass = row[35]
		self.auxclass = row[36]
		self.assdacres = row[37]
		self.deedacres = row[38]
		self.gisacres = row[39]
		self.coname = row[40]
		self.loaddate = row[41]
		self.parcelfips = row[42]
		self.parcelsrc = row[43]
		self.shapeLength = row[44]
		self.shapeArea = row[45]
		self.geomErrors = []
		self.addressErrors = []
		self.taxErrors = []
		self.genErrors = []
		
	def writeErrors(self, row, cursor, fieldNames):
		arcpy.AddMessage(self.addressErrors)
		arcpy.AddMessage(self.addressErrors)
		# create 
		if len(self.addressErrors) > 0:
			row[fieldNames.index("AddressElementErrors")] = str(self.addressErrors).strip('[]').replace("'","")
		if len(self.genErrors) > 0:
			row[fieldNames.index("GeneralElementErrors")] = str(self.genErrors).strip('[]').replace("'","")
		if len(self.taxErrors) > 0:
			row[fieldNames.index("TaxrollElementErrors")] = str(self.taxErrors).strip('[]').replace("'","")
		if len(self.geomErrors) > 0:
			row[fieldNames.index("GeometricElementErrors")] = str(self.geomErrors).strip('[]').replace("'","")
		#row[47] = "currParcel.addressErrors"
		cursor.updateRow(row)

	#def __getitem__(self, key):
	#	return self[key]