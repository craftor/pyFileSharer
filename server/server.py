
#coding: utf-8

import sys,os
import socket, traceback
import threading
import SocketServer

sys.path.append('../common')
from fileshare import *

server_ip = '192.168.0.131'
server_port = 50000
conn_list = []
file_dir = './file'

class FileServer(threading.Thread):
	
	def __init__(self, fd):
		threading.Thread.__init__(self)
		self.fd = fd
		self.fs = fileshare()
	
	def process(self):
		
		Req = ''
		
		# 文件查询
		if self.pt=='FQ':
			
			# 在file目录下查找文件
			if (self.fs.FileExisted(file_dir,fn)):
				Req = self.fs.FRP('FE',self.pu,self.fn,self.fl,0,0)
			else:
				Req = self.fs.FRP('FN',self.pu,self.fn,self.fl,0,0)
		
		# 文件传输请求
		elif self.pt=='FR':
			
			# 扫描文件
			self.fi,self.fl = self.fs.ScanFile(file_dir,self.fn)
			
			if (self.fl):
				# 文件协议包头
				Req = self.fs.FRP('FD',self.pu,self.fn,self.fl,self.fo,self.fs)
				# 文件数据
				Req += self.fs.ReadFile(self.fi,self.fo,self.fs)
			else:
				Req = self.fs.FRP('FN',self.pu,self.fn,self.fl,0,0)
		
		# 发送协议包
		try:
			self.fd.sendall(Req)
		except:
			print "Error 2"
			raise
	
	def run(self):
		message = ''
		try:
			while (len(message)<HEAD_LEN):
				message = self.fd.recv(HEAD_LEN-len(message))
		except:
			print 'Error 1'
			raise
		else:
			# 检测协议包
			self.pt, self.pu = self.fs.UnpkHead(message)
			self.fn, self.fl, self.fo, self.fs = self.fs.UnpkFileInfo(message)
			# 处理
			self.process()

def server_listen():
	global conn_list
	listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_fd.bind((server_ip, server_port))
	listen_fd.listen(1024)
	conn_lock = threading.Lock()
	print "File Server is listening on ", server_ip + ":" + str(server_port)

	while True:
		conn_fd, remote_addr = listen_fd.accept()
		print "connection from ", remote_addr, "conn_list", len(conn_list)
		conn = FileServer(conn_fd)
		conn.start()
		conn_lock.acquire()
		conn_list.append(conn)
		# check timeout
		try:
			curr_time = time.time()
			for conn in conn_list:
				if int(curr_time - conn.alive_time) > conn_timeout:
					if conn.running == True:
						conn.fd.shutdown(socket.SHUT_RDWR)
					conn.running = False
			conn_list = [conn for conn in conn_list if conn.running]
		except:
			print sys.exc_info()
		conn_lock.release()

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


def main():
    server_listen()

if __name__ == "__main__":
	main()