import sys
import os
from atexit import register
from typing import Tuple


class ChatTerminal:
    def __init__(self, log_file_name = None) -> None:
        self.buffer = []
        self.history = []
        self.his_idx = 0
        self.cursor_idx = 0
        self.f = open(log_file_name, 'w') if log_file_name else None

    def _readkey(self) -> Tuple[bytes, bytes]:
        ...
        
    def _insert(self, char: bytes, idx: int) -> None:
        ...

    def _deleteformer(self, idx: int) -> None:
        ...
        
    def _delete(self, idx: int) -> None:
        ...
        
    def _output(self) -> None:
        ...
        
    def _move_cursor(self, idx: int) -> None:
        if 0 <= idx <= len(self.buffer):
            ...
        
    def _write_to(self, msg: str):
        if self.f: os.write(self.f.fileno(), f"{msg}\n".encode())
            
    def _parse_bytes(self, b: bytes) -> str:
        return "default"
        
    def input(self, prompt=">>>"):
        while True:
            a, b = self._readkey()
            instru = self._parse_bytes(b)
            
            self._write_to(f"check inputting msg {a} {b} {instru}\n")
            
            if instru == "backspace":
                self._deleteformer(self.cursor_idx)
                continue
            elif instru == "delete":
                self._delete(self.cursor_idx)
            elif instru == "home":
                self._move_cursor(0)
                continue
            elif instru == "end":
                self._move_cursor(len(self.buffer))
                continue
            elif instru == "right":
                self._move_cursor(self.cursor_idx + 1)
                continue
            elif instru == "left":
                self._move_cursor(self.cursor_idx - 1)
                continue
            elif instru == "up":
                ...
            elif instru == "down":
                ...
            elif instru == "enter":
                ...
            elif instru == "interrupt":
                raise KeyboardInterrupt()
            elif instru == "ignore":
                ...
            elif instru == 'default':    
                self._insert(a, self.cursor_idx)
                
        
    def output(self, output: str):
        ...
        

if sys.platform != 'win32':
    import termios
    import tty
    
    class PosixChatTerminal(ChatTerminal):
        def __init__(self, log_file_name=None) -> None:
            super().__init__(log_file_name)
            self.valid = False
            self.fd = sys.stdin.fileno()
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
            return c4, c1 + c2 + c3 + c4
            
        def _parse_bytes(self, b: bytes) -> str:
            if b == b'\x7f':        return 'backspace'
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
            
        
    ct = PosixChatTerminal("tmp/tmp.txt")
    

else:
    import msvcrt
    class WinChatTerminal(ChatTerminal):
        def __init__(self, log_file_name=None) -> None:
            super().__init__(log_file_name)
            
        def _readkey(self) -> Tuple[bytes, bytes]:
            def _readchar() -> bytes:
                return msvcrt.getch()

            c1 = _readchar()
            if c1 != b'\xe0':
                return c1, c1
            c2 = _readchar()
            return c2, c1 + c2
        
        def _parse_bytes(self, b: bytes) -> str:
            if b == b'\x08':  return 'backspace'
            if b == b'\xe0S': return 'delete'
            if b == b'\xe0K': return 'left'
            if b == b'\xe0M': return 'right'
            if b == b'\xe0H': return 'up'
            if b == b'\xe0P': return 'down'
            if b == b'\xe0G': return 'home'
            if b == b'\xe0O': return 'end'
            if b[:1] == b'\xe0': return 'ignore'
            return super()._parse_bytes(b)
        
    ct = WinChatTerminal("tmp\\tmp.txt")

# while True:
#     a,b = ct._readkey()
#     if a == b'q':
#         break

ct.input()