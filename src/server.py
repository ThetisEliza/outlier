'''
Date: 2022-11-16 16:49:18
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 18:47:27
FilePath: /outlier/src/server.py

I found `python` is really hard to write a project. It's too flexiable to organize the structure ...
'''

import socket
from threading import Thread
import time
import logging
from queue import Queue
from argparse import ArgumentParser
from typing import List


from manager import Config
from protocol import Package, Command, Message

import utils


    


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
        
        self._stop  = True
        self._sock.close()
        
    
    def _listenLoop(self):
        """
        This is a listen loop for accept new connections
        """
        logging.info(f"start bind on {self._conf.ip}, {self._conf.port}")
        
        self._sock.bind((self._conf.ip, self._conf.port))
        self._sock.listen()
        
        while not self._stop:
            logging.info("waiting for connection")
            conn, addr = self._sock.accept()
            self._conns.append(ClientConn(conn, addr, self._bc))

    def _elimateconn(self, client):
        if client in self._conns:
            self._conns.remove(client)
        

class Broadcaster:
    def __init__(self, conns) -> None:
        self._stop = False
        self.syncqueue  = Queue()
        self.allhistory: List[Message] = []
        self.broadthread = Thread(target=self._broadcastLoop, args=(conns,))
        self.broadthread.start()
        
        
        
    def putmsg(self, msg):
        logging.info(f"collect message {msg}")
        self.syncqueue.put(msg)
        self.allhistory.append(msg)
        
    def syncmsg(self, timestamp, name, conn):
        logging.info(f"syncmsg message {timestamp} {name}")
        msgbuffer: List[Message] = []
        for msg in self.allhistory:
            if msg.timestamp > timestamp:
                msgbuffer.append(msg)
        flow = Package.buildpackage().add_field("sync", list(map(lambda x:x.jsonallize(), msgbuffer))).tobyteflow()
        conn.send(flow)
        
        
    def _broadcastLoop(self, conns):
        """
        This is a loop to broad cast all connected client. May be we could differentiate
        some channels later, and this should be move to a more abstractive channel class
        """
        while not self._stop:
            while self.syncqueue.empty():
                time.sleep(0.1)                
            msg = self.syncqueue.get()
            flow = Package.buildpackage().add_field("sync", [msg.jsonallize()]).tobyteflow()
            for client in conns:
                client.send(flow)


class ClientConn:
    def __init__(self, conn, addr, broadcaster:Broadcaster) -> None:
        self._conn = conn
        self._broadcaster = broadcaster
        self._connthread = Thread(target=self._connLoop, args=(self._broadcaster,))
        self._activate()
        
    
    def _recv(self):
        data = self._conn.recv(1024)
        logging.info(f"recv message {data}")
        if data == b"":
            return None, -1
        elif data is None:
            return None, -2
        else:
            return data, 0
        
        
    def _connLoop(self, broadcaster: Broadcaster):
        """
        This is the loop for client to maintain the connection.
        """
        errortime = 0
        while True:
            try:
                logging.info(f"prepare to receive , time {errortime}")
                if errortime > 3:
                    break
                res, status = self._recv()
                res = Package.parsebyteflow(res)
                logging.info(f"receiving finished res: {res} status: {status}")
                if status == -1:
                    logging.info(f"remote conn closed: {self._conn}")
                    break
                
                if "msg" in res.get_data():
                    broadcaster.putmsg(Message(res.get_data().get("msg", ""), res.get_data().get("username"), res.get_data().get('timestamp')))
                
                elif "cmd" in res.get_data() and res.get_data().get('cmd', "") == Command.FETCH:
                    broadcaster.syncmsg(res.get_data().get('timestamp'), res.get_data().get('username'), self._conn)
                
                    
            except Exception as e:
                logging.warning(e)
                time.sleep(1)
                errortime += 1
                
        self._deactivate()
            

    def _activate(self):
        self._connthread.start()
        
        
    def _deactivate(self):
        self._conn.close()
        
        
        
    def send(self, msg):
        self._conn.send(msg)   

def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    args = argparse.parse_args()
    conf = Config(**{"log": args.log})
    utils.init_logger(conf.log)
    
    sm = ServerListener(conf)
    sm.start()
    

if __name__ == '__main__':
    main()
    
    