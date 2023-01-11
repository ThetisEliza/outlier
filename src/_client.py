'''
Date: 2023-01-10 11:20:45
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-11 14:39:37
FilePath: /outlier/src/_client.py
'''

import socket
import time
import sys
import logging
import re
from threading import Thread

from protocol import Package, Command, Message
from regdecorator import bizFuncClientRequestReg, bizFuncClientRecallReg, ClientClassReg
from func import RegisteredFunc, State

from typing import List
import platform


@ClientClassReg
class Client:
        
    def __init__(self, conf):
        self._conf = conf
        self._sk = socket.socket()
        self._status = State.Hall
        self._username = conf.username
        self._sk.connect((self._conf.ip, self._conf.port))
        self._msgbuffer: List[Message] = []
        self._loopflag = True
        self.lastsync = -1
        self.recvThread = Thread(target=self._recvLoop)
        self.recvThread.setDaemon(True)
        self.recvThread.start()
        self._interactloop()
    
    def reconnect(self):
        self._sk.shutdown()
        
    
    def showbufferedmsg(self):
        for m in self._msgbuffer:
            logging.info(f"message {m}")
        self._msgbuffer.clear()  

    @property
    def localInfo(self):
        ret = "Client details:\n"
        ret += f"- Username: {self._username}\n"
        ret += f"- System info: {platform.platform()}\n"
        ret += f"- Python version & location: {sys.version}\n"
        return ret
        
    
    @bizFuncClientRecallReg(RegisteredFunc.INFO)
    def showinfomsg(self, *args, **kwargs):
        logging.debug(args, kwargs)
        
        print("Server details:")
        for arg in args:
            print(arg)
        print(self.localInfo)
        
        
        
        
    @bizFuncClientRecallReg(RegisteredFunc.ROOM)
    def showroommsg(self, *args, **kwargs):
        for arg in args:
            if arg is not None:
                print(arg)
        
                
                
    @bizFuncClientRecallReg(RegisteredFunc.EXIT, RegisteredFunc.CEXIT)
    def exit(self, *args, **kwargs):
        logging.debug("exit program")
        exit(0)
        
    
    @bizFuncClientRecallReg(RegisteredFunc.CHAT)
    def recvmsg(self, *args, **kwargs):
        logging.debug(f"recved msg {args} {kwargs}")
        messagedata = kwargs.get("bc")
        if messagedata is not None:
            for m in messagedata:
                message = Message.parse(**m)
                self._msgbuffer.append(message)
        if args[0] is not None:
            for m in args[0]:
                message = Message.parse(**m)
                self._msgbuffer.append(message)
    
    @bizFuncClientRecallReg(RegisteredFunc.CINFO)
    def showroominfomsg(self, *args, **kwargs):
        logging.debug(args, kwargs)
        
        print("Room details:")
        for arg in args:
            print(arg)
            
        print(self.localInfo)
    
    
    @bizFuncClientRecallReg(RegisteredFunc.CLEAVE)
    def exitroom(self, *args, **kwargs):
        logging.debug(f"recved msg {args} {kwargs}")
        for arg in args:
            if arg is not None:
                print(arg)
        
        
    @bizFuncClientRequestReg(RegisteredFunc.DEFAULT, RegisteredFunc.CHELP, RegisteredFunc.HELP)    
    def showhelpmesg(self, *args, **kwargs):
        print("Supported commands:")
        for func in RegisteredFunc.FuncConfiguredList:
            if func._atstate == self._status:
                print(f"{func._help}")
    
    @bizFuncClientRequestReg(RegisteredFunc.CCLEAR)
    def clearterminal(self, *args, **kwargs):
        import subprocess
        subprocess.call('reset')

        
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
                
                ret_cmd = package.get_data().get("cmd")
                ret_msg = package.get_data().get(ret_cmd)
                bc_msg  = package.get_data().get("bc_"+ret_cmd)
                
                
                
                
                func = RegisteredFunc.getClientRecallFunc(ret_cmd)
                
                if func._switch is not None and ret_msg is not None:
                    self._status = func._switch
                    
                if bc_msg is not None:
                    print(bc_msg)
                else:
                    func.clientrecall(self, ret_msg, bc=bc_msg)
                
                self.showbufferedmsg()
                
                errortime = 0
            except Exception as e:
                logging.warning(e)
                errortime += 1
        self.close()
            
    def _interactloop(self):
        while self._loopflag:
            try:
                inputinfo = input().strip()
            except Exception as e:
                logging.warning(e)
                break
            
            logging.debug(f"check inputs {inputinfo}")
            
            inputs = re.split("\\s+", inputinfo)
            
            inputs = list(filter(lambda x: len(x) != 0, inputs))
            logging.debug(f"check inputs {inputs} inputinfo {inputinfo}")
            if len(inputs):
                # self.controller.interact(inputinfo, *inputs)
                cmd_        = inputs[0]
                func = RegisteredFunc.getClientFunc(self._status, cmd_)
                if func == RegisteredFunc.DEFAULT:
                    logging.warning(f"No cmd [{cmd_}] in state {self._status}")
                    func.clientaction(self)
                else:
                    logging.debug(f"check interact cmd {cmd_}, func_ {func}, inputinfo {inputinfo}, inputs {inputs}")
                    func.clientaction(self, inputinfo=inputinfo, sendarg=inputs)
                    