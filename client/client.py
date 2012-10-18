
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
	
	# ������ʼʱ��
	startime=time.time()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	myclient = fileshare()
	
	try:
		s.connect((server_addr, server_port))
	except:
		print "1�������޷�����"
		sys.exit()
	else:
		print "1���������ӳɹ�"
		Req = myclient.FRP('FR','Craftor',fn,0,0,0)
		try:
			s.sendall(Req)
		except:
			print "1�ļ�����ʧ��"
			s.close()
			sys.exit()

	try:
		# ȷ���յ�������Э���ͷ
		message = s.recv(HEAD_LEN)
		while (len(message)<HEAD_LEN):
			message += s.recv(HEAD_LEN-len(message))
	except:
		print "1������δ��Ӧ"
		s.close()
		sys.exit()
	
	# ���Э���
	pt,pu = myclient.UnpkHead(message)

	# �ļ��Ƿ����
	if (pt=='FE'):
		fn,fl,fo,fs = myclient.UnpkFileInfo(message)
		# �����ļ����
		fi = open('./file/'+fn,'wb')
		FileExisted = True
		print "2�ļ����ҵ�"
	elif (pt=='FN'):
		FileExisted = False
		print "2�ļ�������"
		s.close()
		sys.exit()
	else:
		FileExisted = False
		print "2δ֪����Ӧ"
		s.close()
		sys.exit()
	
	# ������
	print "3���ؿ�ʼ"
	pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=fl).start()

	if (FileExisted):

		FileOK = False
		
		while (FileOK==False):

			try:
				# ȷ����ȷ�յ�������Э���ͷ
				message = s.recv(HEAD_LEN)
				while (len(message)<HEAD_LEN):
					message += s.recv(HEAD_LEN-len(message))
			except:
				print "4������δ��Ӧ"
				s.close()
				sys.exit()
			
			# ���Э���
			pt,pu = myclient.UnpkHead(message)

			# �ļ�����
			if (pt=='FD'):
				
				fn,fl,fo,fs = myclient.UnpkFileInfo(message)
				
				offset = fo
				writesize = 0
				
				# д���ļ���ƫ��fo�ͳ���fs�������ɷ������˸�����
				# ������һ���������ļ���Ҳ�������ļ�Ƭ��
				while (offset<fs):

					if (offset+IBUFSIZE)>fs:
						writesize = fs-offset
					else:
						writesize = IBUFSIZE
					
					try:
						message = s.recv(writesize)
						# д����ʵ��ȡ�����ļ����ݳ���
						myclient.WriteFile(message,fi,offset,len(message))
						pbar.update(offset)
						offset += len(message)
					except:
						print "5��������ʧ��"
						fi.close()
						sys.exit()
				
			# �ļ�����
			elif (pt=='FF'):
				pbar.finish()
				endtime = time.time()
				timeuse = endtime - startime
				print "------------------------------------------"
				print " %s �������." % fn
				print " �ļ���С : %6.2f MB" % (fl/1024/1024)
				print " ������ʱ : %6.2f s" % timeuse
				print " �����ٶ� : %6.2f MB/s" % (fl/1024/1024/timeuse)
				print "------------------------------------------"
				FileOK = True
				fi.close()
				s.close()

if __name__ == "__main__":
	d1 = threading.Thread(target=DownLoadFile(server_addr,server_port,'filename')).start()
