'''
Date: 2022-11-16 16:59:28
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 17:52:50
FilePath: /outlier/src/client.py
'''
import socket
import time
import sys
import logging
import re
from queue import Queue
from threading import Thread
from datetime import datetime
from manager import Config
from protocol import Package, Command, Message
from argparse import ArgumentParser
from typing import List
import utils

class ClientController:
    
    # status
    CHAT    = 0
    CMD     = 1
    BG      = 2
    
    
    # command
    
    def __init__(self, sk, username, client):
        # self._status = ClientController.CHAT
        self._status = ClientController.CMD
        self._func_map = {}
        self._sk = sk
        self._username = username
        self._client = client
        
        
        self.__register_func(ClientController.CHAT, "$cmd", self.__handletocommand)
        # self.__register_func(ClientController.CHAT, "$bg",  self.__handletobg)
        self.__register_func(ClientController.CHAT, "$exit",  self.__handleexit)
        self.__register_func(ClientController.CHAT, "$chat",  self.__handlenonswitch)
        self.__register_func(ClientController.CHAT, "unk",  self.__handlechat)
        
        self.__register_func(ClientController.CMD,  "$chat",  self.__handletochat)
        # self.__register_func(ClientController.CMD,  "$bg",    self.__handletobg)
        self.__register_func(ClientController.CMD,  "history",  self.__handlehistory)
        self.__register_func(ClientController.CMD,  "sync",  self.__handlesync)
        self.__register_func(ClientController.CMD,  "room",  self.__handleroom)
        self.__register_func(ClientController.CMD,  "info",  self.__handlefetchinfo)
        self.__register_func(ClientController.CMD,  "exit",  self.__handleexit)
        self.__register_func(ClientController.CMD,  "reconnect",  self.__handlereconnect)
        
        # self.__register_func(ClientController.BG,  "$chat",  self.__handletochat)
        # self.__register_func(ClientController.BG,  "$cmd",   self.__handletobg)
        # self.__register_func(ClientController.BG,  "state",  self.__handlecheckstate)
        # self.__register_func(ClientController.BG,  "back",   self.__handleback)
        
        
        
        
    def __register_func(self, status, cmd, func):
        self._func_map.setdefault(status, {})
        self._func_map[status][cmd] = func
        logging.debug(f"register func {status}, {cmd}, {func}") 
    
    # default handler
    def __handleunknown(self, inputinfo, *inputs):
        logging.debug(f"input err")
        
    # status switch
    # def __handletobg(self, inputinfo, *inputs):
    #     logging.debug(f"to bg")
    #     self._status = ClientController.BG
        
    def __handletocommand(self, inputinfo, *inputs):
        logging.debug(f"to cmd")
        self._status = ClientController.CMD
        
    def __handletochat(self, inputinfo, *inputs):
        logging.debug(f"to chat")
        
        logging.info(f"start chat")
        self._status = ClientController.CHAT
        self._client.showbufferedmsg()
        
        
    def __handlenonswitch(self, inputinfo, *inputs):
        logging.debug(f"already at state {inputinfo}")
        
        
        
    # chat functions
    def __handlechat(self, inputinfo, *inputs):
        self._sk.send(Package.buildpackage().add_field("msg", inputinfo).add_field("username", self._username).tobyteflow())
        time.sleep(0.1)
        self.activelysyncmessages()
        
        
    # command functions
    def __handlehistory(self, inputinfo, *inputs):
        logging.debug(f"handle history")
        
    def __handlesync(self, inputinfo, *inputs):
        logging.debug(f"handle sycn")
        
    def __handlefetchinfo(self, inputinfo, *inputs):
        logging.debug(f"handle fetch info")
        self._sk.send(Package.buildpackage().add_cmd(Command.INFO).add_field("username", self._username).tobyteflow())
        
    # # bg functions
    # def __handlecheckstate(self, inputinfo, *inputs):
    #     logging.debug(f"handle check state")
        
    # def __handleback(self, inputinfo, *inputs):
    #     logging.debug(f"handle back")
    
    def __handleroom(self, inputinfo, *inputs):
        logging.debug(f"handle room")
        if len(inputs) > 1:
            roomname = inputs[1]
            self._sk.send(Package.buildpackage().add_cmd(Command.ROOM).add_field("username", self._username).add_field("roomname", roomname).tobyteflow())
        else:
            self._sk.send(Package.buildpackage().add_cmd(Command.ROOM).add_field("username", self._username).tobyteflow())
        time.sleep(0.1)
        
    def __handlereconnect(self, inputinfo, *inputs):
        logging.debug(f"handle reconnect")
        self._client.reconnect()
        
    def __handleexit(self, inputinfo, *inputs):
        logging.debug(f"handle exit")
        self._client.close()
    
    # api functions
    def activelysyncmessages(self):        
        self._sk.send(Package.buildpackage().add_cmd(Command.FETCH).add_field('timestamp', self._client.lastsync).tobyteflow())
        time.sleep(0.1)
        
        
        
    def interact(self, inputinfo, *inputs):
        cmd_        = inputs[0]
        funcmap_    = self._func_map.get(self._status, {})
        func_       = funcmap_.get(cmd_, funcmap_.get("unk", self.__handleunknown))
        logging.debug(f"check interact cmd {cmd_}, funcmap {funcmap_.keys()}, func_ {func_}, inputinfo {inputinfo}, inputs {inputs}")
        func_(inputinfo, *inputs)
        


class Client:
        
    def __init__(self, conf):
        self._conf = conf
        self._sk = socket.socket()
        self._sk.connect((self._conf.ip, self._conf.port))
        self._msgbuffer: List[Message] = []
        self.controller = ClientController(self._sk, conf.username, self)
        self._loopflag = True
        self.lastsync = -1
        self.recvThread = Thread(target=self._recvLoop)
        self.recvThread.setDaemon(True)
        self.recvThread.start()
        self.controller.activelysyncmessages()
        self._interactloop()
    
    def reconnect(self):
        logging.info("preparing reconnect")
        self._sk = socket.socket()
        self._sk.connect((self._conf.ip, self._conf.port))
        self.recvThread = Thread(target=self._recvLoop)
        self.recvThread.setDaemon(True)
        self.recvThread.start()
        
    def close(self):        
        self._sk.shutdown()
        
    def showbufferedmsg(self):
        for m in self._msgbuffer:
            logging.info(f"message {m}")
        self._msgbuffer.clear()  
        
    def _recv(self):
        data = self._sk.recv(1024)
        if data == b"":
            return None, -1
        elif data is None:
            return None, -2
        else:
            return data, 0
        
    def _recvLoop(self):
        errortime = 0
        while self._loopflag:
            recv_bytes, status = self._recv()
            
            if status < 0:
                errortime += 1
                
            if errortime > 3:
                break
            
            try:
            
                package = Package.parsebyteflow(recv_bytes)
                logging.debug(f"recv msg {package.get_data()}")
                
                if Command.SYNC_RET in package.get_data():
                    self.lastsync = datetime.timestamp(datetime.now())
                    messagedata = package.get_data()[Command.SYNC_RET]
                    for m in messagedata:
                        message = Message.parse(**m)
                        self._msgbuffer.append(message)
                
                if Command.INFO_RET in package.get_data():
                    messagedata = package.get_data()[Command.INFO_RET]
                    print(messagedata)
                    
                if Command.ROOM_RET in package.get_data():
                    msg = package.get_data()[Command.ROOM_RET]
                    if msg == "enter":
                        logging.info("entered room")
                        self.controller.interact("$chat", "$chat")
                
                
                if self.controller._status == ClientController.CHAT:
                    self.showbufferedmsg()
            
            except Exception as e:
                logging.warning(e)
                errortime += 1
        self.close()
            
    def _interactloop(self):
        while self._loopflag:
            inputinfo = input().strip()
            inputs = re.split("\\s+", inputinfo)
            inputs = list(filter(lambda x: len(x) != 0, inputs))
            logging.debug(f"check inputs {inputs} inputinfo {inputinfo}")
            if len(inputs):
                self.controller.interact(inputinfo, *inputs)
                
        
def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="INFO", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-n", "--name", required=True, type=str)
    args = argparse.parse_args()
    
    conf = Config(**{"log": args.log, "username": args.name})
        
    utils.init_logger(conf.log.upper())
    
    Client(conf)
    
    

    
if __name__ == '__main__':
    main()