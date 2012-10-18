
# coding=utf-8

__version__ = 20120427

import sys,os
import socket, traceback

# Server Information
server_addr = '192.168.0.131'
server_port = 50000

# Head Length
HEAD_LEN = 128

# Buffer Size
OBUFSIZE = 1024*8
IBUFSIZE = 1024*4

PI = '1987'
PT = {'UN':'Unknow Package',
	  'RR':'Register Requrest ',
      'RS':'Register Success ',
	  'SC':'Status Check ',
	  'FQ':'File Query',       # 客户端向服务器查询文件
	  'FE':'File Existed',     # 服务器端文件存在
	  'FN':'File Not Existed', # 服务器端文件不存在
	  'FT':'File Transmit',    # 客户端请求文件传输
	  'FD':'File Data',        # 服务器返回文件数据
	  'FF':'File Finish'}

class fileshare(object):

	def __init__(self):
		pass

	def int2hex(self, num, w):
		s = ''
		for i in range(0, w, 1):
			tmp = num%256
			s += chr(tmp)
			num = num/256
		return s
	
	def hex2int(self, num):
		result = 0
		base = 1
		for i in range(0, len(num), 1):
			result += ord(num[i])*base
			base *= 256
		return result

	# 包头
	def PkgHead(self, pt, pu):
		Req  = PI                 # 包标识
		Req += pt                 # 包类型
		Req += self.int2hex(len(pu),1)  # 用户名长度
		Req += pu                       # 用户名
		for i in range(0, 15-len(pu), 1):
			Req += '\x00'
		Req += self.int2hex(0,10) #保留
		return Req
	
	# 解包头
	def UnpkHead(self, message):
		pt = message[4:6]
		n = self.hex2int(message[6])
		pu = message[7:7+n]
		return pt, pu
	
	# 文件信息
	def FileInfo(self, fn, fl, fo, fs):
		
		# 文件名
		Req = self.int2hex(len(fn),1)
		Req += fn
		for i in range(0,63-len(fn),1):
			Req += '\x00'

		# 文件长度
		Req += self.int2hex(fl,8)

		# 请求偏移
		Req += self.int2hex(fo,8)

		# 请求长度
		Req += self.int2hex(fs, 8)

		# 保留
		Req += self.int2hex(0,8)

		return Req
	
	# 解文件信息
	def UnpkFileInfo(self, message):
		offset=32
		# 文件名
		n = self.hex2int(message[offset])
		fn = message[offset+1:offset+1+n]
		# 文件长度
		fl = self.hex2int(message[offset+64:offset+72])
		# 请求偏移
		fo = self.hex2int(message[offset+72:offset+80])
		# 请求长度
		fs = self.hex2int(message[offset+80:offset+88])
		return fn,fl,fo,fs
	
	# 读文件
	def ReadFile(self, fi, fo, fs):
		fi.seek(fo)
		return fi.read(fs)
	
	# 写文件
	def WriteFile(self, message, fi, fo, fs):
		try:
			WriteData = message[0:fs]
		except:
			print "Missing File Data."
			return False
		else:
			try:
				fi.seek(fo)
				fi.write(WriteData)
			except:
				print "Write File Error."
				return False
			else:
				return True
	
	# 文件请求包头
	def FRP(self, pt, pu, fn, fl, fo, fs):
		return self.PkgHead(pt,pu)+ self.FileInfo(fn,fl,fo,fs)

	# 带数据的文件包头
	def FDP(self, pt, pu, fn, fl, fo, fs, fi):
		Req = self.LoadFileData(fi,fo,fs)
		return self.FRP(pt,pu,fn,fl,fo,fs) + Req

	# 扫描文件，并打开
	def ScanFile(self,path,fn):
		fi = ''
		fl = 0
		for filelist in os.listdir(path):
			if fn == filelist :
				fnn = path+'/'+fn
				try:
					fi = open(fnn, 'rb')
				except:
					fl = 0
					raise
				else:
					fl = os.path.getsize(fnn)
		return fi, fl
	
	# 检查文件是否存在
	def FileExisted(self,path,fn):
		Existed = False
		for filelist in os.listdir(path):
			if fn == filelist :
				Existed = True
		return Existed
	
	# 打印包头信息
	def PrintFRP(self,pt,pu,fn,fl,fo,fs):
		print "----------------------------------"
		print " Craftor's File Sharing  package  "
		print "----------------------------------"
		print "Pkg  Type : %s - %s " %( pt, PT[pt])
		print "     User : %s" % pu
		print "File Name : %s" % fn
		print "File Len  : %d" % fl
		print "   Offset : %d" % fo
		print "     Size : %d" % fs
		print "----------------------------------"