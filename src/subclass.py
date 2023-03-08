




class A:
    
    ins = None
    
    def __new__(cls):
        if A.ins is None:
            A.ins = super().__new__(cls)
        return A.ins

    
a = A()
b = A()
print(a)
print(b)