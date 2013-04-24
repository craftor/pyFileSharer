
#coding: utf-8

import sys,os
import socket, traceback
import threading
import SocketServer

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
                        FileTransferSpeed, FormatLabel, Percentage, \
                        ProgressBar, ReverseBar, RotatingMarker, \
                        SimpleProgress, Timer

sys.path.append('../common')
from fileshare import *

mySer = fileshare()

print "Listening on " , server_addr, server_port

class MyServer(SocketServer.BaseRequestHandler):
	'''
	File Sharing Server Demo
	'''
	def handle(self):

		self.data = self.request.recv(HEAD_LEN).strip()

		# Check the Package Head
		pt,pu = mySer.UnpkHead(self.data)

		# (Registering Requtest)
		if (pt == 'RR'):
			#mySer.PrintDRP(pt,pl,dv,da,dp,du)
			Req = mySer.DRP('RS',pl,dv,da,dp,du)
			try:
				self.request.sendall(Req)
			except:
				print "Client no response"
				self.request.close()
				raise
		
		# (File Request)
		elif (pt == 'FR'):

			offset = 0

			fn,fl,fo,fs = mySer.UnpkFileInfo(self.data)

			# Lookup for the file
			fi,fl = mySer.ScanFile('./file',fn)
			
			if (fl):

				# File Exist
				Req = mySer.FRP('FE',pu,fn,fl,0,0)
				try:
					self.request.sendall(Req)
				except:
					print "Client no response"
					self.request.close()
					raise

				# Process Bar
				print "File Transfer Starting..."
				pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=fl).start()

				# File Data
				Req = mySer.FRP('FD',pu,fn,fl,0,fl)
				try:
					self.request.sendall(Req)
				except:
					print "Client no response"
					self.request.close()
					raise

				# File data
				while (offset < fl):

					# File offset
					if (offset+OBUFSIZE) > fl:
						Req = mySer.ReadFile(fi,offset,fl-offset)
					else:
						Req = mySer.ReadFile(fi,offset,OBUFSIZE)
						
					# Send file data
					try:
						self.request.sendall(Req)
					except:
						print "Client no response"
						print offset
						self.request.close()
						raise	

					# Process Bar Control
					pbar.update(offset)

					# File Offset ++
					offset += OBUFSIZE
				
				# File Finished
				Req = mySer.FRP('FF',pu,fn,fl,0,0)
				try:
					self.request.sendall(Req)
				except:
					print "Client no response"
					self.request.close()
					raise

				pbar.finish()
				fi.close()
				print 'File transfer finished.'
				
			else:

				# File Not exist
				Req = mySer.FRP('FN',pu,fn,fl,offset,0)
				try:
					self.request.sendall(Req)
				except:
					print "Client no response"
					self.request.close()
					raise


if __name__ == "__main__":
	s1 = SocketServer.TCPServer((server_addr,server_port), MyServer)
	s1.serve_forever()
