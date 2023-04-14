import os
import sys

#pathname = os.path.dirname(sys.argv[0])  
pathname = os.path.dirname (os.path.abspath(__file__))      
#print ('path = ' +  pathname)
fullpath = os.path.abspath(pathname) + '\\proj'
os.environ['PROJ_LIB'] = os.path.abspath(fullpath) 
#print ( os.environ['PROJ_LIB'] )