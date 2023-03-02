import queue
import threading
import time
from typing import Callable
from traceback import format_exc

class WorkThread(threading.Thread):
    def __init__(self, target):
        super(WorkThread, self).__init__(target=target)
        self.setDaemon(True)
        self.start()

            
class ThreadPool:
    def __init__(self, max_size=10, status_monitor=False) -> None:
        self.queue = queue.Queue()
        self.waiting_task_num = 0
        self.processing_task_num = 0
        self.status_monitor = status_monitor
        self.threads = [WorkThread(target=self._work) for _ in range(max_size)]
    
    def _work(self):
        while True:
            task, args = self.queue.get()
            try:
                self.waiting_task_num -= 1
                self.processing_task_num += 1
                task(*args)
            except Exception as e:
                time.sleep(1)
                raise Exception("Threadpool work error")
            finally:
                self.processing_task_num -= 1
                self.queue.task_done()
        
    def put_task(self, task: Callable, args=None):
        self.waiting_task_num += 1
        if args is None:
            args = ()
        self.queue.put((task, args))
        
    def close(self):
        while not self.queue.empty() :
            self.queue.get_nowait()
        
    def check_status(self):
        print(f"Working thread {len(self.threads)} waiting task {self.waiting_task_num}, processing task {self.processing_task_num}")
        
    # def open_status_monitor(self):
    #     self.status_monitor = True
    #     self.put_task(self.check_status_loop)
        
    # def close_status_monitor(self):
    #     self.status_monitor = False
        
    # def check_status_loop(self):
    #     import time
    #     while self.status_monitor:
    #         self.check_status()
    #         time.sleep(0.5)
        
    @staticmethod
    def template_loop(r):
        import time
        for i in range(r):
            print(f"[TASK]{r} counts at {i}/{r}")
            time.sleep(1)
            
# tp = ThreadPool(max_size=3)
# tp.put_task(ThreadPool.template_loop, args=(1,))
# tp.put_task(ThreadPool.template_loop, args=(2,))
# tp.put_task(ThreadPool.template_loop, args=(3,))
# tp.put_task(ThreadPool.template_loop, args=(4,))

# input()