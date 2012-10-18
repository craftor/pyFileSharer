
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
	
	# 记下起始时间
	startime=time.time()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	myclient = fileshare()
	
	try:
		s.connect((server_addr, server_port))
	except:
		print "1服务器无法连接"
		sys.exit()
	else:
		print "1服务器连接成功"
		Req = myclient.FRP('FR','Craftor',fn,0,0,0)
		try:
			s.sendall(Req)
		except:
			print "1文件请求失败"
			s.close()
			sys.exit()

	try:
		# 确保收到完整的协议包头
		message = s.recv(HEAD_LEN)
		while (len(message)<HEAD_LEN):
			message += s.recv(HEAD_LEN-len(message))
	except:
		print "1服务器未响应"
		s.close()
		sys.exit()
	
	# 检测协议包
	pt,pu = myclient.UnpkHead(message)

	# 文件是否存在
	if (pt=='FE'):
		fn,fl,fo,fs = myclient.UnpkFileInfo(message)
		# 创建文件句柄
		fi = open('./file/'+fn,'wb')
		FileExisted = True
		print "2文件已找到"
	elif (pt=='FN'):
		FileExisted = False
		print "2文件不存在"
		s.close()
		sys.exit()
	else:
		FileExisted = False
		print "2未知的响应"
		s.close()
		sys.exit()
	
	# 进度条
	print "3下载开始"
	pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=fl).start()

	if (FileExisted):

		FileOK = False
		
		while (FileOK==False):

			try:
				# 确保正确收到完整的协议包头
				message = s.recv(HEAD_LEN)
				while (len(message)<HEAD_LEN):
					message += s.recv(HEAD_LEN-len(message))
			except:
				print "4服务器未响应"
				s.close()
				sys.exit()
			
			# 检测协议包
			pt,pu = myclient.UnpkHead(message)

			# 文件数据
			if (pt=='FD'):
				
				fn,fl,fo,fs = myclient.UnpkFileInfo(message)
				
				offset = fo
				writesize = 0
				
				# 写入文件的偏移fo和长度fs，都是由服务器端给出的
				# 可能是一个完整的文件，也可能是文件片段
				while (offset<fs):

					if (offset+IBUFSIZE)>fs:
						writesize = fs-offset
					else:
						writesize = IBUFSIZE
					
					try:
						message = s.recv(writesize)
						# 写入真实获取到的文件数据长度
						myclient.WriteFile(message,fi,offset,len(message))
						pbar.update(offset)
						offset += len(message)
					except:
						print "5接收数据失败"
						fi.close()
						sys.exit()
				
			# 文件结束
			elif (pt=='FF'):
				pbar.finish()
				endtime = time.time()
				timeuse = endtime - startime
				print "------------------------------------------"
				print " %s 接收完成." % fn
				print " 文件大小 : %6.2f MB" % (fl/1024/1024)
				print " 下载用时 : %6.2f s" % timeuse
				print " 下载速度 : %6.2f MB/s" % (fl/1024/1024/timeuse)
				print "------------------------------------------"
				FileOK = True
				fi.close()
				s.close()

if __name__ == "__main__":
	d1 = threading.Thread(target=DownLoadFile(server_addr,server_port,'filename')).start()
