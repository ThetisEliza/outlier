'''
Date: 2023-01-03 14:58:05
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-11 11:48:53
FilePath: /outlier/src/func.py
'''

'''
Functions Frame
'''
import time

from .protocol import Package

def nop(*args, **kwargs):
    time.sleep(0.1)
    
class State:
    Hall    = "Hall"
    Chat    = "Chat"
    Cmd     = "Cmd"
    


class FuncBase:
    def __init__(self,
        command: str,
        atstate: str = None,
        isremote: bool = False,
        commandpattern = None,
        stateswitch = None,
        *param,
        **kwargs) -> None:
        
        self._cmd       = command
        self._atstate   = atstate
        self._iremote   = isremote
        self._cmdptn    = commandpattern
        self._switch    = stateswitch
        self._param     = param
        self._kwargs    = kwargs


    @property
    def _statusname(self):
        return self._cmd + '@' + self._atstate
    
    @property
    def _retname(self):
        return 'ret_' + self._cmd

    @property
    def _help(self):
        usage =  self._kwargs.get("usage", None)
        usage =  (self._cmd + ((" "+self._kwargs.get("descparams", "")) if "descparams" in self._kwargs else "")) if usage is None else usage
        return "\t"+self._cmd +"\t" + self._kwargs.get("desc", "") + "\n\t\t-Usage:\t" + usage
            

    def clientaction(self, client, *args, **kwargs):
        if self._iremote:
            package = Package.buildpackage() \
                .add_cmd(self._cmd) \
                .add_field("username", client._username) \
                .add_field_if("sendarg" in kwargs, self._cmd, kwargs.get("sendarg")) \
                .tobyteflow()
            client._sk.send(package)
            time.sleep(0.1)
        
        localaction = self._kwargs.get("localaction", nop)
        localaction(client, *args, **kwargs)
        
        
    def clientrecall(self, client, *args, **kwargs):
        
        localrecall = self._kwargs.get("localrecall", nop)
        localrecall(client,  *args, **kwargs)
        
        
    def serveraction(self, conn, **kwargs):
        servereffectaction = self._kwargs.get("servereffectaction", nop)
        
                
        responsearg, bcarg, bc = servereffectaction(conn, **kwargs)
        
        # server response
        package = Package.buildpackage() \
            .add_cmd("ret_" + self._cmd) \
            .add_field_if(responsearg is not None, "ret_" + self._cmd, responsearg) \
            .view() \
            .tobyteflow()
        
        try:
            conn.send(package)
            time.sleep(0.1)
        except:
            print(f"conn has been closed {conn}")
        
        if bc is not None:
            # server broadcast
            package = Package.buildpackage() \
                .add_cmd("ret_" + self._cmd) \
                .add_field_if(bcarg is not None, "bc_ret_" + self._cmd, bcarg) \
                .view() \
                .tobyteflow()
            bc.broadcast(package, conn)
            time.sleep(0.1)

    
    def __repr__(self) -> str:
        return f"FuncBase:{self._cmd}"

import re
from typing import List, Tuple

class RegisteredFunc:
    DEFAULT = FuncBase("NA", None, False)
    INFO = FuncBase("$info", State.Hall, True, desc="To glance at the details of the server and client configuartions")
    ROOM = FuncBase("$room", State.Hall, True, stateswitch=State.Chat, 
                    descparams="[room name]",
                    desc="To enter one of the room or create one by specified name or your username")
    EXIT = FuncBase("$exit", State.Hall, True, desc="To disconnect with the server")
    HELP = FuncBase("$help", State.Hall, False)
    
    CHAT = FuncBase("$chat", State.Chat, True, commandpattern="^(?!\$).+", desc="To send msg to the chat room", usage="Type your message here. DO NOT start with `$`")
    CINFO = FuncBase("$roominfo", State.Chat, True, desc="To glance at the details of the room")
    CLEAVE = FuncBase("$leave", State.Chat, True, stateswitch=State.Hall, desc="To leave the room")
    CEXIT = FuncBase("$exit", State.Chat, True, desc="To disconnect with the server")
    CCLEAR = FuncBase("$clear", State.Chat, False, desc="To clear the terminal")
    CHELP = FuncBase("$help", State.Chat, False)
    
    
    FuncConfiguredList: List[FuncBase] = []
    
    @staticmethod
    def getClientFunc(status: str, cmd: str):
        for func in RegisteredFunc.FuncConfiguredList:
            if func._cmd == cmd and func._atstate == status:
                return func
            elif func._cmdptn is not None and re.search(func._cmdptn, cmd) and status == func._atstate:
                return func
        return RegisteredFunc.DEFAULT
            
    @staticmethod
    def getClientRecallFunc(ret_cmd: str):
        for func in RegisteredFunc.FuncConfiguredList:
            if func._retname == ret_cmd:
                return func
        return RegisteredFunc.DEFAULT

    @staticmethod                
    def getServerFunc(cmd: str):
        for func in RegisteredFunc.FuncConfiguredList:
            if func._cmd == cmd:
                return func
        return RegisteredFunc.DEFAULT
        
        
        

import inspect

for name, a in inspect.getmembers(RegisteredFunc):
    if type(a) == FuncBase:
        RegisteredFunc.FuncConfiguredList.append(a)
        
