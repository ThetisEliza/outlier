'''
Date: 2022-11-16 16:59:28
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 17:52:50
FilePath: /outlier/src/client.py
'''
import socket
from queue import Queue
from threading import Thread

sk = socket.socket()

def recvLoop():
    while 1:
        recv_msg = sk.recv(1024) 
        print("来自服务端的消息：", recv_msg.decode("utf-8"))


def main():
    sk.connect(("127.0.0.1", 8809)) 
    recvThread = Thread(target=recvLoop)
    recvThread.start()
    while 1:  
        send_msg = input(">>>:").strip() 
        sk.send(send_msg.encode("utf-8"))
        if send_msg.upper() == "BYE": 
            break
        
    recvThread.join()
    sk.close() 
    
if __name__ == '__main__':
    main()