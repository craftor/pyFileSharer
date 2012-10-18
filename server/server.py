
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
		
		# �ļ���ѯ
		if self.pt=='FQ':
			
			# ��fileĿ¼�²����ļ�
			if (self.fs.FileExisted(file_dir,fn)):
				Req = self.fs.FRP('FE',self.pu,self.fn,self.fl,0,0)
			else:
				Req = self.fs.FRP('FN',self.pu,self.fn,self.fl,0,0)
		
		# �ļ���������
		elif self.pt=='FR':
			
			# ɨ���ļ�
			self.fi,self.fl = self.fs.ScanFile(file_dir,self.fn)
			
			if (self.fl):
				# �ļ�Э���ͷ
				Req = self.fs.FRP('FD',self.pu,self.fn,self.fl,self.fo,self.fs)
				# �ļ�����
				Req += self.fs.ReadFile(self.fi,self.fo,self.fs)
			else:
				Req = self.fs.FRP('FN',self.pu,self.fn,self.fl,0,0)
		
		# ����Э���
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
			# ���Э���
			self.pt, self.pu = self.fs.UnpkHead(message)
			self.fn, self.fl, self.fo, self.fs = self.fs.UnpkFileInfo(message)
			# ����
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


def main():
    server_listen()

if __name__ == "__main__":
	main()