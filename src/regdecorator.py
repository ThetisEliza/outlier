'''
Date: 2023-01-07 21:00:51
LastEditors: Xiaofei wxf199601@gmail.com
LastEditTime: 2023-01-07 22:29:06
FilePath: /outlier/src/regdecorator.py
'''
from func import FuncBase, State
from client import Client

def bizServerReg(bizfunc: FuncBase):
    def inner(fn):
        def decorate(*args, **kwargs):
            ret = fn(*args, **kwargs)
            return ret
        # Here is the final decoratored function print(decorate)
        decorate.tag = bizfunc
        return decorate
    return inner

INFO = FuncBase("info", State.Hall, True, localrecall=Client.showretmsg)
# ROOM = FuncBase("room", State.Hall, True, localrecall=Client.showretmsg, servereffectaction=ClientConn.changeroom)


FuncConfig = [ INFO ]

ClientFuncMap = {
    func._statusname: func for func in FuncConfig
}

ClientRecallMap = {
    func._retname : func for func in FuncConfig
}

ServerFuncMap = {
    func._cmd : func for func in FuncConfig
}


print(FuncConfig)
print(ClientFuncMap)
print(ClientRecallMap)
print(ServerFuncMap)


import inspect

def ClassReg(cls: type):
    print("reg")
    for name, func in  inspect.getmembers(cls, predicate=inspect.isfunction):
        print(name, func)
        if 'tag' in dir(func) and func.tag is not None:
            BizFunc = func.tag
            BizFunc._kwargs['servereffectaction'] = func
            print(f"register fn {func} at {BizFunc} finished")
            
    return cls


# @ClassReg
# class A:
#     def __init__(self, a, b) -> None:
#         self.a = a
#         self.b = b
        
#     @bizServerReg(INFO)
#     def b(self):
#         print("b")
        
#     @bizServerReg(INFO)
#     def c(self):
#         print("c")
        
#     @bizServerReg(INFO)
#     def d(self):
#         print("d")
    
# A.b.tag = "s"
# A.c.tag = "s"
# A.d.tag = "s"

# a = A(1, 2)
# print(a)

# print(INFO)

@bizServerReg(INFO)
def c():
    print("c")
    return "cret"
    
print(c())