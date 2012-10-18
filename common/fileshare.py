
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
	  'FQ':'File Query',       # �ͻ������������ѯ�ļ�
	  'FE':'File Existed',     # ���������ļ�����
	  'FN':'File Not Existed', # ���������ļ�������
	  'FT':'File Transmit',    # �ͻ��������ļ�����
	  'FD':'File Data',        # �����������ļ�����
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

	# ��ͷ
	def PkgHead(self, pt, pu):
		Req  = PI                 # ����ʶ
		Req += pt                 # ������
		Req += self.int2hex(len(pu),1)  # �û�������
		Req += pu                       # �û���
		for i in range(0, 15-len(pu), 1):
			Req += '\x00'
		Req += self.int2hex(0,10) #����
		return Req
	
	# ���ͷ
	def UnpkHead(self, message):
		pt = message[4:6]
		n = self.hex2int(message[6])
		pu = message[7:7+n]
		return pt, pu
	
	# �ļ���Ϣ
	def FileInfo(self, fn, fl, fo, fs):
		
		# �ļ���
		Req = self.int2hex(len(fn),1)
		Req += fn
		for i in range(0,63-len(fn),1):
			Req += '\x00'

		# �ļ�����
		Req += self.int2hex(fl,8)

		# ����ƫ��
		Req += self.int2hex(fo,8)

		# ���󳤶�
		Req += self.int2hex(fs, 8)

		# ����
		Req += self.int2hex(0,8)

		return Req
	
	# ���ļ���Ϣ
	def UnpkFileInfo(self, message):
		offset=32
		# �ļ���
		n = self.hex2int(message[offset])
		fn = message[offset+1:offset+1+n]
		# �ļ�����
		fl = self.hex2int(message[offset+64:offset+72])
		# ����ƫ��
		fo = self.hex2int(message[offset+72:offset+80])
		# ���󳤶�
		fs = self.hex2int(message[offset+80:offset+88])
		return fn,fl,fo,fs
	
	# ���ļ�
	def ReadFile(self, fi, fo, fs):
		fi.seek(fo)
		return fi.read(fs)
	
	# д�ļ�
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
	
	# �ļ������ͷ
	def FRP(self, pt, pu, fn, fl, fo, fs):
		return self.PkgHead(pt,pu)+ self.FileInfo(fn,fl,fo,fs)

	# �����ݵ��ļ���ͷ
	def FDP(self, pt, pu, fn, fl, fo, fs, fi):
		Req = self.LoadFileData(fi,fo,fs)
		return self.FRP(pt,pu,fn,fl,fo,fs) + Req

	# ɨ���ļ�������
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
	
	# ����ļ��Ƿ����
	def FileExisted(self,path,fn):
		Existed = False
		for filelist in os.listdir(path):
			if fn == filelist :
				Existed = True
		return Existed
	
	# ��ӡ��ͷ��Ϣ
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