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

import traceback

from manager import Config
from protocol import Package, Command, Message

import utils


'''
Chat room
'''
class ChatRoom:
    def __init__(self, name) -> None:
        self.history    = []
        self.connects   = []
        self._bc        = Broadcaster(self.connects)
        self._passwd    = None
        self._name      = str(name)
    
    @staticmethod
    def create(conn, name=None, passwd=None):
        cm = ChatRoom(name)
        cm._passwd = passwd
        cm.enterconn(conn)
        return cm
    
    def enterconn(self, conn):
        self.connects.append(conn)
        conn._chatroom = self
    
    def leaveconn(self, conn):
        if conn in self.connects:
            self.connects.remove(conn)
            conn._chatroom = None
        
    def __repr__(self) -> str:
        l = ("PSWD" if self._passwd else "FREE")
        return f"{'room:'+str(self._name):10}\t{l}\t{len(self.connects)}\t{len(self.history)}"
    
    @staticmethod
    def header():
        return f"{'name':10}\t{'LOCK'}\tpeople\tmsg"
        

'''
We can use this class to manage chat status, maybe release some unused channel,
saving or loading chat history and something else.
'''
class Manager:
    instance = None
    
    def __init__(self) -> None:
        self.allconnects: List[ClientConn]          = []
        self.rooms      : List[ChatRoom]            = []
    
    
    @staticmethod
    def getinstance():
        if Manager.instance is None:
            Manager.instance = Manager()
        return Manager.instance
    
    @staticmethod
    def getinstanceTest():
        if Manager.instance is None:
            Manager.instance = Manager()
            Manager.instance.rooms.append(ChatRoom(1))
            Manager.instance.rooms.append(ChatRoom(2))
            Manager.instance.rooms.append(ChatRoom(3))
        return Manager.instance
    
    def getroom(self, name) -> ChatRoom:
        for room in self.rooms:
            if room._name == name:
                return room
        return  None
    
    def getatroom(self, conn):
        return conn._chatroom
        
    def getconnects(self, room: ChatRoom):
        return list(filter(lambda x: x._chatroom == room, self.allconnects))   
    
    def newconn(self, conn):
        self.allconnects.append(conn)
        
    def newroom(self, room):
        self.rooms.append(room)
        
    def disconn(self, conn):
        if conn in self.allconnects:
            self.allconnects.remove(conn)
        atroom = self.getatroom(conn)
        if atroom is not None:
            atroom.leaveconn(conn)

    def getinfo(self):
        ret = ""
        ret += ChatRoom.header() + "\n"
        for room in self.rooms:
            ret += room.__repr__() + "\n"
        return ret
        
'''
I guess we should try a more specific pattern where an individual listener should
be departed from server
'''
class ServerListener:
    def __init__(self, conf) -> None:
        self._conf   = conf
        self._sock   = socket.socket()
        self._stop   = False
        self._manager = Manager.getinstanceTest()
        

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
        self._sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self._sock.bind((self._conf.ip, self._conf.port))
        self._sock.listen()
        
        while not self._stop:
            logging.info("waiting for connection")
            conn, addr = self._sock.accept()
            clientconn = ClientConn(conn, addr)
            self._manager.newconn(clientconn)

        

class Broadcaster:
    def __init__(self, conns) -> None:
        self._stop = False
        self.syncqueue  = Queue()
        self.allhistory: List[Message] = []
        self.broadthread = Thread(target=self._broadcastLoop, args=(conns,))
        self.broadthread.setDaemon(True)
        self.broadthread.start()
        
        
        
    def putmsg(self, msg):
        logging.info(f"collect message {msg}")
        self.syncqueue.put(msg)
        self.allhistory.append(msg)
        
    def syncmsg(self, timestamp, name, conn):
        logging.info(f"syncmsg message {timestamp} {name}")
        msgbuffer: List[Message] = list(filter(lambda x:x.timestamp > timestamp, self.allhistory))
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
            flow = Package.buildpackage().add_field(Command.SYNC_RET, [msg.jsonallize()]).tobyteflow()
            logging.debug(f"check broadcasting client {conns}")
            for client in conns:
                client.send(flow)


class ClientConn:
    def __init__(self, conn, addr) -> None:
        self._conn = conn
        self._connthread = Thread(target=self._connLoop)
        self._connthread.setDaemon(True)
        self._activate()
        self._chatroom: ChatRoom = None
        
    
    def _recv(self):
        data = self._conn.recv(1024)
        logging.info(f"recv message {data}")
        if data == b"":
            return None, -1
        elif data is None:
            return None, -2
        else:
            return data, 0
        
        
    def _connLoop(self):
        """
        This is the loop for client to maintain the connection.
        """
        errortime = 0
        while True:
            try:
                logging.info(f"prepare to receive , time {errortime}")
                if errortime > 3:
                    break
                if self.process_package(*self._recv()) == -1:
                    break   
                errortime = 0                 
            except Exception as e:
                traceback.print_exc()
                logging.warning(e)
                time.sleep(1)
                errortime += 1                
        self._deactivate()
            

    def _activate(self):
        self._connthread.start()
        
        
    def _deactivate(self):
        self._conn.close()
        Manager.getinstance().disconn(self)
        
        
        
    def send(self, msg):
        self._conn.send(msg)
        
        
    def process_package(self, package, status):
        logging.info(f"receiving finished package: {package} status: {status}")
        package = Package.parsebyteflow(package)
        logging.debug(f"receiving finished package: {package}")
        
        if status == -1:
            logging.info(f"remote conn closed: {self._conn}")
            return -1
        
        if "msg" in package.get_data():
            self._chatroom._bc.putmsg(Message(package.get_data().get("msg", ""), package.get_data().get("username"), package.get_data().get('timestamp')))
        
        elif "cmd" in package.get_data():
            if package.get_data().get('cmd', "") == Command.SYNC:
                self._chatroom._bc.syncmsg(package.get_data().get('timestamp'), package.get_data().get('username'), self._conn)
                ...
            elif package.get_data().get('cmd', "") == Command.INFO:
                # send current info
                logging.info("Check get info")
                self.send(Package.buildpackage().add_field(Command.INFO_RET, Manager.getinstance().getinfo()).tobyteflow())
                ...
            elif package.get_data().get('cmd', "") == Command.DS:
                # send disconnect
                ...
            elif package.get_data().get('cmd', "") == Command.FETCH:
                # send fetch
                ...
            elif package.get_data().get('cmd', "") == Command.ROOM:
                # send room
                
                if 'roomname' in package.get_data():
                    username = package.get_data().get('username')
                    roomname = package.get_data().get('roomname')
                    room = Manager.getinstance().getroom(roomname)
                    if room is None:
                        self._chatroom = Manager.getinstance().newroom(ChatRoom.create(self, username))
                        logging.info(f"Created a room: {username}")    
                        self.send(Package.buildpackage().add_field(Command.ROOM_RET, "err").tobyteflow())
                    else:
                        room.enterconn(self)
                        logging.info(f"Enter the room: {room._name}")    
                        self.send(Package.buildpackage().add_field(Command.ROOM_RET, "enter").tobyteflow())
                else:
                    self._chatroom = Manager.getinstance().newroom(ChatRoom.create(self))
                    logging.info("Created a room")
                    self.send(Package.buildpackage().add_field(Command.ROOM_RET, "new").tobyteflow())

def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-lh", "--loghandler", default=None, type=str)
    args = argparse.parse_args()
    conf = Config(**{"log": args.log, "loghandler": args.loghandler})
    utils.init_logger(conf.log, filehandlename=conf.loghandler)
    
    sm = ServerListener(conf)
    sm.start()
    

if __name__ == '__main__':
    main()
    
    