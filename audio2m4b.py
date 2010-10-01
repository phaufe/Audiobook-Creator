#!/usr/bin/env python

#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************

""" usage: audio2m4b.py [options]
		  Note: mp3 and wav files are the only supported
		  sources.
		  
    -d  work with the provided directory
        [default: the current working directory]
    -h  this help
    -w  set source file as .wav (default: .mp3)
    -o  overwrite existing m4b files
    -r  remove all converted source files 

    This script goes through the provided path and all its
    subdirectories and converts all source files to m4b files.

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
        #path = path.replace('\\ ','\ ')

        return path
    
def convert(pathSource, overwriteM4bs, removeSources, Source, workingDir = ""):
	pathM4b = os.path.splitext(pathSource)[0] + ".m4b"
	
	if not overwriteM4bs and os.path.exists(pathM4b):
		print "Info: %s already exists" % pathM4b[len(workingDir):]
		return
	print "converting: " + pathSource[len(workingDir):] + " -> " + pathM4b[len(workingDir):]
	
	if Source == '.mp3':
		p1_command = "mplayer -ao pcm:fast:file=" + unix_path('d',workingDir) + "temp.pcm -vo null -vc null -really-quiet " + unix_path('f',pathSource)
		#print p1_command
		print "Extracting source to [pcm]..."
		p1 = subprocess.Popen(p1_command, shell=True, stdout=subprocess.PIPE)
		p1.wait()
		if os.path.isfile(workingDir + 'temp.pcm'):
			print "Encoding source to [m4b]..."
			p2 = subprocess.Popen(["faac", "-w", workingDir + "temp.pcm", "-o", pathM4b], stdout=subprocess.PIPE)
			output = p2.communicate()
			os.unlink(workingDir + 'temp.pcm')
		else:
			print "Error: mplayer was unable to create temp file"
			sys.exit()

	elif Source == '.wav':
		p = subprocess.Popen(["faac", "-w", "-o", pathM4b, pathSource], stdout=subprocess.PIPE)
		output = p.communicate()
	else:
		output = ['Error','This source file is not supported']
	
	if output[0] or output[1]:
		print "error converting %s" % pathSource[len(workingDir):]
		print output[0]
		print output[1]
		return
	else:
		if removeSources:
			os.unlink(pathSource)

def convertRecursive(workingDir, overwriteM4bs, removeSources, Source):
	walk = os.walk(workingDir, topdown=True)
	file_list = []
	for root, dirs, files in walk:		        
		for name in files:
			if os.path.splitext(name)[1].lower() == Source:
					file_list.append(os.path.join(root,name))
					  
	file_list.sort()

	for file in file_list:
		convert(file, overwriteM4bs, removeSources, Source, workingDir)
			
	
# Main program: parse command line and start processing
def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'd:whor')
	except getopt.error, msg:
		usage(msg)

	workingDir = os.getcwd()
	overwriteM4bs = False
	removeSources = False
	Source = '.mp3'

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
			overwriteM4bs = True
		if o == '-r':           
			removeSources = True	     
		if o == '-w':
			Source = '.wav'                
                
	if workingDir[-1] != "/":
		workingDir += "/"
		
	convertRecursive(workingDir, overwriteM4bs, removeSources, Source)
        
if __name__ == '__main__':
	main()
