from session.sessionservice import SessionService, Package, Session
from transmission.tcpservice import Ops
from dataclasses import dataclass
from typing import List, Any, Tuple, Generic, TypeVar, Callable, Dict, Union
from enum import Enum
import inspect



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
class BizReq:
    cmd:        str = None
    name:       str = None
    param:      Any = None
    


@dataclass
class BizResponse:
    response:   str = ""
    bcresponse: str = None



class ServerBizService:
    ...





# @dataclass
# class ChatMessage:
#     content: str
#     ts:      float
#     sender:  str

@dataclass
class User:
    sess: Session
    name: str
    syncts: float 
    
# class Room:
#     name: str = ""
#     pswd: str = ""
#     users: List['User']  = list()
#     histories: List[ChatMessage] = list()


class BizService:
    def __init__(self, sessservice: SessionService) -> None:
        self.sessservice = sessservice
        self.regbizfuncs: List[Callable] = list()
        
    def _send(self, user: User, biz: Union[BizResponse, BizReq]):
        pass
        
        
    def _rchandle(self, ops: Ops, session: Session, package: Package, *args):
        pass
        

    def _pack_req(self, bizreq: BizReq) -> Package:
        ...
        
    def _unpack_req(self, func: Callable, package: Package) -> BizReq:
        return BizReq(package.get_field("cmd"), package.get_field("name"), package.get_field("param"))


    def _pack_resp(self, bizresps: BizResponse) -> Tuple[Package, Package]:
        return Package.buildpackage().add_field("resp", bizresps.response) if bizresps.response is not None else None, \
            Package.buildpackage().add_field("resp", bizresps.bcresponse) if bizresps.bcresponse is not None else None

        
    def _unpack_resp(self, package: Package) -> BizResponse:
        return BizResponse(response=package.get_field("resp"))



class ServerBizService(BizService):
    
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        sessservice.set_upper_rchandle(self._rchandle)
        self.users: Dict[int, User] = dict()
        self.bizfuncs: Dict[str, Callable] = dict()
        for name, func in inspect.getmembers(ServerBizService, predicate=inspect.isfunction):
            if 'wrapped' in dir(func):
                print(f"{name} registered on {func}")
                self.bizfuncs[name] = func
        
        
       
    def getBizFunc(self, package: Package) -> Callable:
        bizfuncname = package.get_field('cmd')
        bizfunc = self.bizfuncs.get(bizfuncname)
        return bizfunc
    
        
    def _rchandle(self, ops: Ops, session: Session, package: Package, *args):
        if ops == Ops.Add:
            self.users[session.conn.sock.fileno()] = User(session, "default", -1)
        elif ops == Ops.Rmv:
            remove_key = -1
            for k, v in self.users.items():
                if v.sess.conn.addr == session.conn.addr:    
                    remove_key = k
            if remove_key > 0:
                self.users.pop(remove_key)
        elif ops == Ops.Rcv:
            user: User = self.users.get(session.conn.sock.fileno())
            bizfunc: Callable = self.getBizFunc(package)
            
            if bizfunc is not None:
                bizreq:  BizReq  = self._unpack_req(bizfunc, package)
                bizResponse: BizResponse = bizfunc(self, user, bizreq)
                self._send(user, bizResponse)
            else:
                print("No biz func found")
        
        clients = [f"{k} -> {v.name}[{v.sess.conn.addr}]" for k, v in self.users.items()]
        print(f"Live clients {clients}")
    
    def _send(self, user: User, biz: Union[BizResponse, BizReq]):
        bizresponse: BizResponse = biz
        self.sessservice.send(user.sess if user is not None else None, *self._pack_resp(bizresponse))

    def bizservEx(atstate: State=None, swtstate: State = None, cmdptn=None, **kwargs):
        """Todo maybe we can come later to fix this problem, to make fn inserted in 
        BizFunc and make new BizFunc still a member of the owner of fn.

        Args:
            atstate (State): _description_
            swtstate (State, optional): _description_. Defaults to None.
            cmdptn (_type_, optional): _description_. Defaults to None.
        """
        def inner(fn: Callable):
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            wrapper.__qualname__ = fn.__qualname__
            wrapper.__setattr__("wrapped", "server")
            wrapper.__setattr__("_atstate", atstate)
            wrapper.__setattr__("_stateto", swtstate)
            wrapper.__setattr__("_cmdptn", cmdptn)
            wrapper.__setattr__("_kwargs", kwargs)
            # wrapper.__call__ = fn.__call__
            return wrapper
        return inner

    
    @bizservEx(atstate=State.Hall)
    def connectuser(self, user: User, bizreq: BizReq) -> BizResponse:
        user.name = bizreq.name
        return BizResponse(f"Welcome {bizreq.name}", None)
        
    
    # @bizservEx(atstate=State.Hall)
    def disconnectuser(self, user: User, bizreq: BizReq) -> BizResponse:
        # user.name = biz
        ...
        
    def enteruser(self, ) -> BizResponse:
        ...
        
    @bizservEx(atstate=State.Hall)
    def testchat(self, user: User, bizreq: BizReq) -> BizResponse:
        msg = bizreq.param
        return BizResponse(msg, msg)
        
    
    def newroom(self, user: User, bizreq: BizReq):
        ...
        
    def destroyroom(self, user: User, bizreq: BizReq) -> BizResponse:
        ...
        
    def enterroom(self, user: User, bizreq: BizReq) -> BizResponse:
        ...
        
    def gethallinfo(self, user: User, bizreq: BizReq) -> BizResponse:
        ...
        
    def getroominfo(self, user: User, bizreq: BizReq) -> BizResponse:
        ...
        



def clntbiz(state:State, invoke:Callable[..., bool],  bindto: Callable = None, **kwargs):
    def inner(fn: Callable):
        def wrapper(bizservice: 'ClientBizService', *args, **kwargs):
            bizreq: BizReq = fn(bizservice, *args, **kwargs)
            
            if bindto is not None:
                package = Package.buildpackage().add_cmd(bindto.__qualname__.partition('.')[-1])
                package.add_field_if(bizreq.name is not None, "name", bizreq.name)
                package.add_field_if(bizreq.param is not None, "param", bizreq.param)
                bizservice._send(None, package)
            else:
                print(bizreq.param)
            
        wrapper.__qualname__ = fn.__qualname__
        wrapper.__setattr__("wrapped", "clnt")
        wrapper.__setattr__("invoke", invoke)
        if bindto is not None:
            print(f"{fn} binds to {bindto.__qualname__}")
            wrapper.__setattr__("atstate", bindto._atstate)
        return wrapper
    return inner



            


class ClientBizService(BizService):
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        sessservice.set_upper_rchandle(self._rchandle)
        self.bizfuncs: Dict[str, Callable] = dict()
        for name, func in inspect.getmembers(ClientBizService, predicate=inspect.isfunction):
            if 'invoke' in dir(func):
                print(f"{name} registered on {func}")
                invoke = func.invoke
                self.bizfuncs[invoke] = func
        
        
        
    def _rchandle(self, ops: Ops, session: Session, package: Package, *args):
        bizresponse = self._unpack_resp(package)
        print(bizresponse.response)
        
        
    def _send(self, user: User, package: Package):
        self.sessservice.send(package)



    def process_input(self, inputs: str):
        inputs = inputs.split()
        cmd, params = inputs[0], inputs[1:]
        print(cmd, params)
        biz = self.bizfuncs.get(cmd)
        print(biz)
        biz(self, *inputs[1:])
        


    @clntbiz(bindto=ServerBizService.connectuser)
    def connectuser(self, *args, **kwargs) -> BizReq:
        return BizReq(name="Alice")
    
    
    
    @clntinvoke("$chat")
    @clntbiz(bindto=ServerBizService.testchat)
    def chat(self, *args, **kwargs) -> BizReq:
        msg = args[0] if len(args) > 0 else ""
        return BizReq(param=msg)
        
    
    @clntinvoke("$help")
    @clntbiz()
    def help(self, *args, **kwargs) -> BizReq:
        return BizReq(param="HHHHH")