import time
from typing import Callable

def onexit(func: Callable):
    def wrapped_func(*args, **kwargs):
        print(f"Exiting calling {func}")
        func(*args, **kwargs)
        time.sleep(0.1)
        print("Exited Bye")
        exit(0)
    return wrapped_func
