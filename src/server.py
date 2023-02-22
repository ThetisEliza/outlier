'''
Date: 2022-11-16 16:49:18
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-17 17:27:59
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
from protocol import Package, Message
from regdecorator import bizFuncServerReg, ServerClassReg
from func import RegisteredFunc
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
        if conn not in self.connects:
            self.connects.append(conn)
            conn._chatroom = self
    
    def leaveconn(self, conn):
        if conn in self.connects:
            self.connects.remove(conn)
            conn._chatroom = None
        
    def __repr__(self) -> str:
        l = ("PSWD" if self._passwd else "FREE")
        return f"{'room:'+str(self._name):10}\t{l}\t{len(self.connects)}\t{len(self.history)}"
    
    @property
    def details(self) -> str:
        ret = f"Room: {self._name}\n"
        for conn in self.connects:
            ret += f"Connecting: {conn._name}\tat {conn._addr}\n"
        ret += f"room history message size: {len(self._bc.allhistory)}\n"
        return ret
    
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
        self.refresht   : Thread                    = Thread(target=self.refreshdetails)
        self.refresht.setDaemon(True)
        self.refresht.start()
    
    
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
    
    def getdetails(self):
        ret = "\nServer details:\n\n"
        ret += "- all connects:\n"
        for conn in self.allconnects:
            ret += f"\t- conn: {conn._conn} at {conn._addr}, name: {conn._name} at room {conn._chatroom}\n"
        ret += "- all rooms:\n"
        for room in self.rooms:
            ret += f"\t- room: {room.details}\n"
        return ret
            
    def refreshdetails(self):
        while True:
            logging.info(f"Routing detail check {self.getdetails()}")
            time.sleep(5)
        
        
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
        self.conns = conns
        self.allhistory: List[Message] = []

        
    def putmsg(self, msg):
        logging.debug(f"collect message {msg}")
        self.syncqueue.put(msg)
        self.allhistory.append(msg)
        
    def syncmsg(self, timestamp, name, conn):
        logging.debug(f"syncmsg message {timestamp} {name}")
        msgbuffer: List[Message] = list(filter(lambda x:x.timestamp > timestamp, self.allhistory))
        flow = Package.buildpackage().add_field("sync", list(map(lambda x:x.jsonallize(), msgbuffer))).tobyteflow()
        conn.send(flow)
        
    def getunsyncedmsg(self):
        buffer = []
        while not self.syncqueue.empty():       
            msg = self.syncqueue.get()
            buffer.append(msg)
        return buffer
            
    
    def broadcast(self, msgflow, conn=None):
        for client in self.conns:
            if conn is None or client != conn:
                client.send(msgflow)

        


@ServerClassReg
class ClientConn:
    def __init__(self, conn, addr) -> None:
        self._conn = conn
        self._addr = addr
        self._connthread = Thread(target=self._connLoop)
        self._connthread.setDaemon(True)
        self._activate()
        self._chatroom: ChatRoom = None
        self._name = None
        
    
    def _recv(self):
        logging.debug(f"{self._name} trying recv message")
        data = self._conn.recv(1024)
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
                traceback.logging.debug_exc()
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
        package = Package.parsebyteflow(package)
        if status == -1:
            
            RegisteredFunc.CEXIT.serveraction(self)
            return -1
        
        command = package.get_data().get('cmd', "")
        func = RegisteredFunc.getServerFunc(command)
        
        if func:
            logging.info(f"server func check calling {func} {package.get_data()}")
            func.serveraction(self, **package.get_data())
    
    
    
    
    # Maybe later we can use `decorator` to register server function on FUNCTIONS CONFIGURed in func.py
    # Such as `@BIZREG("INFO")`
    
    # Biz Segment
    
    @bizFuncServerReg(RegisteredFunc.INFO)
    def giveinfo(self, *args, **kwargs):
        logging.debug(args, kwargs)
        return Manager.getinstanceTest().getinfo() + f"\n At Room: {self._chatroom._name if self._chatroom else None}", None, None
    
    
    @bizFuncServerReg(RegisteredFunc.ROOM)
    def changeroom(self, **kwargs):
        logging.debug("args:", kwargs)
        username = kwargs.get('username')
        if self._name is None:
            self._name = username
        cmd = kwargs.get("cmd", "")
        roomargs = kwargs.get(cmd, [])
        roomname = roomargs[1] if len(roomargs) == 2 else ""
        
        room = Manager.getinstanceTest().getroom(roomname)
        if roomname == "":
            room = ChatRoom.create(self, username)
            Manager.getinstance().newroom(room)
            return f"You created and entered a room named as {username}", None, room._bc
        elif room is None:
            return f"No such room named {roomname}", None, None
        else:
            room.enterconn(self)
            return f"You entered the room {room._name}", f"{username} entered the room", room._bc
    
    
    @bizFuncServerReg(RegisteredFunc.EXIT)
    def exit(self, **kwargs):
        logging.debug("args", kwargs)
        Manager.getinstance().disconn(self)
        return "Exit the server", None, None
        
    
    
    @bizFuncServerReg(RegisteredFunc.CHAT)    
    def chat(self, *args, **kwargs):
        logging.debug(args, kwargs)
        cmd = kwargs.get("cmd", "")
        Manager.getinstance().getatroom(self)._bc.putmsg(Message(" ".join(kwargs.get(cmd)), kwargs.get("username"), kwargs.get("timestamp")))
        room = Manager.getinstance().getatroom(self)
        msgs = room._bc.getunsyncedmsg()
        bcmsg = list(map(Message.jsonallize, msgs))
        return bcmsg, bcmsg, room._bc
    
    
    @bizFuncServerReg(RegisteredFunc.CINFO)
    def giveroominfo(self, **kwargs):
        room =  Manager.getinstance().getatroom(self)
        if room is not None:
            return room.details, None, None
        else:
            return "Error", None, None
    
    @bizFuncServerReg(RegisteredFunc.CLEAVE)
    def exitroom(self, *args, **kwargs):
        logging.debug(args, kwargs)
        room = Manager.getinstance().getatroom(self)
        self._chatroom = None
        if room is not None:
            room.leaveconn(self)
            return "Leave the room", f"{self._name} left the room", room._bc
        else:
            return "Error, you are not at room", None, None
        
        
    @bizFuncServerReg(RegisteredFunc.CEXIT)
    def disconnectserver(self, *args, **kwargs):
        logging.debug(f"{args}, {kwargs}")
        
        room = Manager.getinstance().getatroom(self)
        Manager.getinstance().disconn(self)
        
        if room is not None:
            room.leaveconn(self)
            return "Disconnect with the server", f"{self._name} left the room", room._bc
        else:
            return "Disconnect with the server", None, None
        
    
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
    
    