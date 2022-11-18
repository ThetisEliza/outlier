'''
Date: 2022-11-18 13:44:35
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 18:58:28
FilePath: /outlier/src/manager.py
'''
import socket
import json
from threading import Thread
from time import sleep
from queue import Queue
import sys
import os



PROJ_PATH = ""

class Config:
    """
    config class
    """    
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
     


    
class Client:
    def __init__(self, conn, addr, putmsgrecall, notifyrecalls) -> None:
        self._conn = conn
        self._connthread = Thread(target=self._connLoop, args=(putmsgrecall, notifyrecalls,))
        self._activate()
        
        ...
    
    def _recv(self):
        data = self._conn.recv(1024)
        if data == b"":
            return (None, -1)
        elif data is None:
            return (None, -2)
        else:
            recvmsg = data.decode('utf-8')
            return (recvmsg, 0)
        
    def _connLoop(self, putmsgrecall, notifyrecalls):
        """
        This is the loop for client to maintain the connection.
        """
        errortime = 0
        while True:
            try:
                res, status = self._recv()
                if status == -1 or errortime > 3:
                    break
                putmsgrecall(res)
            except:
                sleep(1)
                errortime += 1
                
        notifyrecalls(self)
        self._deactivate()
            

    def _activate(self):
        self._connthread.start()
        
        
    def _deactivate(self):
        ...
        self._conn.close()
        
        
        
    def send(self, msg):
        self._conn.send(msg.encode("utf-8"))
    


'''
We can use this class to manage chat status, maybe release some unused channel,
saving or loading chat history and something else.
'''
class ChatManager:
    def __init__(self) -> None:       
        
        self.history    = []
        self.connects   = []
        
        
        
        # todo
        # self.channels   = []
        
        
        
    
        
        
    def _broadcastLoop(self):
        """
        This is a loop to broad cast all connected client. May be we could differentiate
        some channels later, and this should be move to a more abstractive channel class
        """
        ...
        
        

class ServerManager:
    def __init__(self, conf) -> None:
        self._conf   = conf
        self._sock   = socket.socket()
        self._stop   = False
        self._conns  = []
        self.syncqueue  = Queue()
        
        
    def start(self):
        self._listenLoop()
        
    
    def end(self):
        
        self._stop   = True
        self._sock.close()
        
    
    def _listenLoop(self):
        """
        This is a listen loop for accept new connections
        """
        self._sock.bind((self._conf.ip, self._conf.port))
        self._sock.listen()
        
        broadthread = Thread(target=self._broadcastLoop)
        broadthread.start()
        
        while not self._stop:
            print("waiting for connection")
            conn, addr = self._sock.accept()
            client = Client(conn, addr, self._putmsg, self._elimateconn)
            self._conns.append(client)
                        
        broadthread.join()
    
    
    def _putmsg(self, msg):
        self.syncqueue.put(msg)
            
    def _elimateconn(self, client):
        if client in self._conns:
            self._conns.remove(client)
    
    
        
    def _broadcastLoop(self):
        while not self._stop:
            while not self.syncqueue.empty():
                msg = self.syncqueue.get()
                for client in self._conns:
                    client.send(msg)
        
            

        
        
        
    