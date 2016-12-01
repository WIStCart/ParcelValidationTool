import arcpy
from Parcel import Parcel


#Tool inputs


#Copy feature class, add new fields for error reporting


#Create update cursor


#Iterate through records in feature class
#	Create a parcel object
#	Either call individual error checking methods (Error.GeomError.checkGeometry(Parcel)) or grouped methods in the parcel class (parcel.checkGeomErrors())
#	Write out errors to record
#	Del parcel object to conserve mem

#Write general error report
