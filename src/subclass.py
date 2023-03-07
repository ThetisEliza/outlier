import inspect

class A:
    def __init__(self) -> None:
        # print(inspect.getmembers(self))
        for name, func in inspect.getmembers(self, inspect.ismethod):
            if '_' not in func.__qualname__:
                print(name, func)
                func()
            
    def a(self):
        print('a')
        
        
class B(A):
    
    
    
    def b(self):
        print('b')
        
B()