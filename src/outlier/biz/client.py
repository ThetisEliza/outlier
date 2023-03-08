import time
from typing import List

from encryption.sessionservice import SessionService
from biz.bizservice import ClientBizService, State, bizclnt, BizRequest
from biz.beans import ChatMessage

from biz.server import Server


class Client(ClientBizService):
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        super().__init__(sessservice, **kwargs)
        
        self.chatblock = False
        self.buffer: List[ChatMessage] = list()
        
    def show_msg(self, package):
        print(f"{package.get_field('param')}")
        
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
    
    @bizclnt(state=State.IDLE, bindto=Server.connectuser, recall=connected)
    def connect(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest(param="Alice")
    
    
    
    @bizclnt(state=State.Room, invokeptn="^(?!\$).+", bindto=Server.chat, recall=show_chat)
    def chat(self, inputs=None, *args, **kwargs) -> BizRequest:
        from datetime import datetime
        cm = ChatMessage("Alice", datetime.now().timestamp(), inputs)
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
        super().start()
        time.sleep(0.5)
        self.connect()
        while True:
            a = input()
            self.process_input(a)