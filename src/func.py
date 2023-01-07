'''
Date: 2023-01-03 14:58:05
LastEditors: Xiaofei wxf199601@gmail.com
LastEditTime: 2023-01-07 20:33:35
FilePath: /outlier/src/func.py
'''

'''
Functions Frame
'''
import time

from protocol import Package
from client import Client
from server import ClientConn, Manager

def nop(*args):
    print("nop snap")
    time.sleep(0.1)
    
class State:
    Hall    = "Hall"
    Chat    = "Chat"
    Cmd     = "Cmd"
    


class FuncBase:
    def __init__(self,
        command: str,
        atstate: str,
        isremote: bool,
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

    def clientaction(self, client, **kwargs):
        if self._iremote:
            package = Package.buildpackage() \
                .add_cmd(self._cmd) \
                .add_field("username", client._username) \
                .add_field_if("sendarg" in kwargs, self._cmd, kwargs.get("sendarg")) \
                .tobyteflow()
            client._sk.send(package)
            time.sleep(0.1)
        
        localaction = self._kwargs.get("localaction", nop)
        localaction(client, None)
        
        
    def clientrecall(self, client, msg):
        localrecall = self._kwargs.get("localrecall", nop)
        localrecall(client, msg)
        
        
    def serveraction(self, conn, bc = None, **kwargs):
        
        servereffectaction = self._kwargs.get("servereffectaction", nop)
        responsearg, bcarg = servereffectaction(conn, **kwargs)
        print(responsearg)
        
        # server response
        package = Package.buildpackage() \
            .add_cmd("ret_" + self._cmd) \
            .add_field_if(responsearg is not None, "ret_" + self._cmd, responsearg) \
            # .tobyteflow()
        print(f"send package {package}")
        package = package.tobyteflow()
        conn.send(package)
        
        # server broadcast
        if bc:
            package = Package.buildpackage() \
                .add_cmd("ret_" + self._cmd) \
                .add_field_if(bcarg is not None, "bc_" + self._cmd, bcarg) \
                .tobyteflow()
            bc.broadcast(package)
        
    
    def __repr__(self) -> str:
        return f"FuncBase:{self._cmd}"


INFO = FuncBase("info", State.Hall, True, localrecall=Client.showretmsg, servereffectaction=ClientConn.giveinfo)
ROOM = FuncBase("room", State.Hall, True, localrecall=Client.showretmsg, servereffectaction=ClientConn.changeroom)


FuncConfig = [ INFO, ROOM ]

ClientFuncMap = {
    func._statusname: func for func in FuncConfig
}

ClientRecallMap = {
    func._retname : func for func in FuncConfig
}

ServerFuncMap = {
    func._cmd : func for func in FuncConfig
}


print(FuncConfig)
print(ClientFuncMap)
print(ClientRecallMap)
print(ServerFuncMap)

def bizServerReg(funname, **kwargs):
    def decorate(fn):
        print("decorate", funname, kwargs)
        return fn
    return decorate

class A:
    @bizServerReg("info")
    def b(self):
        print("b")
   
