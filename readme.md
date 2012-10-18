## 项目说明

利用Python学习TCP协议，做了一个简单的主、从模式的文件传输。

## 说明

./doc 文档，协议

./common 服务端和客户端共用的库

./server 服务端

./client 客户端

## 测试步骤：

1. 安装tools目录下的setuptools和processbar
	1）运行setuptools.exe
	2）解压processbar，运行setup.py install

3. 运行 server\server.py

4. 在 server\file 中放入待测试传输的文件(已经放入test文件)

5. 修改 client\client.py中的最后一行文件名为第3步中的文件名(原文件名为test)

6. 运行 client.py
