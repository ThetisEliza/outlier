from encryption.sessionservice import SessionService, Package, Session
from transmission.tcpservice import Ops
from dataclasses import dataclass
from typing import List, Any, Tuple, Generic, TypeVar, Callable, Dict, Union
from enum import Enum
import inspect
import re



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

class BizService:
    def __init__(self, sessservice: SessionService) -> None:
        self.sessservice = sessservice
        self.sessservice.set_upper_rchandle(self.rchandle)
        self.acfuncs: List[Callable] = list()
        self.rcfuncs: List[Callable] = list()
        
        
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
    
    
    def _getrcfuncs(self, bizreq: BizRequest) -> Callable:
        for func in self.rcfuncs:
            cmd = bizreq.cmd
            if func.__qualname__.partition('.')[-1] == cmd:
                return func
        return lambda *args:  BizResponse("NA")
    
    def close(self, *args):
        self.sessservice.close(*args)
    


def bizserv(**kwargs):
    def inner(fn: Callable[[BizService, User, BizRequest, Any], BizResponse]):
        def wrapper(bizservice, user: User, bizreq: BizRequest, *args, **kwargs):
            bizresp: BizResponse = fn(bizservice, user, bizreq, *args, **kwargs)
            bizresp.cmd = fn.__qualname__.partition('.')[-1]
            return bizresp
        wrapper.__qualname__ = fn.__qualname__
        wrapper.__setattr__("wrapped", "server")
        wrapper.__setattr__("kwargs", kwargs)
        return wrapper
    return inner

    
class ServerBizService(BizService):
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        self.users: Dict[Any, User] = dict()
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if 'wrapped' in dir(func):
                print(f"{name} registered on {func}")
                self.rcfuncs.append(func)
        
    
    def rchandle(self, ops: Ops, session: Session, package: Package, *args):
        print(f"[Biz Layer] recall {ops} {session.conn.addr} {package}")
        bizreq = self._unpack_req(package)
        user = self.users.get(session.conn.addr)
        if ops == Ops.Add:
            user = User(session, "default")
            self.users[session.conn.addr] = user
        elif ops == Ops.Rmv:
            self.users.pop(session.conn.addr)
        elif ops == Ops.Rcv:
            pass
        
        bizfunc = self._getrcfuncs(bizreq)
        bizresponse: BizResponse = bizfunc(user, bizreq)
        self.send(user, bizresponse)
        
        
    def send(self, user:User, bizresp: BizResponse):
        pack, bc = self._pack_resp(bizresp)
        self.sessservice.send(pack, user.sess)
        if bc is not None:
            self.sessservice.send_group(bc, user.sess)
        
        

    
def bizclnt(state:State, 
            invoke:str = None, 
            invokeptn: str = None,  
            bindto: Callable = None, 
            recall: Callable = None, 
            **kwargs):
    def inner(fn: Callable[[BizService, str, str, Any], BizRequest]):
        def wrapper(bizservice: BizService, inputs: str = None, *args, **kwargs):
            bizreq: BizRequest = fn(bizservice, inputs = None, *args, **kwargs)
            bizreq.cmd = bindto.__qualname__.partition(".")[-1]
            bizservice.send(bizreq)
            if bindto is not None:
                bizreq.cmd = bindto.__qualname__.partition(".")[-1]
            return bizreq
        
        wrapper.__qualname__ = fn.__qualname__
        wrapper.__setattr__("wrapped", "clnt")
        wrapper.__setattr__("state", state)
        if invoke is not None or invokeptn is not None:
            wrapper.__setattr__("invoke", lambda cmd, atstate: \
                (atstate  == state and (invoke == cmd if invokeptn is  None else re.match(invokeptn, cmd) is not None)))
        if bindto is not None:
            print(f"{fn} binds to {bindto.__qualname__}")
            wrapper.__setattr__("bindtoname", bindto.__qualname__.partition(".")[-1])
        if recall is not None:
            print(f"{fn} recall at {recall.__qualname__}")
            wrapper.__setattr__("recall", recall)
            recall.__setattr__("recall", "clnt")
        return wrapper
    return inner
    
    
        
class ClientBizService(BizService):
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        for name, func in inspect.getmembers(self, predicate=inspect.ismethod):
            if 'wrapped' in dir(func):
                print(f"{name} registered on {func}")
                self.acfuncs.append(func)
        self.atstate = State.IDLE
        
    def rchandle(self, ops: Ops, session: Session, package: Package, *args):
        # print(package)
        bizreq = self._unpack_req(package)
        # print(bizreq)
        for func in self.acfuncs:
            print(func, func.bindtoname, 'recall' in dir(func) )
            if func.bindtoname == bizreq.cmd and 'recall' in dir(func):
                recallfunc = func.recall
                recallfunc(self, package)
        
    def send(self, bizreq: BizRequest):
        self.sessservice.send(self._pack_req(bizreq))
        
    
    
    def process_input(self, inputs: str):
        if len(inputs.strip()) <= 0: return
        splits = inputs.split()
        cmd, params = splits[0], splits[1:]
        # print(splits)
        # print(self.acfuncs)
        for func in self.acfuncs:
            # print(cmd)
            if func.invoke(cmd, self.atstate):
                # print(cmd)
                func(inputs, *params)
                break
            

    
    
    
    
    
    
    
class Server(ServerBizService):
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        
    @bizserv(atstate=State.Hall)
    def testchat(self, user: User, bizreq: BizRequest) -> BizResponse:
        msg = bizreq.param
        return BizResponse(msg, msg)
    
    @bizserv(atstate=State.Hall)
    def connectuser(self, user: User, bizreq: BizRequest) -> BizResponse:
        user.name = bizreq.param
        return BizResponse(f"Welcome {bizreq.param}", f"{bizreq.param} comes")
    
    
    
    
class Client(ClientBizService):
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        
    def show_msg(self, package):
        print(f"show {package.get_field('param')}")
        
    def show_all(self, package):
        print(f"show all {package.get_field('param')}")
        
    
    @bizclnt(state=State.IDLE,
             bindto=Server.connectuser,
             recall=show_msg)
    def connect(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest(param="Alice")
    
    @bizclnt(state=State.IDLE, 
            invokeptn="^[^$].*",
            bindto=Server.testchat)
    def chat(self, inputs=None, *args, **kwargs) -> BizRequest:
        return BizRequest(param=inputs)
    
    
    
    
