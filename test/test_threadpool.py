import sys
import time
import unittest
from pathlib import Path
from tools.threadpool import ThreadPool

sys.path.append(Path(__file__).parent.parent / "src" / "outlier")

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
        self.assertAlmostEqual(endtime - starttime, 5, delta=0.1)
        
    def test_thread_dead(self):
        starttime = time.time()
        t = ThreadPool(2, False)
        t.put_task(lambda x: 1/ x, args=(0,))
        t.put_task(ThreadPool.template_loop, args=(5,))
        time.sleep(2)
        t.put_task(ThreadPool.template_loop, args=(2,))
        t.queue.join()
        endtime = time.time()
        self.assertAlmostEqual(endtime - starttime, 5, delta=0.1)