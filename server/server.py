
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

		# ���Э���
		pt,pu = mySer.UnpkHead(self.data)

		# ע������(Register Requtest)
		if (pt == 'RR'):
			#mySer.PrintDRP(pt,pl,dv,da,dp,du)
			Req = mySer.DRP('RS',pl,dv,da,dp,du)
			try:
				self.request.sendall(Req)
			except:
				print "1�ͻ���δ��Ӧ"
				self.request.close()
				raise
		
		# �ļ�����(File Request)
		elif (pt == 'FR'):

			offset = 0

			fn,fl,fo,fs = mySer.UnpkFileInfo(self.data)

			# ��fileĿ¼�²����ļ�
			fi,fl = mySer.ScanFile('./file',fn)
			
			if (fl):

				# ���߿ͻ����ļ�����
				Req = mySer.FRP('FE',pu,fn,fl,0,0)
				try:
					self.request.sendall(Req)
				except:
					print "2�ͻ���δ��Ӧ"
					self.request.close()
					raise

				# ������
				print "3�ļ����俪ʼ"
				pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=fl).start()

				# �ļ�����ͷ��
				Req = mySer.FRP('FD',pu,fn,fl,0,fl)
				try:
					self.request.sendall(Req)
				except:
					print "2�ͻ���δ��Ӧ"
					self.request.close()
					raise

				# �ļ�����
				while (offset < fl):

					# �ļ�ƫ���ж�
					if (offset+OBUFSIZE) > fl:
						Req = mySer.ReadFile(fi,offset,fl-offset)
					else:
						Req = mySer.ReadFile(fi,offset,OBUFSIZE)
						
					# ����
					try:
						self.request.sendall(Req)
					except:
						print "4�ͻ���δ��Ӧ"
						print offset
						self.request.close()
						raise	

					# ����������
					pbar.update(offset)

					# �ļ�ƫ��++
					offset += OBUFSIZE
				
				# ���߿ͻ����ļ�����
				Req = mySer.FRP('FF',pu,fn,fl,0,0)
				try:
					self.request.sendall(Req)
				except:
					print "2�ͻ���δ��Ӧ"
					self.request.close()
					raise

				pbar.finish()
				fi.close()
				print '6�ļ��������'
				
			else:

				# ���߿ͻ����ļ�������
				Req = mySer.FRP('FN',pu,fn,fl,offset,0)
				try:
					self.request.sendall(Req)
				except:
					print "�ͻ���δ��Ӧ"
					self.request.close()
					raise


if __name__ == "__main__":
	s1 = SocketServer.TCPServer((server_addr,server_port), MyServer)
	s1.serve_forever()