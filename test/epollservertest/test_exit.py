import signal
import time
import os

def handler(a, b):
    exit(0)
    
signal.signal(signal.SIGINT, handler)

while True:
    print("Press ctrl+C")
    time.sleep(10)
