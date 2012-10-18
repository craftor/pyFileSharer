
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

		# 检测协议包
		pt,pu = mySer.UnpkHead(self.data)

		# 注册请求(Register Requtest)
		if (pt == 'RR'):
			#mySer.PrintDRP(pt,pl,dv,da,dp,du)
			Req = mySer.DRP('RS',pl,dv,da,dp,du)
			try:
				self.request.sendall(Req)
			except:
				print "1客户端未响应"
				self.request.close()
				raise
		
		# 文件请求(File Request)
		elif (pt == 'FR'):

			offset = 0

			fn,fl,fo,fs = mySer.UnpkFileInfo(self.data)

			# 在file目录下查找文件
			fi,fl = mySer.ScanFile('./file',fn)
			
			if (fl):

				# 告诉客户端文件存在
				Req = mySer.FRP('FE',pu,fn,fl,0,0)
				try:
					self.request.sendall(Req)
				except:
					print "2客户端未响应"
					self.request.close()
					raise

				# 进度条
				print "3文件传输开始"
				pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=fl).start()

				# 文件数据头部
				Req = mySer.FRP('FD',pu,fn,fl,0,fl)
				try:
					self.request.sendall(Req)
				except:
					print "2客户端未响应"
					self.request.close()
					raise

				# 文件数据
				while (offset < fl):

					# 文件偏移判断
					if (offset+OBUFSIZE) > fl:
						Req = mySer.ReadFile(fi,offset,fl-offset)
					else:
						Req = mySer.ReadFile(fi,offset,OBUFSIZE)
						
					# 发送
					try:
						self.request.sendall(Req)
					except:
						print "4客户端未响应"
						print offset
						self.request.close()
						raise	

					# 进度条控制
					pbar.update(offset)

					# 文件偏移++
					offset += OBUFSIZE
				
				# 告诉客户端文件结束
				Req = mySer.FRP('FF',pu,fn,fl,0,0)
				try:
					self.request.sendall(Req)
				except:
					print "2客户端未响应"
					self.request.close()
					raise

				pbar.finish()
				fi.close()
				print '6文件传输完成'
				
			else:

				# 告诉客户端文件不存在
				Req = mySer.FRP('FN',pu,fn,fl,offset,0)
				try:
					self.request.sendall(Req)
				except:
					print "客户端未响应"
					self.request.close()
					raise


if __name__ == "__main__":
	s1 = SocketServer.TCPServer((server_addr,server_port), MyServer)
	s1.serve_forever()