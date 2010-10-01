#!/usr/bin/env python

#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************

""" usage: mp3reencode.py [options]

    This script goes through the provided path and all its
    subdirectories and reencodes all mp3 files according to
    supplied parameters.

    Written by Ari Bjornsson ari.bjornsson (at) gmail.com
"""

import sys
import os
import getopt
import subprocess
import optparse

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
	
def fileList(workingDir, recursive):
	file_list = []	
	if recursive:
		walk = os.walk(workingDir, topdown=True)
		for root, dirs, files in walk:		        		
			for name in files:
				if os.path.splitext(name)[1].lower() == '.mp3':
					file_list.append(os.path.join(root,name))
	else:
		walk = os.walk(workingDir, topdown=True)	        		
		cnt = 0
		for root, dirs, files in walk:		
			for name in files:
				if os.path.splitext(name)[1].lower() == '.mp3':
					file_list.append(os.path.join(root,name))
			cnt += 1
			if cnt >= 1:
				break
					  
	file_list.sort()
	
	return file_list
	
def printModes(list):
	print "Supported modes are: ",
	for i in list:
		print i,

def reencode(file, audio_layer, sampling_rate, bitrate, bitmode, channels):
	nfile = file[:-4] + "_REENCODED_.mp3"	
	#print file

	avail_bitmodes = ['vbr','abr','cbr']
	avail_bitrates = ['32','40','48','56','64','80','96','112','128','160','192','256']
	avail_channels = ['s','j','f','d','m']
	avail_sampling = ['8','11.025','12','16','22.05','24','32','44.1','48']


        if str(bitrate) in avail_bitrates:
                bitrate = str(bitrate) + ' '
        else:
                print "Error. Unsupported bitrate -b argument!"
                printModes(avail_bitrates)
                sys.exit()

	if bitmode in avail_bitmodes:	
		if bitmode == 'vbr':
			bitmode = '-h '
			bitrate = ''
		elif bitmode == 'abr':
			bitmode = '--abr '
		else:
			bitmode = '-b '
	else:
		print "Error. Unsupported bitmode -m argument!"
		printModes(avail_bitmodes)
		sys.exit()	
	
	if channels in avail_channels:
		channels = '-m ' + str(channels) + ' '
	else:
		print "Error. Unsupported channel -c argument!"
		printModes(avail_channels)	
		sys.exit()

	if str(sampling_rate) in avail_sampling:
		sampling_rate = '--resample ' + str(sampling_rate) + ' ' 
	else:
		print "Error. Unsupported sampling rate -s argument!"
		printModes(avail_sampling)
		sys.exit()

	command = 'lame --mp3input ' + channels + bitmode + bitrate + sampling_rate + unix_path('f',file) + ' ' + unix_path('f',nfile)
	#print command
	# channels: -m 
#						s:sterio 
#						j:jointsterio 
#						f:forcedjointsterio 
#						d:dualchannels 
#						m:mono
	# bitrate: --abr -b 
#	              For MPEG1 (sampling frequencies of 32, 44.1 and 48 kHz)
#                n = 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320
#
#                For MPEG2 (sampling frequencies of 16, 22.05 and 24 kHz)
#                n = 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160
	# sampling: --resample sfreq
#						sfreq = 8, 11.025, 12, 16, 22.05, 24, 32, 44.1, 48
	
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	p.wait()		
	output = p.communicate()
	#print output

def reencode_files(audio_layer, sampling_rate, bitrate, bitmode, channels, workingDir, recursive):
	list = fileList(workingDir, recursive)
    
	for file in list:
		reencode(file, audio_layer, sampling_rate, bitrate, bitmode, channels)    
    
# Main program: parse command line and start processing
def main():
	try:
		parser = optparse.OptionParser()
		parser.add_option('-a', '--audio-layer', 
								dest="audio_layer",
								help="Unsupported",								
								default="",
								)		
		parser.add_option('-s', '--sampling-rate', 
								dest="sampling_rate",
								help="Reencode mp3 file with different sampling rate; lame --resample X\nDefault [22.05 kHz]",
								default="22.05",
								)
		parser.add_option('-b', '--bitrate', 
								dest="bitrate",
								help="Reencode mp3 file with different bitrate; lame --abr X | -h | -b X\nDefault [32 kbps] ",
								default="32",
								)
		parser.add_option('-c', '--channels', 
								dest="channels",
								help="Reencode mp3 file with different channels; lame -m X\nDefault [s:sterio]",
								default="s",
								)
		parser.add_option('-d', '--workingDir', 
								dest="workingDir",
								default=os.getcwd(),
								)
		parser.add_option('-r', '--recursive', 
								dest="recursive",
								action="store_true",								
								default=False,
								)
		parser.add_option('-m', '--bit-mode',
								dest="bitmode",
								help="Reencode mp3 file with constant-, average- or variable bitrates; lame --abr X | -h | -b X\nDefault [cbr]",
								default="cbr",
								)
		options, remainder = parser.parse_args()
	
	except parser.error, msg:
		usage(msg)

	if os.path.isdir(options.workingDir):
		workingDir = options.workingDir
	else:
		print "Error: The provided path is no directory"
		sys.exit()   				
                  
	if workingDir[-1] != "/":
		workingDir += "/"
		
	reencode_files(options.audio_layer, options.sampling_rate, options.bitrate, options.bitmode, options.channels, options.workingDir, options.recursive)
	
	       
if __name__ == '__main__':
	main()
