'''
Date: 2022-11-16 16:49:18
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 18:47:27
FilePath: /outlier/src/server.py

I found `python` is really hard to write a project. It's too flexiable to organize the structure ...
'''
import socket
import json
from threading import Thread
import time
from queue import Queue
import sys
import os

from manager import Config
from protocol import Package        
    
class ClientConn:
    def __init__(self, conn, addr, putmsgrecall, notifyrecalls) -> None:
        self._conn = conn
        self._connthread = Thread(target=self._connLoop, args=(putmsgrecall, notifyrecalls,))
        self._activate()
        
    
    def _recv(self):
        data = self._conn.recv(1024)
        print(f"recv message {data}")
        if data == b"":
            return None, -1
        elif data is None:
            return None, -2
        else:
            return data, 0
        
    def _connLoop(self, putmsgrecall, notifyrecalls):
        """
        This is the loop for client to maintain the connection.
        """
        errortime = 0
        while True:
            try:
                print(f"prepare to receive , errtime {errortime}")
                if errortime > 3:
                    break
                res, status = self._recv()
                print(f"receiving finished res: {res} status: {status}")
                print(f"receiving finished res: {Package.parsebyteflow(res)} status: {status}")
                if status == -1:
                    print(f"remote conn closed: {self._conn}")
                    break
                putmsgrecall(res)
            except Exception as e:
                print(e)
                time.sleep(1)
                errortime += 1
                
        notifyrecalls(self)
        self._deactivate()
            

    def _activate(self):
        self._connthread.start()
        
        
    def _deactivate(self):
        self._conn.close()
        
        
        
    def send(self, msg):
        self._conn.send(msg)
    


'''
We can use this class to manage chat status, maybe release some unused channel,
saving or loading chat history and something else.
'''
class ChatManager:
    def __init__(self) -> None:
        self.history    = []
        self.connects   = []



'''
I guess we should try a more specific pattern where an individual listener should
be departed from server
'''
class ServerListener:
    def __init__(self, conf) -> None:
        self._conf   = conf
        self._sock   = socket.socket()
        self._stop   = False
        self._conns  = []
        self._bc     = Broadcaster(self._conns)

    def start(self):
        self._listenLoop()
        
    
    def end(self):
        
        self._stop   = True
        self._sock.close()
        
    
    def _listenLoop(self):
        """
        This is a listen loop for accept new connections
        """
        print(f"start bind on {self._conf.ip}, {self._conf.port}")
        self._sock.bind((self._conf.ip, self._conf.port))
        self._sock.listen()
        
        while not self._stop:
            print("waiting for connection")
            conn, addr = self._sock.accept()
            self._conns.append(ClientConn(conn, addr, self._bc._putmsg, self._elimateconn))

    def _elimateconn(self, client):
        if client in self._conns:
            self._conns.remove(client)
        

class Broadcaster:
    def __init__(self, conns) -> None:
        self._stop = False
        self.syncqueue  = Queue()
        self.broadthread = Thread(target=self._broadcastLoop, args=(conns,))
        self.broadthread.start()
        
        
    def _putmsg(self, msg):
        self.syncqueue.put(msg)
        
        
    def _broadcastLoop(self, conns):
        """
        This is a loop to broad cast all connected client. May be we could differentiate
        some channels later, and this should be move to a more abstractive channel class
        """
        while not self._stop:
            while self.syncqueue.empty():
                time.sleep(0.1)
                
            
            msg = self.syncqueue.get()
            print(f"broadcast msg {msg}")
            package = Package.parsebyteflow(msg)
            print(f"broadcast msg {package}")
            for client in conns:
                client.send(msg)
        
            

        
        
        
    

conf = Config()

def main():
    sm = ServerListener(conf)
    sm.start()
    

if __name__ == '__main__':
    main()
    
    