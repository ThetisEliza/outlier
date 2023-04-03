import sys
import time
from argparse import ArgumentParser
from typing import List

from .biz.beans import ChatMessage
from .biz.bizservice import BizRequest, ClientBizService, State, bizclnt
from .encryption.sessionservice import ConnectSessService, SessionService
from .server import Server
from .tools.chatterminal import ct
from .tools.utils import RandomGen, initlogger
from .transmission.tcpservice import TcpConnectService

if ct.valid:
    print = ct.output
    input = ct.input

class Client(ClientBizService):
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        super().__init__(sessservice, **kwargs)
        
        self.chatblock = False
        self.buffer: List[ChatMessage] = list()
        self.name = kwargs.get('name')
        
    def show_msg(self, package):
        print(f"{package.get_field('param')}\n")
        
    def show_chat(self, package):
        cm = package.get_field('param')
        cm = ChatMessage.parse(cm)
        if self.chatblock:
            self.buffer.append(cm)
        else:
            print(cm.format())
    
    def connected(self, package):
        self.atstate = State.Hall
        self.show_msg(package)
        
    def process_input(self, inputs: str):
        super().process_input(inputs)
        time.sleep(0.5)
        for cm in self.buffer:
            print(cm.format())
            
    
    @bizclnt(state=State.IDLE, bindto=Server.connectuser, recall=connected)
    def connect(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest(param=self.name)
    
    
    @bizclnt(state=State.Room, invokeptn="^(?!\$).+", bindto=Server.chat, recall=show_chat)
    def chat(self, inputs=None, *args, **kwargs) -> BizRequest:
        from datetime import datetime
        cm = ChatMessage(self.name, datetime.now().timestamp(), inputs)
        return BizRequest(param=cm.getattrs())
    
    
    
    @bizclnt(state=State.Hall, invoke="$info", bindto=Server.infohall, recall=show_msg, 
             desc="To glance at the details of the server and client configuartions")
    def info(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest()
    
    
    
    @bizclnt(state=State.Hall, invoke="$exit", 
             desc="To disconnect with the server")
    def quit(self, inputs=None, *args, **kwargs):
        self.close()
        return BizRequest()
        
    
    @bizclnt(state=State.Hall, invoke="$help")
    def help(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest()
    
    
    
    def entered(self, package):
        self.atstate = State.Room
        self.show_msg(package)
    
    @bizclnt(state=State.Hall, invoke="$room", bindto=Server.enterroom, recall=entered,
            descparams="[room name]",
            desc="To enter one of the room or create one by specified name or your username")
    def enter(self, inputs=None, *args, **kwargs) -> BizRequest:
        if len(args) == 1:
            return BizRequest(param=args[0])
        else:
            raise Exception("Parameter Error")
    
    
    
    def left(self, package):
        self.atstate = State.Hall
        self.show_msg(package)

    @bizclnt(state=State.Room, invoke="$leave", bindto=Server.leftroom, recall=left)
    def leave(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest()
    
    
    
    @bizclnt(state=State.Room, invoke="$info", bindto=Server.roominfo, recall=show_msg,
            desc="To glance at the details of the room")
    def roominfo(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest()
    
    
    @bizclnt(state=State.Room, invoke="$clear",
            desc="To clear the terminal")
    def clear(self, inputs=None, *args, **kwargs) -> BizRequest:
        import subprocess
        subprocess.call('reset')
        return BizRequest()
    
    
    @bizclnt(state=State.Room, invoke="$",
            desc="Switch comming message block")
    def blockswitch(self, inputs=None, *args, **kwargs) -> BizRequest:
        if self.chatblock:
            self.chatblock = False
            for cm in self.buffer:
                print(cm.format())
        else:
            self.chatblock = True
        return BizRequest()
        
        
    def start(self):
        def waituntilready():
            retrials = 0
            while True:
                retrials += 1
                time.sleep(3)
                if self.sessservice.ready and self.sessservice.tsservice.loop:
                    break
                print(f"Waiting for channel ready for {retrials * 5} / {5 * 5} secs")
                if retrials > 4:
                    raise Exception("channel build failed")
            retrials = 0
            
        try:
            super().start()
            waituntilready()
            self.connect()
            while True:
                a = input()
                self.process_input(a)
        except Exception as e:
            print(e)
            self.close()
        
            
            
            



def main():
    argparse = ArgumentParser(prog="Chat room", description="This is a chat room for your mates")
    argparse.add_argument("-l", "--log", default="error", type=str, choices=["DEBUG", "INFO", "ERROR", "debug", "info", "error"])
    argparse.add_argument("-n", "--name", required=True, type=str)
    argparse.add_argument("-i", "--ip",   required=True, type=str)
    argparse.add_argument("-p", "--port", required=False, type=int, default=8809)
    argparse.add_argument("-k", "--key",  required=False, type=str, default=RandomGen.getrandomvalue()[:6])
        
    kwargs = vars(argparse.parse_args())
    initlogger(kwargs.get('log').upper(), filehandlename=kwargs.get('loghandler'))    
    
    ts = TcpConnectService(False, **kwargs)
    ss = ConnectSessService(ts, **kwargs)
    bs = Client(ss, **kwargs)
    bs.start()  

    
if __name__ == '__main__':
    main()
