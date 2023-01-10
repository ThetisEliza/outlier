'''
Date: 2023-01-07 21:00:51
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-10 18:08:13
FilePath: /outlier/src/regdecorator.py
'''
import logging
from func import FuncBase, State

import inspect
# import logging

# Server Decorators

def bizFuncServerReg(*bizfunc: FuncBase):
    def inner(fn):
        def decorate(*args, **kwargs):
            ret = fn(*args, **kwargs)
            return ret
        # Here is the final decoratored function print(decorate)
        decorate.tag = bizfunc
        return decorate
    return inner


def ServerClassReg(cls: type):
    print("Server register bussiness functions")
    for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        if 'tag' in dir(func) and func.tag is not None:
            for BizFunc in func.tag:
                BizFunc._kwargs['servereffectaction'] = func
                print(f"register fn {func} at {BizFunc} finished")
    return cls



# Client Decorators

def bizFuncClientRequestReg(*bizfunc: FuncBase):
    def inner(fn):
        def decorate(*args, **kwargs):
            ret = fn(*args, **kwargs)
            return ret
        # Here is the final decoratored function print(decorate)
        decorate.localactiontag = bizfunc
        return decorate
    return inner

def bizFuncClientRecallReg(*bizfunc: FuncBase):
    def inner(fn):
        def decorate(*args, **kwargs):
            ret = fn(*args, **kwargs)
            return ret
        # Here is the final decoratored function print(decorate)
        decorate.recalltag = bizfunc
        return decorate
    return inner


def ClientClassReg(cls: type):
    logging.debug("Client register bussiness functions")
    for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        if 'localactiontag' in dir(func) and func.localactiontag is not None:
            for BizFunc in func.localactiontag:
                BizFunc._kwargs['localaction'] = func
                logging.debug(f"register fn {func} at {BizFunc} finished")
        if 'recalltag' in dir(func) and func.recalltag is not None:
            for BizFunc in func.recalltag:
                BizFunc._kwargs['localrecall'] = func
                logging.debug(f"register fn {func} at {BizFunc} finished")
    return cls

