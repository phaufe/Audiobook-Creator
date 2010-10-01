#!/usr/bin/env python

##############################################################################
# Written by ari.bjornsson@gmail.com - Enjoy
#
# This script traverses recursively through directory tree from where it was
# started. It converts all videos using HandBrakeCLI to a Android, iPhone and 
# iPod Touch friendly format. 
#
# The script does not traverse directories if the text from exclude_dirs array 
# is found within the directory path.
#
# Similarly files are excluded with text from exclude_files, in addition
# files can be filtered by suffixes. 
#
###############################################################################
###############################################################################

import os
import subprocess
import logging
import time
import shutil
import optparse
import sys

# Logging
logging.basicConfig(level=logging.INFO)


# Variables
suffixes = ['mp3']
exclude_dirs = ['sample']
exclude_files = ['REENCODED']



def exclude_directories(dir, excl_arr):
	for excl in excl_arr:
                dir = dir.lower()
                if  dir.find(excl.lower()) > 0:
                        return True # Do not enter directories which contain exclude text
		
	return False


class mp3file:
	def __init__(self, path, file):
		self.path = path
		self.name = file
		self.corrupt = False
		self.audiolayer = ''
		self.samplingrate = ''
		self.bitrate = ''
		self.channels = ''
		self.duration = ''
		self.author = ''
		self.series = ''
		self.number = ''
		self.title = ''
		self.comment = ''
		self.encoding_failed = False
		self.discrepency = False
		self.get_info()


	def get_info(self):
		logging.debug("Getting mp3 info for file: %s" % self.name)
		proc = subprocess.Popen(["mp3check", "-c", os.path.join(self.path,self.name)]
					, shell=False
					, stdout=subprocess.PIPE
					, stderr=subprocess.PIPE
					)

		stdout_value, stderr_value = proc.communicate()
		logging.debug('stdout: %s' % stdout_value)
		#logging.debug('stderr: %s' % stderr_value)

		attr = []
		for item in stdout_value.split(' '):
			if item != '':
 				attr.append(item)

		if len(attr) < 7:
			self.corrupt = True
			logging.info('Error getting mp3 info!')
		else:
			self.corrupt = False
			self.audiolayer = attr[0]
			self.samplingrate = attr[1]
			self.bitrate = attr[2]
			self.channels = attr[3]		
			self.duration = attr[6]

        def encode(self, channels, bitrate, samplingrate):
                logging.info('Encoding file: %s' % self.name)
                temp_name = self.name + '.tmp'

		# If temp file exists, remove it
		if os.path.isfile(os.path.join(self.path,temp_name)):
			try:
				logging.debug('Temp file exist, removing..')
				os.remove(os.path.join(self.path,temp_name))
			except:
				logging.info('Unable to remove temp file, press Enter')

                proc = subprocess.Popen('lame --mp3input -m %s -b %s --resample %s "%s" "%s"' % (channels, bitrate, samplingrate, os.path.join(self.path,self.name), os.path.join(self.path,temp_name))
                                        , shell=True
                                        , stdout=subprocess.PIPE
                                        , stderr=subprocess.PIPE
                                        )

		
                stdout_value, stderr_value = proc.communicate()
                logging.debug('stdout: %s' % stdout_value)
                logging.debug('stderr: %s' % stderr_value)
		
		# if successful then temp file must exist
		if os.path.isfile(os.path.join(self.path,temp_name)):
			# Replace old file with new file
			try:
				logging.debug('Renaming orginal file as %s.orig' % self.name)
				shutil.move(os.path.join(self.path, self.name), os.path.join(self.path, self.name + '.orig'))
				
				try:
	                                logging.debug('Replacing original file with encoded file')
                                	shutil.move(os.path.join(self.path, temp_name), os.path.join(self.path, self.name))
				except:
					logging.debug('Replacing orginal file unsuccessful')
					self.encoding_failed = True
			except:
				logging.debug('Unable to store orginal file, aborting!')
				self.encoding_failed = True
	
			if not self.encoding_failed:
				logging.info('Encoding successful')

	def rename(self):
		if self.author != "" and self.series != "" and self.number != "" and self.title != "":
			new_name = '%s - %s - %s - %s.mp3' % (self.author, self.series, self.number, self.title)	
		elif self.series == "" and self.number == "":
			new_name = '%s - %s.mp3' % (self.author, self.title)
		elif self.series == "":
			new_name = '%s - %s - %s.mp3' % (self.author, self.number, self.title) 
		elif self.number == "":
			new_name = '%s - %s - %s.mp3' % (self.author, self.series, self.title)
		else:
			new_name = 'newaudiobook.mp3'
	
		try:
			logging.info('Renaming: %s to %s' % (self.name, new_name))
			shutil.move(os.path.join(self.path,self.name),os.path.join(self.path,new_name))
			self.name = new_name
		except:
			logging.debug('Unable to rename temp file')	

	def tag(self):
		self.comment = "This audiobooks was created with audiobookcreator.py, written by ari.bjornsson@gmail.com"
		
		logging.info('Retagging file')	
		clear = subprocess.Popen('id3v2 -D "%s"' % (os.path.join(self.path, self.name))
					, shell=True
					, stdout=subprocess.PIPE
					, stderr=subprocess.PIPE
					)
		
		stdout_value, stderr_value = clear.communicate()
		logging.debug('stdout: %s' % stdout_value)
		logging.debug('stderr: %s' % stderr_value)

		proc = subprocess.Popen('id3v2 -a "%s" -A "%s" -t "%s" -c "%s" -T "%s" "%s"' % (self.author, self.series, self.title, self.comment, self.number, os.path.join(self.path, self.name))
					, shell=True
					, stdout=subprocess.PIPE
					, stderr=subprocess.PIPE
					)

		stdout_value, stderr_value = proc.communicate()
                logging.debug('stdout: %s' % stdout_value)
                logging.debug('stderr: %s' % stderr_value)



class fileset:
	def __init__(self):
		self.retry = False
		self.file = ''
		self.name = ''
		self.author = ''
		self.series = ''
		self.audiolayers = []
		self.bitrates = []
		self.samplingrates = []
		self.channels = []	
		self.pop_audiolayer = ''
		self.pop_samplingrate = ''
		self.pop_bitrate = ''
		self.pop_channels = ''
		self.discrepency = False
		self.get_files()
		self.number = len(self.set)	
		self.summary()	

	def getfile(self):
		return self.file

	def get_files(self):
		self.set = []
		for top, dirs, files in os.walk(os.getcwd()):
	        	# Check for directory exclusion violation       
	        	if exclude_directories(top, exclude_dirs):
	                	break # Break on exclusion 
	        	else:
        	        	files.sort()
                		fcount = 0

                		for file in files:
					# Check and continue if file exists				
					if os.path.isfile(os.path.join(top,file)):
						filelow = file.lower()
                       	         		suffix = filelow.split('.')[-1]

						# Check and continue if file is an mp3 file
						if suffix == 'mp3':
							mp3 = mp3file(top,file)
							self.set.append(mp3)
							self.audiolayers.append(mp3.audiolayer)
							self.samplingrates.append(mp3.samplingrate)
							self.bitrates.append(mp3.bitrate)
							self.channels.append(mp3.channels)
						else:
							logging.debug('File %s isn\'t a mp3 file' % file)  
					else:
						logging.debug('File doesn\'t exist: %s' % file) 

		return self.set

	def unique_items(self, L):
		found = set()
		uniques = []
		for item in L:
			if item not in found:
				uniques.append(item)
				found.add(item)
		return uniques

	def count_me(self, list):
		d = {}
		for i in set(list):
			d[i] = list.count(i)

		return d

	def summary(self):
		
		u_audiolayers = self.count_me(self.audiolayers)
		u_sampl = self.count_me(self.samplingrates)
		u_bit = self.count_me(self.bitrates)
		u_chan = self.count_me(self.channels)

		a_max = 0
		s_max = 0
		b_max = 0
		c_max = 0

		for i in u_audiolayers:
			logging.debug('Audiolayer:\t %s found in %s of %s' % (i, u_audiolayers[i], self.number))
			if u_audiolayers[i] > a_max:
				a_max = u_audiolayers[i]
				self.pop_audiolayer = i
		for i in u_sampl:
                        logging.debug('Sampl. rate:\t %s kHz found in %s of %s' % (i, u_sampl[i], self.number))
			if u_sampl[i] > s_max:
				s_max = u_sampl[i]
				self.pop_samplingrate = i
                for i in u_bit:
                        logging.debug('Bitrate:\t %s kbps found in %s of %s' % (i, u_bit[i], self.number))
			if u_bit[i] > b_max:
				b_max = u_bit[i]
				self.pop_bitrate = i
                for i in u_chan:
                        logging.debug('Channels:\t %s found in %s of %s' % (i, u_chan[i], self.number))
			if u_chan[i] > c_max:
				c_max = u_chan[i]
				self.pop_channels = i

		if len(u_audiolayers) > 1 or len(u_sampl) > 1 or len(u_bit) > 1 or len(u_chan) > 1:
			self.discrepency = True


	def fix_files(self):
		for file in self.set:
			if file.audiolayer != self.pop_audiolayer or file.samplingrate != self.pop_samplingrate or file.bitrate != self.pop_bitrate or file.channels != self.pop_channels:
				file.discrepency = True
				logging.info('File %s is not encoded as the others in this set' % file.name)
				logging.debug('Audiolayer is:\t %s but not %s' % (file.audiolayer, self.pop_audiolayer))
                        	logging.debug('Sampling rate is:\t %s but not %s' % (file.samplingrate, self.pop_samplingrate))
                        	logging.debug('Bitrate is:\t %s but not %s' % (file.bitrate, self.pop_bitrate))
                        	logging.debug('Channel is:\t %s but not %s' % (file.channels, self.pop_channels))

				file.encode(self.pop_channels, self.pop_bitrate, self.pop_samplingrate)


	def join_files(self):
		s = ''
		t = 'temp.join'
		for file in self.set:
			s = s + '"%s" ' % os.path.join(file.path, file.name)	
		
		# If temp file exist, remove it
		if os.path.isfile(os.path.join(os.getcwd(),t)):
			try:
				logging.debug('Temp file exists, removing ..')
				os.remove(os.path.join(os.getcwd(),t))
			except:
				logging.info('Unable to remove temp file, press Enter')


		proc = subprocess.Popen('mpgtx -j -N --force %s -o "%s"' % (s, os.path.join(os.getcwd(),t))
					, shell=True
					, stdout=subprocess.PIPE
					, stderr=subprocess.PIPE
					)	

		stdout_value, stderr_value = proc.communicate()
		#logging.info('stdout: %s' % stdout_value)
		#logging.info('stderr: %s' % stderr_value)

		if os.path.isfile(os.path.join(os.getcwd(),t)):
			logging.info('stderr: %s' % stderr_value)
			logging.info('Files joined togeter into file %s' % t)
			self.retry = False
			self.file = mp3file(os.getcwd(),t)
		else:
			# TODO: handle "is nota valid mpeg file"
			t = stderr_value.split('\n')
			if len(t) > 2:
				line = t[len(t)-2]
				if line.find('is not a valid mpeg file') != -1:
					logging.info('Invalid mpeg file detected')

					elements = line.split('/')
					filename = elements[len(elements)-1][:-25] 
					path = line[:-(25+len(filename))]
					
					file = mp3file(path, filename)
					file.encode(self.pop_channels, self.pop_bitrate, self.pop_samplingrate)
					#logging.info(path)
					if file.encoding_failed:	
						self.retry = False
						logging.info('Encoding failed, script unable to fix files')
					else:	
						self.retry = True					
			if self.retry:
				return False			


def main():
	try:
		parser = optparse.OptionParser()
		parser.add_option('-a', '--author'
			, dest="author"
			, help="Author name in quotes"
			, default=""
			)
                parser.add_option('-A', '--series'
                        , dest="series"
                        , help="Series name in quotes"
                        , default=""
                        )
                parser.add_option('-t', '--title'
                        , dest="title"
                        , help="Book title in quotes"
                        , default=""
                        )
                parser.add_option('-T', '--track'
                        , dest="number"
                        , help="Book number in quotes"
                        , default=""
                        )

		options, remainder = parser.parse_args()

	except parser.error, msg:
		usage(msg)

	
	#print options.author
	#print options.series
	#print options.title
	#print options.number

	# Retrieve file set
	x = fileset()

	# If there are file encoding discrepencies,
	# then lets try to fix them
	if x.discrepency:
		x.fix_files()

	# After fixing, lets try to join the files together
	x.join_files()

	while x.retry:
		logging.info('Retrying to join mp3 files (may cause infinite loop)')
		x.join_files()
		#logging.info('Retry: %s' % x.retry)	

	if not x.retry:
		f = x.getfile()

	if f:
		f.author = options.author
		f.series = options.series
		f.title = options.title
		f.number = options.number

		# Rename joined file
		f.rename()
		# Tag joined file
		f.tag()
			
	else:
		# Joining was unsuccessful
		logging.info('Joining of files unsuccessful')

if __name__ == '__main__':
        main()
