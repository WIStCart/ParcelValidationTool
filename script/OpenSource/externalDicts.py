'''This file contains the lengthy dictionaries used by the validation tool script'''


## list of field names with ogr schema type 
fieldNames =  ["STATEID", "PARCELID","TAXPARCELID","PARCELDATE","TAXROLLYEAR",
"OWNERNME1","OWNERNME2","PSTLADRESS","SITEADRESS","ADDNUMPREFIX","ADDNUM","ADDNUMSUFFIX","PREFIX","STREETNAME",
"STREETTYPE","SUFFIX","LANDMARKNAME","UNITTYPE","UNITID","PLACENAME","ZIPCODE","ZIP4","STATE","SCHOOLDIST",
"SCHOOLDISTNO","CNTASSDVALUE","LNDVALUE","IMPVALUE","MFLVALUE","ESTFMKVALUE","NETPRPTA","GRSPRPTA",
"PROPCLASS","AUXCLASS","ASSDACRES","DEEDACRES","GISACRES","CONAME","LOADDATE","PARCELFIPS","PARCELSRC", "SHAPE_Length", "SHAPE_Area","GeneralElementErrors","AddressElementErrors","TaxrollElementErrors","GeometricElementErrors"]

fieldListPass = ["OID","OID@","SHAPE","SHAPE@","SHAPE_LENGTH","SHAPE_AREA","SHAPE_XY","SHAPE@LENGTH","SHAPE@AREA","SHAPE@XY", "LONGITUDE","LATITUDE","IMPROVED","FORESTVALUE","GENERALELEMENTERRORS","ADDRESSELEMENTERRORS","TAXROLLELEMENTERRORS","GEOMETRICELEMENTERRORS", "SHAPE_Length", "SHAPE_Area"]

#V10 schema requirements
parcelSchemaReq = {
	'STATEID':[['String'],[100]],
	'PARCELID':[['String'],[100]],
	'TAXPARCELID':[['String'],[100]],
	'PARCELDATE':[['String'],[25]],
	'TAXROLLYEAR':[['String'],[10]],
	'OWNERNME1':[['String'],[254]],
	'OWNERNME2':[['String'],[254]],
	'PSTLADRESS':[['String'],[200]],
	'SITEADRESS':[['String'],[200]],
	'ADDNUMPREFIX':[['String'],[50]],
	'ADDNUM':[['String'],[50]],
	'ADDNUMSUFFIX':[['String'],[50]],
	'PREFIX':[['String'],[50]],
	'STREETNAME':[['String'],[50]],
	'STREETTYPE':[['String'],[50]],
	'SUFFIX':[['String'],[50]],
	'LANDMARKNAME':[['String'],[50]],
	'UNITTYPE':[['String'],[50]],
	'UNITID':[['String'],[50]],
	'PLACENAME':[['String'],[100]],
	'ZIPCODE':[['String'],[50]],
	'ZIP4':[['String'],[50]],
	'STATE':[['String'],[50]],
	'SCHOOLDIST':[['String'],[50]],
	'SCHOOLDISTNO':[['String'],[50]],
	'CNTASSDVALUE':[['String','Real'],[50,0]],
	'LNDVALUE':[['String','Real'],[50,0]],
	'IMPVALUE':[['String','Real'],[50,0]],
	'MFLVALUE':[['String','Real'],[50,0]],
	'ESTFMKVALUE':[['String','Real'],[50,0]],
	'NETPRPTA':[['String','Real'],[50,0]],
	'GRSPRPTA':[['String','Real'],[50,0]],
	'PROPCLASS':[['String'],[150]],
	'AUXCLASS':[['String'],[150]],
	'ASSDACRES':[['String','Real'],[50,0]],
	'DEEDACRES':[['String','Real'],[50,0]],
	'GISACRES':[['String','Real'],[50,0]],
	'CONAME':[['String'],[50]],
	'LOADDATE':[['String'],[10]],
	'PARCELFIPS':[['String'],[10]],
	'PARCELSRC':[['String'],[50]],
}

#V3 zoning schema requirements
zoneSchemaReq = {
	'ZONINGFIPS':[['STRING'],[10]],
	'JURISDICTION':[['STRING'],[100]],
	'ZONINGCLASS':[['STRING'],[100]],
	'DESCRIPTION':[['STRING'],[254]],
	'LINK':[['STRING'],[254]]
}

#bad characters dictionary
fieldNamesBadChars = {
"PARCELID": ["\n","\r","$","^","=","<",">","@","%","?","`","!","~","(",")"],
"TAXPARCELID": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","~","(",")"],
"PARCELDATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\-"],
"TAXROLLYEAR": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',"\-"],
"OWNERNME1": ["\n","\r"],
"OWNERNME2": ["\n","\r"],
"PSTLADRESS": ["\n","\r"],
"SITEADRESS": ["\n","\r"],
"ADDNUMPREFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ADDNUM": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ADDNUMSUFFIX": ["\n","\r","$","^","=","<",">","@","%","&","?","`","!","*","~",',',],
"PREFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"STREETNAME": ["\n","\r","$","^","=","<",">","@","#","%","?","!","*","~","(",")"],
"STREETTYPE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"SUFFIX": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"LANDMARKNAME": ["\n","\r"],
"UNITTYPE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"UNITID": ["\n","\r","$","^","=","<",">","@","%","?","`","!","*","~","(",")",','],
"PLACENAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"ZIPCODE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"ZIP4": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"STATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"SCHOOLDIST": ["\n","\r","$","^","=","<",">","@","#","%","&","?","!","*","~","(",")","\\",','],
"SCHOOLDISTNO": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"IMPROVED": ["\n","\r","$","^","=","@","#","%","&","?","`","!","*","~","(",")",',','.',"\-"],
"CNTASSDVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"LNDVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"IMPVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")",',',"\-"],
"MFLVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"ESTFMKVALUE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"NETPRPTA": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"GRSPRPTA": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"PROPCLASS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/','.',"\-"],
"AUXCLASS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/','.',"\-"],
"ASSDACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"DEEDACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"GISACRES": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',','],
"CONAME": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',',"\-"],
"LOADDATE": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")",',','.','\-'],
"PARCELFIPS": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"],
"PARCELSRC": ["\n","\r","$","^","=","<",">","@","#","%","&","?","`","!","*","~","(",")","\\",'/',',','.',"\-"]
}

#acceptable COP domains
copDomains = ['1','2','3','4','5','6','7','5M','M']

#acceptable AUXCOP domains
auxDomains = ['W1','W2','W3','W4','W5','W6','W7','W8','W9','X1','X2','X3','X4','AW','AWO','XTEL']

#dictionary for completeness collection
CompDict = {
	'STATEID':0,
	'PARCELID':0,
	'TAXPARCELID':0,
	'PARCELDATE':0,
	'TAXROLLYEAR':0,
	'OWNERNME1':0,
	'OWNERNME2':0,
	'PSTLADRESS':0,
	'SITEADRESS':0,
	'ADDNUMPREFIX':0,
	'ADDNUM':0,
	'ADDNUMSUFFIX':0,
	'PREFIX':0,
	'STREETNAME':0,
	'STREETTYPE':0,
	'SUFFIX':0,
	'LANDMARKNAME':0,
	'UNITTYPE':0,
	'UNITID':0,
	'PLACENAME':0,
	'ZIPCODE':0,
	'ZIP4':0,
	'STATE':0,
	'SCHOOLDIST':0,
	'SCHOOLDISTNO':0,
	'IMPROVED':0,
	'CNTASSDVALUE':0,
	'LNDVALUE':0,
	'IMPVALUE':0,
	'MFLVALUE':0,
	'ESTFMKVALUE':0,
	'NETPRPTA':0,
	'GRSPRPTA':0,
	'PROPCLASS':0,
	'AUXCLASS':0,
	'ASSDACRES':0,
	'DEEDACRES':0,
	'GISACRES':0,
	'CONAME':0,
	'LOADDATE':0,
	'PARCELFIPS':0,
	'PARCELSRC':0,
}


lsadDomains = ['CITY OF','TOWN OF','VILLAGE OF']

# V9 Centroids
ctyCentroidDict = {'BAYFIELD': [431520.93, 680603.53], 'ASHLAND': [472540.66, 673218.59], 'DOUGLAS': [372200.31, 666054.38], 'IRON': [501486.64, 645881.29], 'VILAS': [559568.32, 622897.77], 'BURNETT': [328765.11, 605081.53], 'WASHBURN': [380874.28, 604271.89], 'SAWYER': [433678.34, 603389.86], 'FOREST': [618433.03, 584176.01], 'FLORENCE': [646477.36, 600723.27], 'PRICE': [491780.7, 578564.95], 'ONEIDA': [555505.02, 579181.61], 'POLK': [323600.32, 557748.89], 'BARRON': [375305.33, 551661.58], 'RUSK': [433131.5, 555378.2], 'LINCOLN': [540735.26, 540545.66], 'LANGLADE': [595936.85, 530938.04], 'TAYLOR': [481939.8, 525998.76], 'CHIPPEWA': [418190.04, 512059.01], 'ST CROIX': [325644.3, 509652.16], 'DUNN': [370226.7, 498804.07], 'MENOMINEE': [619716.68, 502411.96], 'MARATHON': [538212.68, 492091.63], 'MARINETTE': [676613.08, 547433.14], 'DOOR': [734729.59, 512362.14], 'CLARK': [470916.11, 472859.35], 'SHAWANO': [620226.54, 482500.67], 'PIERCE': [324457.75, 472682.38], 'EAU CLAIRE': [418074.83, 473406.79], 'OCONTO': [660039.1, 507045.85], 'KEWAUNEE': [712744.48, 450447.72], 'PEPIN': [362603.26, 454671.83], 'PORTAGE': [557078.6, 443637.01], 'WAUPACA': [606076.91, 443675.29], 'WOOD': [518299.08, 443721.19], 'BUFFALO': [376355.42, 427986.83], 'TREMPEALEAU': [409492.01, 425116.6], 'JACKSON': [460977.18, 429521.12], 'OUTAGAMIE': [642301.28, 439157.0], 'BROWN': [678301.0, 444721.31], 'MANITOWOC': [697700.76, 406452.53], 'CALUMET': [662354.38, 400984.68], 'WINNEBAGO': [628582.64, 400528.97], 'ADAMS': [535024.37, 385806.71], 'JUNEAU': [516054.55, 385796.34], 'WAUSHARA': [580715.62, 404704.62], 'MONROE': [468365.55, 385692.51], 'LA CROSSE': [426310.57, 382204.75], 'GREEN LAKE': [595306.96, 370986.65], 'MARQUETTE': [569621.31, 371286.36], 'FOND DU LAC': [639032.53, 364508.52], 'SHEBOYGAN': [686550.48, 362590.99], 'VERNON': [456112.52, 345063.37], 'COLUMBIA': [568975.57, 332443.73], 'SAUK': [523561.34, 324550.69], 'DODGE': [624804.71, 327690.07], 'OZAUKEE': [687813.87, 323729.52], 'WASHINGTON': [663471.72, 323240.45], 'RICHLAND': [485120.4, 320756.6], 'CRAWFORD': [443800.1, 304313.74], 'DANE': [566874.17, 288739.47], 'GRANT': [455403.2, 265315.27], 'IOWA': [509125.6, 282116.41], 'WAUKESHA': [658267.75, 284192.53], 'JEFFERSON': [619773.62, 283870.87], 'MILWAUKEE': [687533.34, 284761.49], 'RACINE': [680918.54, 252272.0], 'GREEN': [552655.48, 245285.47], 'WALWORTH': [639616.99, 244907.38], 'ROCK': [596047.69, 244728.88], 'LAFAYETTE': [509135.31, 243102.05], 'KENOSHA': [679779.11, 236179.66]}
