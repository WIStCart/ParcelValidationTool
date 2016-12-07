import arcpy
from Parcel import Parcel

class Error:

	def __init__(self):
		self.genErrorCount = 0
		self.geomErrorCount = 0
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

	#Will contain get, set, display methods

	#Any other total error report data will go here