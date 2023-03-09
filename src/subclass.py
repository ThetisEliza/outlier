'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-09 11:39:31
FilePath: /outlier/src/subclass.py
'''

def dec(fn):
    def wrapper(*args, **kwargs):
        ret =  fn(*args, **kwargs)
        return ret
    return wrapper
        
        

def singleton(clazz):
    clazz.ins = None
    clazz.inited = False
    clazz.origin_init = clazz.__init__
    
    def wrappednew(cls, *args, **kwargs):
        if clazz.ins is None:
            print(f"created cls {cls}")
            clazz.ins = super(clazz, cls).__new__(cls)
        return clazz.ins
    
    def wrappedinit(self, *args, **kwargs):
        if not clazz.inited:
            print(f"init cls {self}")
            clazz.origin_init(self, *args, **kwargs)
            clazz.inited = True
            
    
    clazz.__new__ = wrappednew
    clazz.__init__ = wrappedinit
    return clazz


def singletoninject(*injects: type):
    def dec(clazz):
        clazz.ins = None
        clazz.inited = False
        clazz.origin_init = clazz.__init__
        
        
        def wrappednew(cls, *args, **kwargs):
            if clazz.ins is None:
                print(f"created cls {cls}")
                clazz.ins = super(clazz, cls).__new__(cls)
            return clazz.ins
        
        def wrappedinit(self, *args, **kwargs):
            if not clazz.inited:
                print(f"init cls {self}")
                clazz.origin_init(self, *args, **kwargs)
                
                
                print(f"try injecting {clazz}")
                print(f"try injecting {[cl.mro() for cl in injects]}")
                clazz.origin_init(self, *args, **kwargs)
            
                def inject_var(self, name, *injects):
                    for cl in injects:
                        for x in cl.mro():
                            print(name, cl.__name__)
                            if name.lower() == x.__name__.lower():
                                self.__setattr__(name, cl())
                                return
                            
                for name, obj in vars(self).items():
                    inject_var(self, name, *injects)
                clazz.inited = True
                
        
        clazz.__new__ = wrappednew
        clazz.__init__ = wrappedinit
        return clazz
    return dec


def inject(*cls: type):
    def dec(origin_init):
        def wrapped_init(self, *args, **kwargs):
            print(f"try injecting {cls}")
            print(f"try injecting {[cl.mro() for cl in cls]}")
            origin_init(self, *args, **kwargs)
            
            def inject_var(self, name, *cls):
                for cl in cls:
                    for x in cl.mro():
                        print(name, cl.__name__)
                        if name.lower() == x.__name__.lower():
                            self.__setattr__(name, cl())
                            return
                        
            for name, obj in vars(self).items():
                inject_var(self, name, *cls)
        return wrapped_init
    return dec
    

@singleton
class C:
    def __init__(self, *args, **kwargs) -> None:
        print("C inited")
        self.atr = 'atr'


class B:
    def __init__(self) -> None:
        ...
        
class B1(B):
    def __init__(self) -> None:
        super().__init__()


@singletoninject(C)
class B2(B):
    # @inject(C)
    def __init__(self) -> None:
        super().__init__()
        self.c = ...


@singletoninject(B2)
class A:
    def __init__(self) -> None:
        self.b = ...        

a = A()
a2 = A()
print(a.b.c)
print(a2.b.c)
