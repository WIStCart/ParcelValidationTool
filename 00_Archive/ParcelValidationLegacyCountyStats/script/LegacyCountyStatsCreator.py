import arcpy

##############################
#
# README: 
# 	1)	We're trying to make one of these for each county:
#			ADAMSLegacyDict = {'PLACENAME': 38653, 'GISACRES': 0, 'CONAME': 38657, 'SUFFIX': 0, 'STREETTYPE': 22335, 'TAXPARCELID': 38657, 'PARCELID': 38657, 'ZIPCODE': 29356, 'PARCELSRC': 38657, 'PARCELFIPS': 38657, 'LOADDATE': 38657, 'PREFIX': 5999, 'AUXCLASS': 5245, 'NETPRPTA': 0, 'SCHOOLDISTNO': 38653, 'UNITID': 697, 'LNDVALUE': 38490, 'OWNERNME1': 38490, 'OWNERNME2': 10531, 'IMPVALUE': 38490, 'CNTASSDVALUE': 38490, 'DEEDACRES': 38490, 'TAXROLLYEAR': 38657, 'PSTLADRESS': 38468, 'IMPROVED': 38490, 'STATEID': 38657, 'ASSDACRES': 38490, 'FORESTVALUE': 0, 'ADDNUMPREFIX': 27, 'ADDNUMSUFFIX': 756, 'ADDNUM': 22335, 'LANDMARKNAME': 29, 'PROPCLASS': 34173, 'UNITTYPE': 697, 'SCHOOLDIST': 38653, 'SITEADRESS': 22335, 'ESTFMKVALUE': 38490, 'GRSPRPTA': 38486, 'STATE': 38657, 'PARCELDATE': 9790, 'STREETNAME': 22335, 'ZIP4': 1101}
#	2)	The values represent the number of records that are NOT NULL per PARCELSRC and field. Variable order in the dicts above does not matter, they are referenced by their "key" (e.g. Dict[field])
#	3)	Use the previous version's most recent statewide version (i.e. V3.0.1). When the tool completes, copy and paste the results in the console to the LegacyCountyStats.py file within the ParcelValidationTool\script directory
#	4)	Make sure to archive the old LegacyCountyStats.py
#	5)	Validate the results through a few spot checks. 
#
##############################

in_fc = arcpy.GetParameterAsText(0)
arcpy.AddMessage("Processing ... ")
arcpy.Delete_management("in_memory")
fields = arcpy.ListFields(in_fc)
field_names = [f.name for f in fields]
skips = ['OBJECTID','SHAPE','SHAPE_LENGTH','SHAPE_AREA']
#county_array = ["ADAMS","ASHLAND","BARRON","BAYFIELD","BROWN","BUFFALO","BURNETT","CALUMET","CHIPPEWA","CLARK","COLUMBIA","CRAWFORD","DANE","DODGE","DOOR","DOUGLAS","DUNN","EAU CLAIRE","FLORENCE","FOND DU LAC","FOREST","GRANT","GREEN","GREEN LAKE","IOWA","IRON","JACKSON","JEFFERSON","JUNEAU","KENOSHA","KEWAUNEE","LA CROSSE","LAFAYETTE","LANGLADE","LINCOLN","MANITOWOC","MARATHON","MARINETTE","MARQUETTE","MENOMINEE","MILWAUKEE","MONROE","OCONTO","ONEIDA","OUTAGAMIE","OZAUKEE","PEPIN","PIERCE","POLK","PORTAGE","PRICE","RACINE","RICHLAND","ROCK","RUSK","SAUK","SAWYER","SHAWANO","SHEBOYGAN","ST. CROIX","TAYLOR","TREMPEALEAU","VERNON","VILAS","WALWORTH","WASHBURN","WASHINGTON","WAUKESHA","WAUPACA","WAUSHARA","WINNEBAGO","WOOD"] # Be careful about ST CROIX: V3 data had ST. CROIX in its PARCELSRC (but V4 shouldnt)
county_array = ["ST. CROIX","TAYLOR","TREMPEALEAU","VERNON","VILAS","WALWORTH","WASHBURN","WASHINGTON","WAUKESHA","WAUPACA","WAUSHARA","WINNEBAGO","WOOD"] # Be careful about ST CROIX: V3 data had ST. CROIX in its PARCELSRC (but V4 shouldnt)
#for testing --> 
#county_array = ["ADAMS","VERNON"]
for county_name in county_array:
	w1 = '"PARCELSRC" = \'' +county_name+ '\''
	arcpy.FeatureClassToFeatureClass_conversion(in_fc, "in_memory", "in_" + county_name.replace(" ","_").replace(".",""), w1)
	field_values = ""
	for field in fields:
		if field.name.upper() not in skips:
			w2 = '"'+field.name+'" IS NOT NULL'  
			lr = arcpy.MakeFeatureLayer_management("in_memory/in_" + county_name.replace(" ","_").replace(".",""), 'tmp_layer', w2).getOutput(0)  
			result = int(arcpy.GetCount_management(lr).getOutput(0))  
			arcpy.Delete_management(lr)
			field_values = field_values + "'" + field.name + "':" + str(result) + ","
	arcpy.AddMessage(county_name.replace(" ","_").replace(".","") + "LegacyDict = {" +(field_values[:-1]) + "}")
	arcpy.Delete_management("in_memory")