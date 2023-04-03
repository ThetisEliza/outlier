'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-20 19:19:27
FilePath: \outlier\src\outlier\biz\bizservice.py

This is the key layer for bussniness implementation. We use server 
as the `stem` update way, client follows. we use some way to add the biz
respond function automatically and we use some way to make the client can
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
import inspect
import logging
import re
import signal
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List

from ..encryption.sessionservice import Package, Session, SessionService
from ..tools.chatterminal import ct
from ..tools.events import Ops

if ct.valid:
    print = ct.output
    input = ct.input

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
    """This decorator can make a method in server to be a busniess function
    and automatically do works around the method list as follows:
    1. Automatically registered in the server and handle the comming message
    if command inside corresponds.
    2. Send the response to client for the requesting client and broadcast the message
    for the group designated.
    3. Once `rc` is set, it can handle the corresponding Ops, if required.
    
    """
    def inner(fn: Callable[[BizService, User, BizRequest, Any], BizResponse]):
        def wrapper(bizservice, user: User, bizreq: BizRequest, *args, **kwargs):
            bizresp: BizResponse = fn(bizservice, user, bizreq, *args, **kwargs)
            bizresp.cmd = fn.__qualname__.partition('.')[-1]
            bizservice.send(user, bizresp)
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
        logging.debug(f"[Biz Layer]\trecall {ops} {session.conn.addr} {package}")
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
        bizfunc(user, bizreq)
        
        
        
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
    """This decorator can make a method in client to be a busniess function
    and automatically do works around the method list as follows:
    
    1. Automatically registered in the client.
    2. Send the request to the server
    3. Designate a state can be invoked
    4. Designate a invoke command or pattern
    5. Designate a responding method of the server
    6. Designate a recall method once the message comes from the server
    

    Args:
        state (State): _description_
        invoke (str, optional): _description_. Defaults to None.
        invokeptn (str, optional): _description_. Defaults to None.
        bindto (Callable, optional): _description_. Defaults to None.
        recall (Callable, optional): _description_. Defaults to None.
    """
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
                print(e)
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
            # logging.debug(f"{fn} binds to {bindto.__qualname__}")
            wrapper.__setattr__("bindtoname", bindto.__qualname__.partition(".")[-1])
            
        # set recall method to proc server response
        if recall is not None:
            # logging.debug(f"{fn} recall at {recall.__qualname__}")
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
                
