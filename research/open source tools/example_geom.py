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
try: from osgeo import ogr, osr, gdal
except: sys.exit('ERROR: cannot find GDAL/OGR modules')

import json
from urllib.request import urlopen


# Enable GDAL/OGR exceptions
# gdal.UseExceptions()

# Parameters
gdb_driver = ogr.GetDriverByName('OpenFileGDB')
parcels_filename = 'V8ValidationTool_dist/TEST_DATASET_PARCELS_2022/TEST_DATASET_PARCELS_2022.gdb'
geojson_driver = ogr.GetDriverByName('GeoJSON')
counties_url = "https://sco-admin.carto.com/api/v2/sql?format=GEOJSON&q=SELECT%20*%20FROM%20%22sco-admin%22.scobase_wi_county_boundaries_24k%20WHERE%20county_nam='Vernon'"


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


for parcel in parcels_layer:
    print(county_feature.GetField("county_cap"))
    county_geom = county_feature.geometry().Clone()
    print(parcel.GetField("PARCELID"))
    parcel_geom = parcel.geometry().Clone()
    within = parcel_geom.Within(county_geom)
    print(within)

    county_geom = None
    parcel_geom = None
    break

# # create the output layer
# shp_driver = ogr.GetDriverByName('ESRI Shapefile')

# outSpatialRef = osr.SpatialReference()
# outSpatialRef.ImportFromEPSG(4326)

# outputShapefile = 'county.shp'
# if os.path.exists(outputShapefile):
#     shp_driver.DeleteDataSource(outputShapefile)
# outDataSet = shp_driver.CreateDataSource(outputShapefile)
# outLayer = outDataSet.CreateLayer("county", geom_type=ogr.wkbMultiPolygon)



del parcels
del county
os.remove('temp.geojson')
