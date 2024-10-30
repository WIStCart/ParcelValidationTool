# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# example_field.py
# This is an example using open source tools to work with fields of spatial
#   data.
# Hayden Elza (hayden.elza@gmail.com)
# Created: 2022-04-04
# Modified: 
#------------------------------------------------------------------------------

import sys

# Check install
try: from osgeo import ogr, gdal
except: sys.exit('ERROR: cannot find GDAL/OGR modules')


# Enable GDAL/OGR exceptions
gdal.UseExceptions()

# Parameters
gdb_driver = ogr.GetDriverByName('OpenFileGDB')
parcels_filename = 'V8ValidationTool_dist/TEST_DATASET_PARCELS_2022/TEST_DATASET_PARCELS_2022.gdb'


def check_numeric_text_value(parcel, field, accept_null):

    # Get values
    parcel_id = parcel.GetField("PARCELID")
    field_value = parcel.GetField(field)
    # print(parcel_id, field_value)

    # If accepting Null
    if accept_null:

        # If value is Null then return
        if field_value is None: return

        # If value is invalid Null type
        elif field_value in ["<Null>", "<NULL>", "NULL", " ", ""]:

            # Throw error and return
            warning(parcel_id, field, "invalid null")
            return
    
    # If not accepting null and is null or null-ish
    elif (not accept_null) and (field_value is None):
        warning(parcel_id, field, "null not accepted")
        return

    # Check if digit (int or float)
    elif field_value.isdigit(): return

    # If not a digit, throw error and return
    else: 
        warning(parcel_id, field, "not digit")
        return


def warning(parcel_id, field, error):

    # Error reason
    if error=="invalid null": reason = "has an invalid null value"
    elif error=="null not accepted": reason = "cannot be null"
    elif error=="not digit": reason = "needs to be a digit"
    else: reason = "has an invalid value"

    # Print warning
    print(f"WARNING: Parcel {parcel_id} {reason} for field {field}")

    return


# Open filegeodatabase
parcels = gdb_driver.Open(parcels_filename, 0)

# Get Parcels Layer
parcels_layer = parcels.GetLayer()

# Check each parcel
for parcel in parcels_layer:
    check_numeric_text_value(parcel, "ADDNUM", True)