import os
import signal
import sys
from typing import Tuple, List
from wcwidth import wcswidth


class Terminal:
    def __init__(self, log_file_name = None) -> None:
        self.buffer: List[str] = []
        self.history = []
        self.his_idx = 0
        self.cursor_idx = 0
        self.active = True
        self.f = open(log_file_name, 'w') if log_file_name else None
        self.fd = sys.stdout.fileno()

    def _readkey(self) -> Tuple[bytes, bytes]:
        ...
        
    def _up(self):
        if 0 <= self.his_idx - 1 < len(self.history):
            self.his_idx -= 1
            self.buffer.clear()
            self.buffer.extend(list(self.history[self.his_idx]))
            self.rewrite_line(f'\r{self.prompt}' +''.join(self.buffer))
            self.cursor_idx = len(self.buffer)
            sys.stdout.flush()
        
    def _down(self):
        self.buffer.clear()
        if 0 < self.his_idx + 1 < len(self.history):
            self.his_idx += 1
            self.buffer.extend(self.history[self.his_idx])
        elif self.his_idx + 1 == len(self.history):
            self.his_idx += 1
            self.buffer.extend([])
        
        self.rewrite_line(f'\r{self.prompt}' + ''.join(self.buffer))
        self.cursor_idx = len(self.buffer)
        sys.stdout.flush()
            
    def _get_len(self, a: str):
        return wcswidth(a)
        
    def _left(self):
        if self.cursor_idx > 0:
            left_len = self._get_len(self.buffer[self.cursor_idx -1])
            self.cursor_idx -= 1
            for _ in range(left_len):
                os.write(self.fd, b'\x1b[D')
        
    def _right(self):
        if self.cursor_idx < len(self.buffer):
            right_len = self._get_len(self.buffer[self.cursor_idx])
            self.cursor_idx += 1
            for _ in range(right_len):
                os.write(self.fd, b'\x1b[C')
                
    def _reset_cursor_after_full_output(self):
        shift_len = self._get_len("".join(self.buffer[self.cursor_idx:]))
        self._write_spec_char(b'\x1b[D', shift_len)
        # self.cursor_idx = 0
        
    def _home(self):
        shift_len = self._get_len("".join(self.buffer[:self.cursor_idx]))
        self._write_spec_char(b'\x1b[D', shift_len)
        self.cursor_idx = 0
        
    def _end(self):
        shift_len = self._get_len("".join(self.buffer[self.cursor_idx:]))
        self._write_spec_char(b'\x1b[C', shift_len)
        self.cursor_idx = len(self.buffer)
        
    def _insert(self, char: bytes) -> None:
        self.buffer.insert(self.cursor_idx, char.decode())
        self.cursor_idx += 1
        os.write(self.fd, char)
        os.write(self.fd, "".join(self.buffer[self.cursor_idx:]).encode())
        shift_len = self._get_len("".join(self.buffer[self.cursor_idx:]))
        self._write_spec_char(b'\x1b[D', shift_len)
        
    def _delete(self) -> None:
        if 0 <= self.cursor_idx < len(self.buffer):
            self.buffer.pop(self.cursor_idx)
            self._write_spec_char(b'\x1b[K')
            shift_len = self._get_len("".join(self.buffer[self.cursor_idx:]))
            os.write(self.fd, "".join(self.buffer[self.cursor_idx:]).encode())
            self._write_spec_char(b'\x1b[D', shift_len)
        
    def _delete_former(self) -> None:
        if 0 <= self.cursor_idx - 1 < len(self.buffer):
            shift_len = self._get_len(self.buffer[self.cursor_idx - 1])
            self.buffer.pop(self.cursor_idx - 1)
            self._write_spec_char(b'\x1b[D', shift_len)
            self._write_spec_char(b'\x1b[K')
            shift_len = self._get_len("".join(self.buffer[self.cursor_idx - 1:]))
            os.write(self.fd, "".join(self.buffer[self.cursor_idx - 1:]).encode())
            self._write_spec_char(b'\x1b[D', shift_len)
            self.cursor_idx -= 1
        
    def _write_spec_char(self, char: bytes, times: int = 1) -> None:
        if times > 0:
            for _ in range(times):
                os.write(self.fd, char)
        
    def _write_to(self, msg: str):
        if self.f: os.write(self.f.fileno(), f"{msg}\n".encode())
        
    def _write_buffer_details(self):
        self._write_to(f"{self.buffer}, {self.buffer}, {self.cursor_idx}")
        
    def _parse_bytes(self, b: bytes) -> str:
        return "default"
    
    def _input_confirm(self) -> str:
        self.cursor_idx = 0
        outputstr = "".join(self.buffer)
        # self.rewrite_line(f"\r{outputstr}")
        self.buffer.clear()
        sys.stdout.write('\r\n')
        if len(outputstr):
            self.history.append(outputstr)
            self.his_idx = len(self.history)
        sys.stdout.flush()
        self._write_to(f"Check history {self.history}")
        return outputstr
    
    
    def input(self, prompt = ">>> "):
        self.rewrite_line('\r')
        self.rewrite_line(prompt)
        self.prompt = prompt
        while self.active:
            a, b = self._readkey()
            instru = self._parse_bytes(b)
            self._write_to(f"check inputting msg {a} {b} {instru}\n")

            if instru == "backspace":
                self._delete_former()
            elif instru == "delete":
                self._delete()
            elif instru == "home":
                self._home()
            elif instru == "end":
                self._end()
            elif instru == "right":
                self._right()
            elif instru == "left":
                self._left()
            elif instru == "up":
                self._up()
            elif instru == "down":
                self._down()
            elif instru == "enter":
                return self._input_confirm()
            elif instru == "interrupt":
                os.kill(os.getpid(), signal.SIGINT)
            elif instru == "ignore":
                ...
            elif instru == 'default':    
                self._insert(a)
                
            self._write_buffer_details()        
            
    def output(self, output: str) -> None:
        output = str(output)
        output = output.replace('\n', '\r\n')
        sys.stdout.write('\r')
        self.rewrite_line(output)
        sys.stdout.write('\r\n')
        
        self.rewrite_line(self.prompt)
        sys.stdout.flush()
        
        if len(self.buffer):
            sys.stdout.write("".join(self.buffer))
            sys.stdout.flush()
            self._reset_cursor_after_full_output()
            pre_cursor_idx = self.cursor_idx
            self._home()
            for _ in range(pre_cursor_idx):
                self._right()
        sys.stdout.flush()
        self._write_buffer_details()
        
        
        
    def rewrite_line(self, line: str) -> None:
        os.write(self.fd, b'\x1b[2K')
        os.write(self.fd, line.encode())
        
        
    def rewrite_lines(self, *lines: str) -> None:
        lines_all = []
        for l in lines:
            lines_all.extend(l.split("\n"))
        for l in lines_all:
            self.rewrite_line(f"\r{l}\n")
            
    def refresh_lines(self, *lines: str) -> None:
        self._write_spec_char(b'\x1b[2J')
        self.rewrite_lines(*lines)
        self.output("")
        
    def rewrite_rightside(self, line: str) -> None:
        ...

    def __del__(self):
        self.close()

    def close(self):
        self.active = False
        if self.f: self.f.close()


if sys.platform != 'win32':
    import termios
    import tty
    
    # @singleton
    class PosixTerminal(Terminal):
        def __init__(self, log_file_name=None) -> None:
            super().__init__(log_file_name)
            self.valid = False
            try:
                self.settings = termios.tcgetattr(self.fd)
                self.valid = True
            except:
                self.settings = None
                self.valid = False
    
        def _readkey(self) -> Tuple[bytes, bytes]:
            def _readchar() -> bytes:
                if self.valid:
                    try:
                        tty.setraw(self.fd)
                        ch = sys.stdin.read(1)
                    except:
                        print("tty ends")
                    finally:
                        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.settings)
                    return ch.encode()
                else:
                    ch = sys.stdin.read(1)
                    return ch.encode()

            c1 = _readchar()
            if c1 != b'\x1b':
                return c1, c1
            c2 = _readchar()
            if c2 != b'\x5b':
                return c2, c1 + c2
            c3 = _readchar()
            if c3 != b'6' and c3 != b'5' and c3 != b'3':
                return c3, c1 + c2 + c3
            c4 = _readchar()
            return     c4, c1 + c2 + c3 + c4
        
        def _parse_bytes(self, b: bytes) -> str:
            if b == b'\x7f':        return 'backspace'
            if b == b'\r':          return 'enter'
            if b == b'\x1b[3~':     return 'delete'
            if b == b'\x1b[D':      return 'left'
            if b == b'\x1b[C':      return 'right'
            if b == b'\x1b[A':      return 'up'
            if b == b'\x1b[B':      return 'down'
            if b == b'\x1b[H':      return 'home'
            if b == b'\x1b[F':      return 'end'
            if b == b'\x03':        return "interrupt"
            if b[:2] == b'\x1b[':   return 'ignore'
            return super()._parse_bytes(b)
        
        def close(self):
            super().close()
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.settings)
            
    terminal = PosixTerminal()
            
else:
    import msvcrt
    class WinTerminal(Terminal):
        def __init__(self, log_file_name=None) -> None:
            super().__init__(log_file_name)
            self.valid = True
            
        def _readkey(self) -> Tuple[bytes, bytes]:
            def _readchar() -> bytes:
                return msvcrt.getwch().encode()

            c1 = _readchar()
            if c1 != b'\xc3\xa0':
                return c1, c1
            c2 = _readchar()
            return c2, c1 + c2
        
        def _parse_bytes(self, b: bytes) -> str:
            if b == b'\x08':            return 'backspace'
            if b == b'\r':              return 'enter'
            if b == b'\xc3\xa0S':       return 'delete'
            if b == b'\xc3\xa0K':       return 'left'
            if b == b'\xc3\xa0M':       return 'right'
            if b == b'\xc3\xa0H':       return 'up'
            if b == b'\xc3\xa0P':       return 'down'
            if b == b'\xc3\xa0G':       return 'home'
            if b == b'\xc3\xa0O':       return 'end'
            if b == b'\x03':            return "interrupt"
            if b[:-1] == b'\xc3\xa0':   return 'ignore'
            return super()._parse_bytes(b)
        
    terminal = WinTerminal()
    
    
# import asyncio
# import random
# import time 

# async def request(req: str) -> str:
#     await asyncio.sleep(1)
#     # print(f"resp from async {req}")
#     return f"resp from async {req}"

# def randommesssage() -> None:
#     while True:
#         time.sleep(random.random()*5)
#         terminal.output(f"random message {random.random()}")
        
    
# async def client():
#     # asyncio.to_thread(randommesssage)
#     while True:
#         c = terminal.input("$ ")
#         if len(c):
#             r = await request(c)
#             terminal.output(r)

# from threading import Thread

# a = Thread(target=randommesssage)
# a.daemon = True
# a.start()

# asyncio.get_event_loop().run_until_complete(client())
