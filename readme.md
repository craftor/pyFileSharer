## 说明

./doc 文档，协议

./common 服务端和客户端共用的库

./server 服务端

./client 客户端

## 测试步骤：
1、修改 common\fileshare.py中的server_addr为本地IP地址
2、运行 server\server.py
3、在   server\file 中放入待测试传输的文件
4、修改 client\client.py中的最后一行文件名为第3步中的文件名
5、运行 client.py
