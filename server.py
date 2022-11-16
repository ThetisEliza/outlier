'''
Date: 2022-11-16 16:49:18
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-16 19:36:06
FilePath: /py-outlier/server.py
'''

import socket 
from threading import Thread
from time import sleep
from queue import Queue

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
        if errorTime >= 3:
            break
        try:
            if (recv()): break
            errorTime = 0
        except:
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
    
    sk.bind(("127.0.0.1", 2702))
    sk.listen()

    
    print(cm)
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
    
    
# while 1:
#     seng_msg = input(">>>:").strip()
#     conn.send(seng_msg.encode("utf-8"))
#     if seng_msg.upper() == "BYE":
#         break
    # recv_msg = conn.recv(1024)
#     print("from client", recv_msg.decode('utf-8'))
#     if recv_msg.decode('utf-8').upper() == "BYE":
#         break
# conn.close()
# sk.close()

if __name__ == '__main__':
    main()
        