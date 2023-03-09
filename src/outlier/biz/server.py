'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-09 14:13:29
FilePath: /outlier/src/outlier/biz/server.py
'''
import logging
from typing import List, Union
import time
from encryption.sessionservice import SessionService
from transmission.tcpservice import Ops
from biz.bizservice import ServerBizService,  BizRequest, BizResponse, User, bizserv
from biz.beans import ChatMessage,  Room
from datetime import datetime
from tools.threadpool import ThreadPool

class Server(ServerBizService):
    def __init__(self, sessservice: SessionService, **kwargs) -> None:
        super().__init__(sessservice, **kwargs)
        self.rooms: List[Room] = [Room("R1")]
        self.threadpool = ThreadPool()
        self.threadpool.put_task(self._room_guard)
        self.rooms[0].lastact = datetime.now().timestamp()
        
    def _findroom(self, _x: Union[str, int]) -> Union[Room, None]:
        for room in self.rooms:
            if (type(_x) == str and room.name == _x) or (type(_x) == int and room.group == _x):
                logging.debug(f"find Room {room}")
                return room
        return None
    
    def _createroom(self, name: str) -> Room:
        room = Room(name)
        self.rooms.append(room)
        return room
    
    def _findusers(self, room: Room) -> List[User]:
        return list(filter(lambda u: u.sess.group == room.group, self.users.values()))
    
    
    def _room_guard(self):
        max_idle = self.kwargs.get('roomgard', 1800)
        while True:
            rms = []
            for room in self.rooms:
                if room.lastact != -1 and datetime.now().timestamp() - room.lastact > max_idle:
                    logging.info(f"{Room} idled for {max_idle} closed")
                    for user in self._findusers(room):
                        self.leftroom(user, None)
                    rms.append(room)
            for room in rms:
                self.rooms.remove(room)        
            time.sleep(1)
        

    @bizserv()
    def chat(self, user: User, bizreq: BizRequest) -> BizResponse:
        searchroom = self._findroom(user.sess.group)
        if searchroom is not None:            
            searchroom.lastact = datetime.now().timestamp()
            searchroom.history.append(ChatMessage.parse(bizreq.param))
            return BizResponse(bizreq.param, bizreq.param, group=searchroom.group, inc=True)
        else:
            return BizResponse("error")
    
    
    @bizserv()
    def connectuser(self, user: User, bizreq: BizRequest) -> BizResponse:
        user.name = bizreq.param
        return BizResponse(f"Welcome {bizreq.param}")
    
    @bizserv()
    def infohall(self, user: User, bizreq: BizRequest) -> BizResponse:
        info = f"{Room.header()}\n" + "\n".join(map(str, self.rooms))
        return BizResponse(f"{info}", None)
    
    @bizserv()
    def enterroom(self, user: User, bizreq: BizRequest) -> BizResponse:
        name = bizreq.param
        room = self._findroom(name)
        if room is not None:
            room.lastact = datetime.now().timestamp()
            user.sess.group = room.group
            room.connects += 1
            return BizResponse(f"Enter room {room.name}", f"{user.name} entered", group=room.group, inc=False)
        else:
            room = self._createroom(name)
            room.lastact = datetime.now().timestamp()
            user.sess.group = room.group
            room.connects += 1
            return BizResponse(f"Create and enter room {room.name}", f"{user.name} entered", group=room.group, inc=False)
        
    
    @bizserv(rc=Ops.Rmv)
    def leftroom(self, user: User, bizreq: BizRequest) -> BizResponse:
        room = self._findroom(user.sess.group)
        if room is not None:
            user.sess.group = -1
            room.connects -= 1
            return BizResponse(f"leave room {room.name}", f"{user.name} left", group=room.group)
        else:
            return BizResponse()
        
    @bizserv()
    def roominfo(self, user: User, bizreq: BizRequest) -> BizResponse:
        room = self._findroom(user.sess.group)
        if room is not None:
            ret = f"Room: {room.name}\n"
            users = self._findusers(room)
            for u in users:
                ret += f"Connecting: {u.name}\tat {u.sess.conn.addr}\n"
            ret += f"room history message size: {len(room.history)}\n"
            return BizResponse(ret)
        else:
            return BizResponse('error')
        