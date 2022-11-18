'''
Date: 2022-11-16 16:49:18
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-16 19:36:06
FilePath: /py-outlier/server.py

I found `python` is really hard to write a project. It's too flexiable to organize the structure ...
'''

import socket 
import json
import logging
from threading import Thread
from time import sleep
from queue import Queue


PROJ_PATH = ""

class Config:
    def __init__(self):
        with open(PROJ_PATH+"config/config.json") as f:
            self.__dict__.update(json.load(f))


'''
The Encryptor algorithm. there might be a huge amout of mature algorithms, but 
we still could consider a new method to encrypt the communication in case of
any vulnerable situation
'''
class Encryptor:
    ...
    
 
    
'''
We can use this class to manage chat status, maybe release some unused channel,
saving or loading chat history and something else.
'''
class ChatManager:
    ...


class CommManager:
    def __init__(self) -> None:
        self.historyQueue = []
        self.connects = []
        self.msgQueue = Queue()    
        
cm = CommManager()   

def commuLoop(conn):
    
    def recv():
        print("waiting for recv...")
        data = conn.recv(1024)
        if data == b"":
            return -1
        elif data:
            recvMsg = data.decode('utf-8')
            cm.msgQueue.put(recvMsg)
        return 0
        
    errorTime = 0
    while 1:
        try:
            if recv() == -1 or erroTime >= 3: 
                break
            errorTime = 0
        except:
            sleep(1)
            print(f"Reconnecting .. {errorTime}")
            errorTime += 1
    print("connection closed")
    conn.close()
    if conn in cm.connects:
        cm.connects.remove(conn)

def sendLoop():
    while 1:
        while (not cm.msgQueue.empty()):
            msg = cm.msgQueue.get()
            print(f"send msg {msg} to {cm.connects}")
            for c in cm.connects:
                c.send(msg.encode("utf-8"))
        sleep(0.5)

def main():
    print('start.')
    sk = socket.socket()
    
    sk.bind(("10.0.4.2", 8809))
    sk.listen()

    threads = []
    Thread(target=sendLoop, args=()).start()
    while 1:
        print('waiting for conn')
        conn, address = sk.accept()
        cm.connects.append(conn)  
        t = Thread(target=commuLoop, args=(conn,))
        t.start()
        threads.append(t)
    
    print("end.")
    
def fn():
    print('hello')

if __name__ == '__main__':
    # main()
    # 
    FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
    logging.basicConfig(format=FORMAT)
    d = {'clientip': '192.168.0.1', 'user': 'fbloggs'}
    logging.getLogger("server").warning("watch  out", extra=d)
    
    
    