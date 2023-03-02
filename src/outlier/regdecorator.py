'''
Date: 2023-01-07 21:00:51
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-01-10 18:08:13
FilePath: /outlier/src/regdecorator.py
'''
import inspect
import logging

from .func import FuncBase


def serverbizfunc(*bizfunc: FuncBase):
    """
    This decorator is to regesiter bizfuncs on server, to response the request from client
    """
    def inner(fn):
        def decorate(*args, **kwargs):
            return fn(*args, **kwargs)
        decorate.tag = bizfunc
        return decorate
    return inner


def Serverbiz(cls: type) -> type:
    """
    This decorator is to designate server class as the path to search for biz funcs
    Args:
        cls (type): _description_

    Returns:
        type: _description_
    """
    logging.info("Server register bussiness functions")
    for name, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        if 'tag' in dir(func) and func.tag is not None:
            for bizfunc in func.tag:
                bizfunc._kwargs['servereffectaction'] = func
                logging.info(f"register fn {func} at {bizfunc} name {name} finished")
    return cls



def clientbizfunreq(*bizfunc: FuncBase):
    def inner(fn):
        def decorate(*args, **kwargs):
            ret = fn(*args, **kwargs)
            return ret
        # Here is the final decoratored function print(decorate)
        decorate.localactiontag = bizfunc
        return decorate
    return inner

def clientbizfuncrecall(*bizfunc: FuncBase):
    def inner(fn):
        def decorate(*args, **kwargs):
            ret = fn(*args, **kwargs)
            return ret
        # Here is the final decoratored function print(decorate)
        decorate.recalltag = bizfunc
        return decorate
    return inner


def Clientbiz(cls: type):
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

