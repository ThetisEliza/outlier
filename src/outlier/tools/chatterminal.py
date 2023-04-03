import sys
import os
from typing import Tuple
import signal

class ChatTerminal:
    def __init__(self, log_file_name = None) -> None:
        self.buffer = []
        self.history = []
        self.his_idx = 0
        self.cursor_idx = 0
        self.f = open(log_file_name, 'w') if log_file_name else None

    def _readkey(self) -> Tuple[bytes, bytes]:
        ...
        
    
    def _upper_command(self):
        if 0 <= self.his_idx - 1 < len(self.history):
            self.his_idx -= 1
            sys.stdout.write("\r"+" "*3*len(self.buffer))
            self.buffer.clear()
            self.buffer.extend(list(self.history[self.his_idx]))
            sys.stdout.write('\r'+''.join(self.buffer))
            self.cursor_idx = len(self.buffer)
            sys.stdout.flush()
            
            
    def _belower_command(self):
        if 0 < self.his_idx + 1 < len(self.history):
            self.his_idx += 1
            sys.stdout.write("\r"+" "*3*len(self.buffer))
            self.buffer.clear()
            self.buffer.extend(self.history[self.his_idx])
            sys.stdout.write('\r'+''.join(self.buffer))
            self.cursor_idx = len(self.buffer)
            sys.stdout.flush()
            
        elif self.his_idx + 1 == len(self.history):
            self.his_idx += 1
            sys.stdout.write("\r"+" "*3*len(self.buffer))
            self.buffer.clear()
            self.buffer.extend([])
            sys.stdout.write('\r'+''.join(self.buffer))
            self.cursor_idx = len(self.buffer)
            sys.stdout.flush()
            
        
    def _insert(self, char: bytes, idx: int) -> None:
        self.buffer.insert(idx, char.decode())
        refresh_chars = ''.join(self.buffer[idx:])
        sys.stdout.write(refresh_chars)
        sys.stdout.write('\r'+''.join(self.buffer[:idx+1]))
        sys.stdout.flush()
        self.cursor_idx += 1

    def _deleteformer(self, idx: int) -> None:
        if 0 <= idx < len(self.buffer):
            self.buffer.pop(idx)
            self._write_to(f"Check buffer {self.buffer}")
            sys.stdout.write('\r'+''.join(self.buffer)+" ")
            sys.stdout.write('\r'+''.join(self.buffer[:idx]))
            sys.stdout.flush()
            self.cursor_idx -= 1
        
    def _delete(self, idx: int) -> None:
        if 0 <= idx < len(self.buffer):
            self.buffer.pop(idx)
            sys.stdout.write('\r'+''.join(self.buffer) + " ")
            sys.stdout.write('\r'+''.join(self.buffer[:idx]))
            sys.stdout.flush()
        
    def _output(self) -> str:
        self.cursor_idx = 0
        outputstr = "".join(self.buffer)
        sys.stdout.write("\r"+ " "*len("".join(self.buffer).encode()))
        self.buffer.clear()
        sys.stdout.write("\r")
        if len(outputstr):
            self.history.append(outputstr)
            self.his_idx = len(self.history)
        sys.stdout.flush()
        self._write_to(f"Check history {self.history}")
        return outputstr
        
    def _move_cursor(self, idx: int) -> None:
        if 0 <= idx <= len(self.buffer):
            sys.stdout.write('\r'+''.join(self.buffer[:idx]))
            self.cursor_idx = idx
        
    def _write_to(self, msg: str):
        if self.f: os.write(self.f.fileno(), f"{msg}\n".encode())
            
    def _parse_bytes(self, b: bytes) -> str:
        return "default"
        
    def input(self, prompt=">>>") -> str:
        while True:
            a, b = self._readkey()
            instru = self._parse_bytes(b)
            
            self._write_to(f"check inputting msg {a} {b} {instru}\n")
            
            if instru == "backspace":
                self._deleteformer(self.cursor_idx - 1)
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
                self._upper_command()
            elif instru == "down":
                self._belower_command()
            elif instru == "enter":
                ot = self._output()
                return ot
            elif instru == "interrupt":
                os.kill(os.getpid(), signal.SIGINT)
            elif instru == "ignore":
                ...
            elif instru == 'default':    
                self._insert(a, self.cursor_idx)
                
        
    def output(self, output: str) -> None:
        if len(self.buffer):
            sys.stdout.write("\r"+ " "*len("".join(self.buffer).encode()))
            sys.stdout.write(f'\r{output}\n\r')
            sys.stdout.write("\r"+"".join(self.buffer))
            self._move_cursor(self.cursor_idx)
        else:
            sys.stdout.write(f'\r{output}\n\r')
        sys.stdout.flush()
        
        

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
            
        
    ct = PosixChatTerminal()
    

else:
    import msvcrt
    class WinChatTerminal(ChatTerminal):
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
        
    ct = WinChatTerminal()
