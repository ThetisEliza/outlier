from session.sessionservice import SessionService, Package, Session
from dataclasses import dataclass
from typing import List, Any, Tuple, Generic, TypeVar, Callable
from enum import Enum



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
    @bizclnt
    def bizfuncA:
    
    @bizclnt
    def bizfuncB:

'''




class State(Enum):
    
    Hall = 0
    Room = 1
    Cfrm = 2

@dataclass
class BizReq:
    request: str = None
    


@dataclass
class BizResponse:
    response:   str = ""
    bcresponse: str = None




T = TypeVar("T", bound=Any)

class BizFunc():
    def __init__(self,
                 command:   str,
                 atstate:   str,
                 isrmt:     bool    = False,
                 cmdptn:    str     = None,
                 stateto:   State   = 0,
                 *args, **kwargs) -> None:
        
        self._command   = command
        self._atstate   = atstate
        self._isrmt     = isrmt
        self._stateto   = stateto
        self._cmdptn    = cmdptn
        self._stateto   = stateto
        self._args      = args
        self._kwargs    = kwargs

    @property
    def _statusname(self):
        return f"{self._command}@{self._atstate}"

    @property
    def _retname(self):
        return f"~{self._command}"
    
    @property
    def _help(self):
        usage =  self._kwargs.get("usage", None)
        usage =  (self._command + ((" "+self._kwargs.get("descparams", "")) if "descparams" in self._kwargs else "")) if usage is None else usage
        return "\t"+self._command +"\t" + self._kwargs.get("desc", "") + "\n\t\t-Usage:\t" + usage
    
    
    # def clntact(self, bizservice: 'BizService', *args, **kwargs):
    #     if self._isrmt:
    #         bizservice._send()
    
    
    # def clntrc(self, bizservice: 'BizService', *args, **kwargs):
    #     bizservice._rchandle(args, kwargs)
        
        
    # def srvrc(self, bizservice: 'BizService', *args, **kwargs):
        
    #     bizservice._rchandle(args, kwargs)

# def servicebizfunc(*)

@dataclass
class ChatMessage:
    ...




class User:
    sess: Session
    name: str
    syncts: float 
    
class Room:
    name: str = ""
    pswd: str = ""
    users: List['User']  = list()
    histories: List[str] = list()


class BizService:
    def __init__(self, sessservice: SessionService) -> None:
        self.sessevice = sessservice
        self.regbizfuncs: List[BizFunc] = list()
        
    def _send(self, user: User, bizresp: BizResponse):
        self.sessevice.send(user.sess, self.__pack(bizresp.response), self.__pack(bizresp.response))
        
        
    def _rchandle(self, user: User, bizreq: BizReq):
        ...
        

    def __pack(resp: str = None) -> Package:
        return Package.buildpackage().add_cmd("resp", resp) if resp else None



class ServerBizService(BizService):
    
    def __init__(self, sessservice: SessionService) -> None:
        super().__init__(sessservice)
        
        
    def _rchandle(self, user: User, bizreq: BizReq):
        ...
        # get func from bizreq  bizfunc: Callable
        # use it!  bizResponse = bizfunc(bizreq.args)
        # send back! send(user, bizResponse)
        bizfunc: BizFunc = self.getBizFunc(bizreq)
        BizResponse = bizfunc.srvrc()
        
    
    def response(self, package: Package) -> BizResponse:
        ...       
        
    def connectuser(self, ) -> BizResponse:
        ...
        
    def disconnectuser(self, ) -> BizResponse:
        ...
        
    def enteruser(self, ) -> BizResponse:
        ...
        
        
    
    def newroom(self, ):
        ...
        
    def destroyroom(self, ) -> BizResponse:
        ...
        
    def enterroom(self) -> BizResponse:
        ...
        
    def gethallinfo(self) -> BizResponse:
        ...
        
    def getroominfo(self) -> BizResponse:
        ...
        

        
