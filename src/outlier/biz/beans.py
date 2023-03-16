'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-12 20:12:28
FilePath: /outlier/src/outlier/biz/beans.py
'''
from dataclasses import dataclass
from datetime import datetime
from typing import List



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
        self.lastact: float             = datetime.now().timestamp()
        Room.index += 1
        
    
    def __repr__(self) -> str:
        l = ("PSWD" if self.passwd else "FREE")
        return f"{'room:'+str(self.name):10}\t{l}\t{self.connects}\t{len(self.history)}"
    
    @staticmethod
    def header():
        return f"{'name':10}\t{'LOCK'}\tpeople\tmsg"
    