import time
from typing import Callable
import os
import logging

def onexit(func: Callable):
    def wrapped_func(*args, **kwargs):
        logging.debug(f"Exiting calling {func}")
        func(*args, **kwargs)
        time.sleep(0.1)
        print("Exited Bye")
        os._exit(0)
    return wrapped_func
