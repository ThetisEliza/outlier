import inspect
import logging
import re
import signal
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Tuple, TypeVar, Union

from encryption.sessionservice import Package, Session, SessionService
from transmission.tcpservice import Ops

'''
I am kinda confused. what is the design supposed to ... I think there must be
a way for a proper update process. Now let's use another way. We use server 
as the `stem` update way, client follows. we should use some way to add the biz
respond function automatically and we should use some way to make the client can
easily correspoing to it.
For exmaple,

`python`

def bizserv:

class Server:
    @bizserv
    def bizfuncA:
    
    @bizserv
    def bizfuncB:

def bizclnt

class Client:
    @bizclnt(bizfuncA)
    def bizfuncA:
    
    @bizclnt(bizfunc)
    def bizfuncB:


We have three phase in total.
1. generate request -> biz and this request can be related with biz func
2. request -> package
3. package -> request 
4. generate response -> biz
5. repsonse -> package
6. solve repsonse -> biz
'''

class State(Enum):
    IDLE = -1
    Hall = 0
    Room = 1
    Cfrm = 2
    
    

@dataclass
class User:
    sess: Session
    name: str
    syncts: float = -1
    
@dataclass
class BizRequest:
    cmd: str   = None
    ts:  float = None
    param: Any = None

@dataclass
class BizResponse:
    resp: Any   = None
    bcresp: Any = None
    ts: float   = None
    cmd: str    = None
    group: int  = -1
    inc: bool   = False

class BizService:
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        self.sessservice = sessservice
        self.sessservice.set_upper_rchandle(self.rchandle)
        self.acfuncs: List[Callable] = list()
        self.rcfuncs: List[Callable] = list()
        self.kwargs = kwargs
        signal.signal(signal.SIGINT, self.close)
        
    def rchandle(self, ops: Ops, session: Session, package: Package, *args):
        pass
        
    def _pack_req(self, bizreq: BizRequest) -> Package:
        return Package.buildpackage().add_cmd(bizreq.cmd) \
            .add_field_if(bizreq.param is not None, "param", bizreq.param) \
            .add_field_if(bizreq.ts is not None, Package.TIME, bizreq.ts)
        
    def _unpack_req(self, package: Package) -> BizRequest:
        return BizRequest(package.get_field("cmd"), package.get_field("ts"), package.get_field("param"))
    
    def _pack_resp(self, bizresp: BizResponse) -> Package:
        pack = Package.buildpackage().add_cmd(bizresp.cmd) \
            .add_field("param", bizresp.resp) \
            .add_field_if(bizresp.ts is not None, Package.TIME, bizresp.ts)
            
        bc = None if bizresp.bcresp is None else Package.buildpackage().add_cmd(bizresp.cmd) \
            .add_field("param", bizresp.bcresp) \
            .add_field_if(bizresp.ts is not None, Package.TIME, bizresp.ts)
        return pack, bc
    
    
    def _getrcfuncs(self, ops: Ops, bizreq: BizRequest) -> Callable:
        for func in self.rcfuncs:
            if func.__qualname__.partition('.')[-1] == bizreq.cmd:
                return func
            if 'rc' in dir(func) and func.rc == ops:
                return func
        return lambda *args:  BizResponse("NA")
    
    def close(self, *args):
        self.sessservice.close(*args)
    
    def start(self):
        self.sessservice.start()


def bizserv(**kwargs):
    def inner(fn: Callable[[BizService, User, BizRequest, Any], BizResponse]):
        def wrapper(bizservice, user: User, bizreq: BizRequest, *args, **kwargs):
            bizresp: BizResponse = fn(bizservice, user, bizreq, *args, **kwargs)
            bizresp.cmd = fn.__qualname__.partition('.')[-1]
            return bizresp
        wrapper.__qualname__ = fn.__qualname__
        wrapper.__setattr__("wrapped", "server")
        wrapper.__setattr__("kwargs", kwargs)
        
        if kwargs is not None and 'rc' in kwargs:
            wrapper.__setattr__('rc', kwargs.get('rc'))
        return wrapper
    return inner

    
class ServerBizService(BizService):
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        super().__init__(sessservice, **kwargs)
        self.users: Dict[Any, User] = dict()
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if 'wrapped' in dir(func):
                logging.debug(f"{name} registered on {func}")
                self.rcfuncs.append(func)
        
    
    def rchandle(self, ops: Ops, session: Session, package: Package, *args):
        logging.debug(f"[Biz Layer] recall {ops} {session.conn.addr} {package}")
        bizreq = self._unpack_req(package)
        user = self.users.get(session.conn.addr)
        if ops == Ops.Add:
            user = User(session, "default")
            self.users[session.conn.addr] = user
        elif ops == Ops.Rmv:
            self.users.pop(session.conn.addr)
        elif ops == Ops.Rcv:
            pass
        
        bizfunc = self._getrcfuncs(ops, bizreq)
        bizresponse: BizResponse = bizfunc(user, bizreq)
        self.send(user, bizresponse)
        
        
    def send(self, user:User, bizresp: BizResponse):
        pack, bc = self._pack_resp(bizresp)
        if not bizresp.inc:
            self.sessservice.send(pack, user.sess)
        if bc:
            bcusers = filter(lambda u: u.sess.group == bizresp.group, self.users.values())
            bcusers = filter(lambda u: u != user if not bizresp.inc else True, bcusers)
            bcsess = map(lambda u: u.sess, bcusers)
            self.sessservice.send_group(bc, *bcsess)
        
        

        
        

    
def bizclnt(state:State, 
            invoke:str = None, 
            invokeptn: str = None,  
            bindto: Callable = None, 
            recall: Callable = None, 
            **kwargs):
    
    def gethelp():
        usage =  kwargs.get("usage", None)
        if invoke is not None:
            usage =  (invoke + ((" "+kwargs.get("descparams", "")) if "descparams" in kwargs else "")) if usage is None else usage
            return "\t"+ invoke +"\t" + kwargs.get("desc", "") + "\n\t\t-Usage:\t" + usage
        else:
            return "\t"+ f"hidden method {invoke} {invokeptn} {bindto} {recall}. Do not invoke" 
        
    
    def inner(fn: Callable[[BizService, str, str, Any], BizRequest]):
        def wrapper(bizservice: BizService, inputs: str = None, *args, **kwargs):
            try:
                bizreq: BizRequest = fn(bizservice, inputs, *args, **kwargs)
                if bindto is not None:
                    bizreq.cmd = bindto.__qualname__.partition(".")[-1]
                bizservice.send(bizreq)
                return bizreq
            except Exception as e:
                logging.debug(e)
                print(wrapper.help)
                return BizRequest()
       

        # set basic attribute: [name, wrapped, state]        
        wrapper.__qualname__ = fn.__qualname__
        wrapper.__setattr__("wrapped", "clnt")
        wrapper.__setattr__("state", state)
        wrapper.__setattr__("help", gethelp())
        
        # set invoke string to make sure whether it should be invoked by certain command
        if invoke is not None:
            wrapper.__setattr__("invokestr", invoke)
            
        # set invoke command pattern
        if invoke is not None or invokeptn is not None:
            wrapper.__setattr__("invoke", lambda cmd, atstate: \
                (atstate  == state and (invoke == cmd if invokeptn is None else re.match(invokeptn, cmd) is not None)))
            
        # set server proc method
        if bindto is not None:
            logging.debug(f"{fn} binds to {bindto.__qualname__}")
            wrapper.__setattr__("bindtoname", bindto.__qualname__.partition(".")[-1])
            
        # set recall method to proc server response
        if recall is not None:
            logging.debug(f"{fn} recall at {recall.__qualname__}")
            wrapper.__setattr__("recall", recall)
            recall.__setattr__("recall", "clnt")
            
        return wrapper
    return inner
    
    
        
class ClientBizService(BizService):
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        super().__init__(sessservice, **kwargs)
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if 'wrapped' in dir(func):
                logging.debug(f"{name} registered on {func}")
                self.acfuncs.append(func)
        self.atstate = State.IDLE
        
    def rchandle(self, ops: Ops, session: Session, package: Package, *args):
        bizreq = self._unpack_req(package)
        for func in self.acfuncs:
            if 'bindtoname' in dir(func) and  func.bindtoname == bizreq.cmd and 'recall' in dir(func):
                recallfunc = func.recall
                recallfunc(self, package)
        
    def send(self, bizreq: BizRequest):
        self.sessservice.send(self._pack_req(bizreq))
        
    
    
    def process_input(self, inputs: str):
        if len(inputs.strip()) <= 0: return
        splits = inputs.split()
        cmd, params = splits[0], splits[1:]
        
        searchfunc = None
        for func in self.acfuncs:
            if 'invoke' in dir(func) and func.invoke(cmd, self.atstate):
                searchfunc = func
                
        if searchfunc is None:
            print("Command failed")
            self.gethelp(inputs, *params)
        else:
            searchfunc(inputs, *params)
            
    
    def gethelp(self, inputs=None, *args, **kwargs):
        print(f"Current at {self.atstate.name} - Supported commands:\n")
        
        for func in self.acfuncs:
            if func.state == self.atstate and 'invokestr' in dir(func):
                print(f"{func.help}\n")
                
        



@dataclass
class ChatMessage:
    name:       str
    ts:         float
    content:    str

    def getattrs(self):
        return {'name': self.name, 'timestamp': self.ts, 'content': self.content}
    
    @staticmethod
    def parse(cm: dict):
        return ChatMessage(cm['name'], cm['timestamp'], cm['content'])
    
    @staticmethod
    def get_round_time(timestamp: float) -> str:
        """This is to convert timestamp gap to a human-readable time gap
        such as `1 days ago`, `1 hours ago` etc.

        Args:
            timestamp (float): target timestamp

        Returns:
            str: time gap
        """
        curr = datetime.now()
        happening = datetime.fromtimestamp(timestamp)
        delta = curr - happening
        if (delta.days > 0):
            return f"{delta.days} days ago"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds // 60 > 0:
            return f"{delta.seconds // 60} minutes ago"
        else:
            return "just now"
    
    def format(self):
        return f"{self.name} -- {ChatMessage.get_round_time(self.ts)}: {self.content}\n"
    

class Room:
    index = 0
    def __init__(self, name) -> None:
        self.history: List[ChatMessage] = list()
        self.group:   int               = Room.index
        self.passwd:  str               = None
        self.name:    str               = name
        self.connects:int               = 0
        Room.index += 1
        
    
    def __repr__(self) -> str:
        l = ("PSWD" if self.passwd else "FREE")
        return f"{'room:'+str(self.name):10}\t{l}\t{self.connects}\t{len(self.history)}"
    
    @staticmethod
    def header():
        return f"{'name':10}\t{'LOCK'}\tpeople\tmsg"
    

    
class Server(ServerBizService):
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        super().__init__(sessservice, **kwargs)
        self.rooms: List[Room] = [Room("R1")]
        

    @bizserv()
    def chat(self, user: User, bizreq: BizRequest) -> BizResponse:
        searchroom = None
        for room in self.rooms:
            if room.group == user.sess.group:
                logging.debug(f"find Room {room}")
                searchroom = room   
                break
            
        if searchroom is not None:            
            searchroom.history.append(ChatMessage.parse(bizreq.param))
            return BizResponse(bizreq.param, bizreq.param, group=room.group, inc=True)
        else:
            return BizResponse("error")
    
    
    @bizserv()
    def connectuser(self, user: User, bizreq: BizRequest) -> BizResponse:
        user.name = bizreq.param
        return BizResponse(f"Welcome {bizreq.param}")
    
    @bizserv()
    def infohall(self, user: User, bizreq: BizRequest) -> BizResponse:
        def getinfo():
            ret = ""
            ret += Room.header() + "\n"
            for room in self.rooms:
                ret += str(room) + "\n"
            return ret
        info = getinfo()
        return BizResponse(f"{info}", None)
    
    @bizserv()
    def enterroom(self, user: User, bizreq: BizRequest) -> BizResponse:
        name = bizreq.param
        for room in self.rooms:
            if room.name == name:
                logging.debug(f"enter room {room.name}")
                user.sess.group = room.group
                room.connects += 1
        return BizResponse(f"enter room {room.name}", f"{user.name} entered", group=room.group, inc=False)
    
    @bizserv(rc=Ops.Rmv)
    def leftroom(self, user: User, bizreq: BizRequest) -> BizResponse:
        group = -1
        for room in self.rooms:
            if room.group == user.sess.group:
                logging.debug(f"left room {room.name}")
                group = room.group
                user.sess.group = -1
                room.connects -= 1
                break
        if group != -1:
            return BizResponse(f"leave room {room.name}", f"{user.name} left", group=group)
        else:
            return BizResponse()
        
    @bizserv()
    def roominfo(self, user: User, bizreq: BizRequest) -> BizResponse:
        def getinfo():
            searchroom = None
            for room in self.rooms:
                if room.group == user.sess.group:
                    logging.debug(f"find Room {room}")
                    searchroom = room   
                    break
                
            if searchroom is not None:
                ret = f"Room: {searchroom.name}\n"
                for u in self.users.values():
                    if u.sess.group == searchroom.group:
                        ret += f"Connecting: {u.name}\tat {u.sess.conn.addr}\n"
                ret += f"room history message size: {len(searchroom.history)}\n"
                return ret
            else:
                return "error"
        ret = getinfo()
        return BizResponse(ret)
            
        
    
    
    
    
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