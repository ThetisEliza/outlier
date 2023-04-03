'''
Date: 2023-03-08 23:10:22
LastEditors: ThetisEliza wxf199601@gmail.com
LastEditTime: 2023-03-13 19:34:21
FilePath: /outlier/test/test_threadpool.py
'''
import sys
import time
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src" ))

from outlier.tools.threadpool import ThreadPool

class testThreadPool(unittest.TestCase):
    def test_norm(self):
        starttime = time.time()
        t = ThreadPool(10, False)
        t.put_task(ThreadPool.template_loop, args=(1,))
        t.put_task(ThreadPool.template_loop, args=(5,))
        t.put_task(ThreadPool.template_loop, args=(2,))
        t.put_task(ThreadPool.template_loop, args=(4,))
        t.put_task(ThreadPool.template_loop, args=(3,))
        t.queue.join()
        endtime = time.time()
        self.assertAlmostEqual(endtime - starttime, 5, delta=0.9)
        
    def test_thread_dead(self):
        starttime = time.time()
        t = ThreadPool(2, False)
        t.put_task(lambda x: 1/ x, args=(0,))
        t.put_task(ThreadPool.template_loop, args=(5,))
        time.sleep(2)
        t.put_task(ThreadPool.template_loop, args=(2,))
        t.queue.join()
        endtime = time.time()
        self.assertAlmostEqual(endtime - starttime, 5, delta=0.9)
