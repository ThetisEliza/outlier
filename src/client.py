'''
Date: 2022-11-16 16:59:28
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2022-11-18 17:52:50
FilePath: /outlier/src/client.py
'''
import socket
import json
from queue import Queue
from threading import Thread
from manager import Config
from protocol import Package, Command


class ClientController:
    
    # status
    CHAT    = 0
    CMD     = 1
    BG      = 2
    
    
    # command
    
    def __init__(self, sk):
        self._status = ClientController.CHAT
        self._func_map = {}
        self._sk = sk
        
        self.__register_func(ClientController.CHAT, "$cmd", self.__handletocommand)
        self.__register_func(ClientController.CHAT, "$bg",  self.__handletobg)
        self.__register_func(ClientController.CHAT, "unk",  self.__handlechat)
        
        self.__register_func(ClientController.CMD,  "$chat",  self.__handletochat)
        self.__register_func(ClientController.CMD,  "$bg",    self.__handletobg)
        self.__register_func(ClientController.CMD,  "history",  self.__handlehistory)
        self.__register_func(ClientController.CMD,  "sync",  self.__handlesync)
        self.__register_func(ClientController.CMD,  "info",  self.__handlefetchinfo)
        self.__register_func(ClientController.CMD,  "exit",  self.__handleexit)
        
        self.__register_func(ClientController.BG,  "$chat",  self.__handletochat)
        self.__register_func(ClientController.BG,  "$cmd",   self.__handletobg)
        self.__register_func(ClientController.BG,  "state",  self.__handlecheckstate)
        self.__register_func(ClientController.BG,  "back",   self.__handleback)
        
        
    def __register_func(self, status, cmd, func):
        self._func_map.setdefault(status, {})
        self._func_map[status][cmd] = func
        print(f"register func {status}, {cmd}, {func}") 
    
    # default handler
    def __handleunknown(self, inputinfo, *inputs):
        print(f"input err")
        
    # status switch
    def __handletobg(self, inputinfo, *inputs):
        print(f"to bg")
        
    def __handletocommand(self, inputinfo, *inputs):
        print(f"to cmd")
        self._status = ClientController.CMD
        
    def __handletochat(self, inputinfo, *inputs):
        print(f"to chat")
        self._status = ClientController.CHAT
        
        
    # chat functions
    def __handlechat(self, inputinfo, *inputs):
        self._sk.send(Package.buildpackage().add_field("msg", inputinfo).tobyteflow())
        self.activelysyncmessages()
        
    # command functions
    def __handlehistory(self, inputinfo, *inputs):
        print(f"handle history")
        
    def __handlesync(self, inputinfo, *inputs):
        print(f"handle sycn")
        
    def __handlefetchinfo(self, inputinfo, *inputs):
        print(f"handle fetch info")
        
    def __handleexit(self, inputinfo, *inputs):
        print(f"handle exit")
        
        
    # bg functions
    def __handlecheckstate(self, inputinfo, *inputs):
        print(f"handle check state")
        
    def __handleback(self, inputinfo, *inputs):
        print(f"handle back")
        
    
    # api functions
    def activelysyncmessages(self):        
        package = Package.buildpackage().add_cmd(Command.FETCH)
        print(f"send msg {package}")
        self._sk.send(package.tobyteflow())
        
        
    def interact(self, inputinfo, *inputs):
        cmd_        = inputs[0]
        funcmap_    = self._func_map.get(self._status, {})
        func_       = funcmap_.get(cmd_, funcmap_.get("unk", self.__handleunknown))
        print(f"check interact cmd {cmd_}, funcmap {funcmap_.keys()}, func_ {func_}, inputinfo {inputinfo}, inputs {inputs}")
        func_(inputinfo, *inputs)
        


class Client:
        
    def __init__(self, conf):
        self._sk = socket.socket()
        self._sk.connect((conf.ip, conf.port)) 
        self.controller = ClientController(self._sk)
        self._interactloop()
        recvThread = Thread(target=self._recvLoop)
        recvThread.start()
        # self._interactloop()
        recvThread.join()
        self._sk.close()
        

    def _recvLoop(self):
        while 1:
            recv_bytes = self._sk.recv(1024)
            package = Package.parsebyteflow(recv_bytes)
            print(f"recv msg {package}")
            
            
    def _interactloop(self):
        while 1:  
            inputinfo = input().strip()
            import re
            inputs = re.split("\\s+", inputinfo)
            inputs = list(filter(lambda x: len(x) != 0, inputs))
            print(f"check inputs {inputs} inputinfo {inputinfo}")
            if len(inputs):
                self.controller.interact(inputinfo, *inputs)
        
def main():
    conf = Config()
    Client(conf)
    
    

    
if __name__ == '__main__':
    main()