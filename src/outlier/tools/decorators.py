
def singleton(clazz):
    """A class decorator to make a class as singleton

    Args:
        clazz (_type_): _description_

    Returns:
        _type_: _description_
    """
       
    clazz.ins = None
    clazz.inited = False
    clazz.origin_init = clazz.__init__
    
    
    def wrappednew(cls, *args, **kwargs):
        if clazz.ins is None:
            clazz.ins = super(clazz, cls).__new__(cls)
        return clazz.ins
    
    def wrappedinit(self, *args, **kwargs):
        if not clazz.inited:
            clazz.origin_init(self, *args, **kwargs)
            clazz.inited = True
            
    
    clazz.__new__ = wrappednew
    clazz.__init__ = wrappedinit
    # print(clazz)
    # z = clazz()
    # print(z)
    return clazz
