from enum import Enum
from dataclasses import dataclass

class Ops(Enum):
    ADD = 0
    RMV = 1
    RCV = 2


class Event:
    def __init__(self) -> None:
        self.op:  Ops = None
        self.fd:  int = -1
        self.ts:  float = -1
        
    