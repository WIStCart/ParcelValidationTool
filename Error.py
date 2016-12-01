import arcpy
from Parcel import Parcel

class Error:

	def __init__(self):
		pass

	#Will contain get, set, display methods

	#Any other total error report data will go here

#Class for general error checking
class GenError(Error):

	def __init__(self):
		self.count = 0
		self.errors = []

#Class for geometric error checking
class GeomError(Error):

	def __init__(self):
		self.count = 0
		self.errors = []

#Class for address error checking
class AddressError(Error):

	def __init__(self):
		self.count = 0
		self.errors = []

#Class for tax error checkingg
class TaxError(Error):

	def __init__(self):
		self.count = 0
		self.errors = []