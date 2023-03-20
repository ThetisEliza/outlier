import sys


if sys.platform != 'win32':
    import termios
    import tty
    import os
    from atexit import register
    from .decorators import onexit, singleton

    MOVE_LEFT = (27, 91, 68)
    MOVE_RIGHT = (27, 91, 67)

    @singleton
    class ChatTerminal:
        def __init__(self, log_file_name = None) -> None:
            self.fd = sys.stdin.fileno()
            self.settings = termios.tcgetattr(self.fd)
            self.buffer = []
            self.history = []
            
            self.his_idx   = 0
            self.curse_idx = 0
            self.f = None
            if log_file_name:
                self.f = open(log_file_name, 'w')
            
        def _rdchar(self):
            try:
                tty.setraw(self.fd)
                ch = sys.stdin.read(1)
            except:
                print("tty ends")
            finally:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.settings)
            return ch
        
        def readkey(self):
            # some key input is a combination of `ESC`(0x1b) + `[` (0x5b) + other, such as up, down
            # getchar = getchar_fn or readchar
            c1 = self._rdchar()
            if ord(c1) != 0x1b:
                return c1, ()
            c2 = self._rdchar()
            if ord(c2) != 0x5b:
                return c1, ()
            c3 = self._rdchar()
            return chr(0x10 + ord(c3) - 65), (c1, c2, c3)
        
        
        def _insert(self, char, idx):
            self.buffer.insert(idx, char)
            sys.stdout.write('\r' + "".join(self.buffer))
            self.curse_idx = len(self.buffer)
            self._move_cursor(idx + 1)
            sys.stdout.flush()
            self._write_to("check inserted msg", self.curse_idx)   
            
        def _deleteformer(self, idx):
            if len(self.buffer) and idx - 1 < len(self.buffer):
                self.buffer.pop(idx - 1)
                sys.stdout.write('\r' + "".join(self.buffer) + " ")
                self.curse_idx = len(self.buffer) + 1
                sys.stdout.write('\b' * 1)
                self.curse_idx -= 1
                self._move_cursor(idx - 1)
            sys.stdout.flush()
            
        def _delete(self, idx):
            if len(self.buffer) and idx < len(self.buffer):
                self.buffer.pop(idx)
                sys.stdout.write('\r' + "".join(self.buffer) + " ")
                self.curse_idx = len(self.buffer) + 1
                sys.stdout.write('\b' * 1)
                self.curse_idx -= 1
                self._move_cursor(idx)
            sys.stdout.flush()
            
        def _output(self):
            outputs = "".join(self.buffer)
            self.curse_idx = 0
            self.history.append(outputs)
            self.buffer.clear()
            return outputs
            
        def _move_cursor(self, idx):
            
            def moveleft(n):
                for _ in range(n):
                    for c in MOVE_LEFT:
                        sys.stdout.write(chr(c))
                sys.stdout.flush()
                    
            def moveright(n):
                for _ in range(n):
                    for c in MOVE_RIGHT:
                        sys.stdout.write(chr(c))
                sys.stdout.flush()
                
            
            self._write_to(f"{self.curse_idx} move to idx {0} {idx} {len(self.buffer)} - {self.buffer}")    
            
            if 0 <= idx <= len(self.buffer):
                if self.curse_idx > idx:
                    moveleft(self.curse_idx - idx)
                else:
                    moveright(idx - self.curse_idx)    
                self.curse_idx = idx
                sys.stdout.flush()
            
        def _write_to(self, msg: str, *params):
            if self.f:
                os.write(self.f.fileno(), (msg+":"+"->".join(map(str, params))+"\n").encode())
        
        
        def chatinput(self, prompt = " >>> "):
            while True:
                key, seq = self.readkey()
                self._write_to(f"Check key input {ord(key)}", *seq)
                
                if ord(key) == 0x7F:   # backspace -> delete the former char
                    self._deleteformer(self.curse_idx)
                elif ord(key) == 126:     # delete -> delete the next char
                    self._delete(self.curse_idx)
                elif ord(key) == 23:     # Home  -> move to the first position
                    # self._delete(self.curse_idx)
                    self._move_cursor(0)
                elif ord(key) == 21:     # End   -> move to the last position
                    # self._delete(self.curse_idx)
                    self._move_cursor(len(self.buffer))
                elif ord(key) == 0x12:  # move right
                    self._move_cursor(self.curse_idx + 1)
                elif ord(key) == 0x13: # move left
                    self._move_cursor(self.curse_idx - 1)
                elif ord(key) == 0x0D: # enter  -> to give output
                    return self._output()
                elif ord(key) == 0x03: # control C -> exit
                    os._exit(0)
                else:
                    self._insert(key, self.curse_idx)
        
        def chatoutput(self, output: str):
            sys.stdout.write("\n\r" + output + "\n")
            sys.stdout.write("\r"+''.join(self.buffer))
        
        @register        
        def close(self):
            print("Closed chat terminal system")
            if self.f:
                self.f.close()
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.settings)
            
    ct = ChatTerminal()


    