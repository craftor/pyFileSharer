
# coding=utf-8

import sys,os
import socket, traceback
import threading
import time

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
                        FileTransferSpeed, FormatLabel, Percentage, \
                        ProgressBar, ReverseBar, RotatingMarker, \
                        SimpleProgress, Timer

sys.path.append('../common')
from fileshare import *

def DownLoadFile(server_addr,server_port,fn):
	
	# Mark the start time
	startime=time.time()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	myclient = fileshare()
	
	try:
		s.connect((server_addr, server_port))
	except:
		print "Connecting to the server failed."
		sys.exit()
	else:
		print "Connecting to the server success."
		Req = myclient.FRP('FR','Craftor',fn,0,0,0)
		try:
			s.sendall(Req)
		except:
			print "File Request failed."
			s.close()
			sys.exit()

	try:
		# Make Sure get the full protocol head
		message = s.recv(HEAD_LEN)
		while (len(message)<HEAD_LEN):
			message += s.recv(HEAD_LEN-len(message))
	except:
		print "Failed to get full protocol head"
		s.close()
		sys.exit()
	
	# Check the Protocol Head
	pt,pu = myclient.UnpkHead(message)

	# File Exist
	if (pt=='FE'):
		fn,fl,fo,fs = myclient.UnpkFileInfo(message)
		# Handle the file
		fi = open('./file/'+fn,'wb')
		FileExisted = True
		print "File found."
	elif (pt=='FN'):
		FileExisted = False
		print "File not found."
		s.close()
		sys.exit()
	else:
		FileExisted = False
		print "No reponse"
		s.close()
		sys.exit()
	
	# Process Bar
	print "Downloading..."
	pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=fl).start()

	if (FileExisted):

		FileOK = False
		
		while (FileOK==False):

			try:
				# Get full protocol head
				message = s.recv(HEAD_LEN)
				while (len(message)<HEAD_LEN):
					message += s.recv(HEAD_LEN-len(message))
			except:
				print "Failed to get full protocol head"
				s.close()
				sys.exit()
			
			# Check the head
			pt,pu = myclient.UnpkHead(message)

			# File Data
			if (pt=='FD'):
				
				fn,fl,fo,fs = myclient.UnpkFileInfo(message)
				
				offset = fo
				writesize = 0
				
				# fo,fs are get from Sever, maybe full or part of a file
				while (offset<fs):

					if (offset+IBUFSIZE)>fs:
						writesize = fs-offset
					else:
						writesize = IBUFSIZE
					
					try:
						message = s.recv(writesize)
						# Write data
						myclient.WriteFile(message,fi,offset,len(message))
						pbar.update(offset)
						offset += len(message)
					except:
						print "Failed on receiving file."
						fi.close()
						sys.exit()
				
			# File Finish
			elif (pt=='FF'):
				pbar.finish()
				endtime = time.time()
				timeuse = endtime - startime
				print "------------------------------------------"
				print " %s Downloading Finished." % fn
				print " File Size : %6.2f MB" % (fl/1024/1024)
				print " Time Use  : %6.2f s" % timeuse
				print " Speed     : %6.2f MB/s" % (fl/1024/1024/timeuse)
				print "------------------------------------------"
				FileOK = True
				fi.close()
				s.close()

if __name__ == "__main__":
	d1 = threading.Thread(target=DownLoadFile(server_addr,server_port,'test')).start()
