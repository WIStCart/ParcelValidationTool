# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# example_geom.py
# This is an example using open source tools to work with geometry of spatial
#   data.
# Hayden Elza (hayden.elza@gmail.com)
# Created: 2022-03-30
# Modified: 
#------------------------------------------------------------------------------


import sys, os

# Check install
try: from osgeo import ogr, gdal
except: sys.exit('ERROR: cannot find GDAL/OGR modules')

import json
from urllib.request import urlopen


# Enable GDAL/OGR exceptions
gdal.UseExceptions()

# Parameters
gdb_driver = ogr.GetDriverByName('OpenFileGDB')
parcels_filename = 'V8ValidationTool_dist/TEST_DATASET_PARCELS_2022/TEST_DATASET_PARCELS_2022.gdb'
geojson_driver = ogr.GetDriverByName('GeoJSON')
counties_url = "https://sco-admin.carto.com/api/v2/sql?format=GEOJSON&q=SELECT%20cartodb_id,%20county_nam,%20ST_Transform(the_geom,%203071)%20AS%20the_geom%20FROM%20scobase_wi_county_boundaries_24k%20WHERE%20county_nam=%27Vernon%27"


# Open filegeodatabase
parcels = gdb_driver.Open(parcels_filename, 0)

# Download geojson to temp file
with open('temp.geojson', 'w') as f:
    response = urlopen(counties_url)
    json.dump(json.loads(response.read()), f, indent=None)

# Open geojson
county = ogr.Open('temp.geojson')

# Get county feature
county_feature= county.GetLayer().GetFeature(0)

# Get Parcels Layer
parcels_layer = parcels.GetLayer()

# Check each parcel
for parcel in parcels_layer:

    # Get geometries
    county_geom = county_feature.geometry().Clone()
    parcel_geom = parcel.geometry().Clone()

    # Check if parcel within county geom (both geometries must have the same SRS for this to work)
    within = parcel_geom.Within(county_geom)

    # Print results
    print("{county} {parcel} {within}".format(
        county=county_feature.GetField("county_nam"), 
        parcel=parcel.GetField("PARCELID"), 
        within=within)
    )

    # Clear geom references
    county_geom = None
    parcel_geom = None


del parcels
del county
os.remove('temp.geojson')
