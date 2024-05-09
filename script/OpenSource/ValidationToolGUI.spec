# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['ValidationToolGUI.py', 'ValidationToolScriptFoss.py', 'LegacyCountyStats.py', 'externalDicts.py', 'ErrorFoss.py', 'Parcel.py', 'SummaryFoss.py'],
    pathex=['C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource', 
'C:\\OSGeo4W\\apps\\gdal\\lib\\gdalplugins','C:\\OSGeo4W\\apps\\gdal\\share\\gdal', 'C:\\OSGeo4W\\share\\proj', 'C:\\OSGeo4W\\bin'],
    binaries=[  
('C:\\OSGeo4W\\bin\\python39.dll', 'python39'), 
('C:\\OSGeo4W\\bin\\gdal307.dll', 'gdal307'),
('C:\\OSGeo4W\\apps\\gdal\\lib\\gdalplugins\\ogr_FileGDB.dll', '.')
],
    datas=[('C:\\OSGeo4W\\apps\\Python39\\tcl\\tix8.4.3', 'tcl\\tix8.4.3'),
('C:\\OSGeo4W\\apps\\gdal\\lib\\gdalplugins\\drivers.ini', '.'),
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\proj\\proj.ini', 'proj'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\proj\\proj.db', 'proj'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\data\\CoNameFips.csv', 'data'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\data\\school_district_codes.csv', 'data'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\assets\\V1.ico', 'assets'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\assets\\openfilefolder.gif', 'assets'),
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\summary.js', 'summary'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\explanations.js', 'summary'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\main_compiled.js', 'summary'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\validation.html', 'summary'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\core.min.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\react.js', 'summary\\src'),
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\react-dom.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\babel.min.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\react.production.min.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\react-dom.production.min.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\prop-types.min.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\src\\jquery.min.js', 'summary\\src'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\styles.css', 'summary'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\tippy.css', 'summary'), 
('C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\summary\\withumb.png', 'summary')
],
    hiddenimports=[ 'osgeo', 'osgeo.ogr', 'osgeo.gdal', 'osgeo._gdal', 'osgeo._ogr'],
    hookspath=[ ],
    hooksconfig={},
    runtime_hooks=['hook.py'],
    excludes=['matplotlib', 'scipy', 'fiona', 'geopandas', 'pandas',
 'site', 'tornado', 'PIL', 'PyQt4', 'PyQt5',
 'pydoc', 'pythoncom', 'pywintypes','sqlite3', 'pyz', 'sklearn', 'scapy', 'scrapy', 
 'sympy', 'kivy', 'pyramid', 'opencv', 'lxml',  
 'tensorflow', 'pipenv', 'pattern', 'mechanize', 'beautifulsoup4', 'requests', 'wxPython', 
 'pygi', 'IPython', 'pillow', 'pygame', 
 'pyglet', 'flask', 'django', 'pylint', 'pytube', 'odfpy', 'mccabe', 'pilkit',
 'wrapt', 'astroid', 'isort', 'win32com'],

    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ValidationToolGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\ajwells.AD\\Documents\\GitHub\\ValidationTool\\ParcelValidationTool\\script\\OpenSource\\assets\\V1.ico'],
)
