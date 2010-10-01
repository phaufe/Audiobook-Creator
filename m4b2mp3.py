#!/usr/bin/env python

#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************

""" usage: m4b2mp3.py [options]

    -d  work with the provided directory
        [default: the current working directory]
    -h  this help
    -o  overwrite existing Mp3 files
    -r  remove all converted M4b files 

    This script goes through the provided path and all its
    subdirectories and converts all m4b or mp4 files to mp3 files.

    Written by Ari Bjornsson ari.bjornsson (at) gmail.com
"""

import sys
import os
import getopt
import subprocess

def usage(*args):
    sys.stdout = sys.stderr
    print __doc__
    print 50*"-"
    for msg in args: print msg
    sys.exit(2)
    
def unix_path(type,path):
	if type == 'd': 
		if path[-1] != '/': path += '/'

	path = path.replace(' ','\ ')
	path = path.replace("'","\\'")
	path = path.replace("(","\\(")
	path = path.replace(")","\\)")
	path = path.replace("{","\\{")
	path = path.replace("}","\\}")
	path = path.replace('&','\&')

	return path

def convert(pathM4b, overwriteMp3s, removeM4bs, workingDir = ""):
	pathMp3 = os.path.splitext(pathM4b)[0] + ".mp3"
	
	if not overwriteMp3s and os.path.exists(pathMp3):
		print "Info: %s already exists" % pathMp3[len(workingDir):]
		return
	print "converting: " + pathM4b[len(workingDir):] + " -> " + pathMp3[len(workingDir):]
	
	p1 = subprocess.Popen(["faad", "-q", "-o", "-", pathM4b], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(["lame", "-", pathMp3], stdin=p1.stdout, stdout=subprocess.PIPE)
	output = p2.communicate()
	
	if output[0] or output[1]:
		print "error converting %s" % pathM4b[len(workingDir):]
		print output[0]
		print output[1]
		return
	else:
		if removeM4bs:
			os.unlink(pathM4b)

def convertRecursive(workingDir, overwriteMp3s, removeM4bs):
	walk = os.walk(workingDir, topdown=True)
	file_list = []
	for root, dirs, files in walk:		        
		for name in files:
			if os.path.splitext(name)[1].lower() == ".m4b" or os.path.splitext(name)[1].lower() == ".mp4" :
					file_list.append(os.path.join(root,name))
					  
	file_list.sort()

	for m4bfile in file_list:
		convert(m4bfile, overwriteMp3s, removeM4bs, workingDir)
			
	
# Main program: parse command line and start processing
def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'd:hor')
	except getopt.error, msg:
		usage(msg)

	workingDir = os.getcwd()
	overwriteMp3s = False
	removeM4bs = False

	for o, a in opts:
		if o == '-h':
			print __doc__
			sys.exit()
		if o == '-d':
			if os.path.isdir(a):
				workingDir = a
			else:
				print "Error: The provided path is no directory"
				sys.exit()   				
		if o == '-o':
			overwriteMp3s = True
		if o == '-r':           
			removeM4bs = True	     
                
		if workingDir[-1] != "/":
			workingDir += "/"
		
	convertRecursive(workingDir, overwriteMp3s, removeM4bs)
        
if __name__ == '__main__':
	main()