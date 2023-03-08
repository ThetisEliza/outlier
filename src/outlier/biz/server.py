import logging
from typing import List

from encryption.sessionservice import SessionService
from transmission.tcpservice import Ops
from biz.bizservice import ServerBizService,  BizRequest, BizResponse, User, bizserv
from biz.beans import ChatMessage,  Room



    
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