# import asyncio

# async def tcp_echo_client(message):
#     reader, writer = await asyncio.open_connection(
#         '127.0.0.1', 22)

#     print(f'Send: {message!r}')
#     writer.write(message.encode())
#     await writer.drain()

#     data = await reader.read(100)
#     print(f'Received: {data.decode()!r}')

#     print('Close the connection')
#     writer.close()
#     await writer.wait_closed()

# asyncio.run(tcp_echo_client('Hello World!'))

import termios
import tty
import time
import sys
from threading import Thread


def dec():
    a = 1
    while True:
        sys.stdout.write(f'\rsleep {a}\n\r')
        time.sleep(1)
        a += 1

t = Thread(target=dec)
t.daemon = True
t.start()

settings = termios.tcgetattr(sys.stdin.fileno())
tty.setraw(sys.stdin.fileno())
while True:
    # try:
        
    ch = sys.stdin.read(1)
    # except:
    # print("tty ends")
    # finally:
        
    sys.stdout.write(f'\r{ch}')
    if ch == 'q':
        break
termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)