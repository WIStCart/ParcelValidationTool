import os
import sys
 
pathname = os.path.dirname (os.path.abspath(__file__))    
fullpath = pathname + '\\proj'  
#print (fullpath)
os.environ['PROJ_LIB'] = fullpath  
