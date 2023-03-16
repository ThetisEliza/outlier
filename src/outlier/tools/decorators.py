'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-09 16:55:14
FilePath: /outlier/src/outlier/tools/decorators.py
'''
import time
from typing import Callable
import os
import logging

def onexit(func: Callable):
    def wrapped_func(*args, **kwargs):
        print("Exiting...")
        logging.debug(f"Exiting calling {func}")
        func(*args, **kwargs)
        time.sleep(1)
        print("Exited Bye")
        os._exit(0)
    return wrapped_func


def singleton(clazz):
    clazz.ins = None
    clazz.inited = False
    clazz.origin_init = clazz.__init__
    
    def wrappednew(cls, *args, **kwargs):
        if clazz.ins is None:
            # print(f"created cls {cls}")
            clazz.ins = super(clazz, cls).__new__(cls)
        return clazz.ins
    
    def wrappedinit(self, *args, **kwargs):
        if not clazz.inited:
            # print(f"init cls {self}")
            clazz.origin_init(self, *args, **kwargs)
            clazz.inited = True
            
    
    clazz.__new__ = wrappednew
    clazz.__init__ = wrappedinit
    return clazz
