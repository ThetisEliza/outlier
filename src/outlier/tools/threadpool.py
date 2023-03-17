'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-10 02:58:46
FilePath: /outlier/src/outlier/tools/threadpool.py
'''
import queue
import threading
import time
import logging
from typing import Callable
from traceback import print_exc
from ..tools.decorators import singleton

class WorkThread(threading.Thread):
    def __init__(self, target):
        super(WorkThread, self).__init__(target=target)
        self.daemon = True
        self.start()
        
@singleton
class ThreadPool:
    def __init__(self, max_size=10, show_exception=True, status_monitor=False) -> None:
        self.queue = queue.Queue()
        self.waiting_task_num = 0
        self.processing_task_num = 0
        self.status_monitor = status_monitor
        self.show_exception = show_exception
        self.threads = [WorkThread(target=self._work) for _ in range(max_size)]
    
    def _work(self):
        while True:
            task, args = self.queue.get()
            try:
                self.waiting_task_num -= 1
                self.processing_task_num += 1
                task(*args)
            except Exception as e:
                logging.debug(f"warning some work failed {e}")
                if self.show_exception:
                    print_exc()
                time.sleep(1)
            finally:
                self.processing_task_num -= 1
                self.queue.task_done()
        
    def put_task(self, task: Callable, args=None):
        self.waiting_task_num += 1
        for thread in self.threads:
            if not thread.is_alive():
                logging.debug(f"Some thread dead remove it {thread}")
                self.threads.remove(thread)
                logging.debug(f"Add a new thread")
                self.threads.append(WorkThread(target=self._work))
    
        self.queue.put((task, args if args is not None else ()))
        
    def close(self):
        while not self.queue.empty():
            self.queue.get_nowait()
            
        
    def check_status(self):
        logging.debug(f"Working thread {len(self.threads)} waiting task {self.waiting_task_num}, processing task {self.processing_task_num}")
        
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
            logging.debug(f"[TASK]{r} counts at {i}/{r}")
            time.sleep(1)
            
# tp = ThreadPool(max_size=3)
# tp.put_task(ThreadPool.template_loop, args=(1,))
# tp.put_task(ThreadPool.template_loop, args=(2,))
# tp.put_task(ThreadPool.template_loop, args=(3,))
# tp.put_task(ThreadPool.template_loop, args=(4,))

# input()