#Parcel class defines a parcel record based on the attribute schema
class Parcel:
	#Class vars go here

	#Initialize a parcel object
	def __init__(self,row,fieldNames):
		#self.objectid = row.GetField("OID@")
		#self.shape = row.GetField("SHAPE@")
		self.stateid = row.GetField("STATEID")
		self.parcelid = row.GetField("PARCELID")
		self.taxparcelid = row.GetField("TAXPARCELID")
		self.parceldate = row.GetField("PARCELDATE")
		self.taxrollyear = row.GetField("TAXROLLYEAR")
		self.ownernme1 = row.GetField("OWNERNME1")
		self.ownernme2 = row.GetField("OWNERNME2")
		self.pstladress = row.GetField("PSTLADRESS")
		self.siteadress = row.GetField("SITEADRESS")
		self.addnumprefix = row.GetField("ADDNUMPREFIX")
		self.addnum = row.GetField("ADDNUM")
		self.addnumsuffix = row.GetField("ADDNUMSUFFIX")
		self.prefix = row.GetField("PREFIX")
		self.streetname = row.GetField("STREETNAME")
		self.streettype = row.GetField("STREETTYPE")
		self.suffix = row.GetField("SUFFIX")
		self.landmarkname = row.GetField("LANDMARKNAME")
		self.unittype = row.GetField("UNITTYPE")
		self.unitid = row.GetField("UNITID")
		self.placename = row.GetField("PLACENAME")
		self.zipcode = row.GetField("ZIPCODE")
		self.zip4 = row.GetField("ZIP4")
		self.state = row.GetField("STATE")
		self.schooldist = row.GetField("SCHOOLDIST")
		self.schooldistno = row.GetField("SCHOOLDISTNO")
		self.cntassdvalue = row.GetField("CNTASSDVALUE")
		self.lndvalue = row.GetField("LNDVALUE")
		self.impvalue = row.GetField("IMPVALUE")
		self.mflvalue = row.GetField("MFLVALUE")
		self.estfmkvalue = row.GetField("ESTFMKVALUE")
		self.netprpta = row.GetField("NETPRPTA")
		self.grsprpta = row.GetField("GRSPRPTA")
		self.propclass = row.GetField("PROPCLASS")
		self.auxclass = row.GetField("AUXCLASS")
		self.assdacres = row.GetField("ASSDACRES")
		self.deedacres = row.GetField("DEEDACRES")
		self.gisacres = row.GetField("GISACRES")
		self.coname = row.GetField("CONAME")
		self.loaddate = row.GetField("LOADDATE")
		self.parcelfips = row.GetField("PARCELFIPS")
		self.parcelsrc = row.GetField("PARCELSRC")
		self.shapeLength = row.GetField("SHAPE_Length")
		self.shapeArea = row.GetField("SHAPE_Area")
		# self.geometry = row.GetField("geometry")		
		self.geometricErrors = []
		self.addressErrors = []
		self.taxErrors = []
		self.generalErrors = []
		try:
			self.shapeXY =  row.GetGeometryRef().Centroid()  #row.GetField("SHAPE@XY")
		except:
			self.shapeXY = None

	def writeErrors(self, row, fieldNames):
		#Write all accumulated errors to their respective rows, then update the row within the cursor
		if len(self.addressErrors) > 0:
			addressErrors = str(self.addressErrors).strip('[]').replace("'","").replace('"','').replace(",","  | ").replace("#","'").replace(";",",")
			row.SetField("AddressElementErrors", addressErrors)
		if len(self.generalErrors) > 0:
			generalErrors = str(self.generalErrors).strip('[]').replace("'","").replace('"','').replace(",","  | ").replace("#","'").replace(";",",")
			row.SetField("GeneralElementErrors", generalErrors)
		if len(self.taxErrors) > 0:
			taxErrors = str(self.taxErrors).strip('[]').replace("'","").replace('"','').replace(",","  | ").replace("#","'").replace(";",",")
			row.SetField("TaxrollElementErrors", taxErrors)
		if len(self.geometricErrors) > 0:
			geometricErrors = str(self.geometricErrors).strip('[]').replace("'","").replace('"','').replace(",","  | ").replace("#","'").replace(";",",")
			row.SetField("GeometricElementErrors", geometricErrors) 