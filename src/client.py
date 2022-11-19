'''
Date: 2022-11-16 16:59:28
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 17:52:50
FilePath: /outlier/src/client.py
'''
import socket
from queue import Queue
from threading import Thread
from manager import Config

class Client:
    def __init__(self, conf):
        self._sk = socket.socket()
        self._sk.connect((conf.ip, conf.port)) 
        
        recvThread = Thread(target=self._recvLoop)
        recvThread.start()
        self._interactloop()
        recvThread.join()
        
        self._sk.close()

    def _recvLoop(self):
        while 1:
            recv_msg = self._sk.recv(1024)
            print("Message from the server:", recv_msg.decode("utf-8"))
            
    def _interactloop(self):
        while 1:  
            send_msg = input(">>>:").strip() 
            self._sk.send(send_msg.encode("utf-8"))
            if send_msg.upper() == "BYE": 
                break


def main():
    conf = Config()
    Client(conf)
    

    
if __name__ == '__main__':
    main()