import unittest
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.parent / "src" / "outlier")

class testThreadPool(unittest.TestCase):
    def test_time(self):

        import time
        from tools.threadpool import ThreadPool

        starttime = time.time()
        t = ThreadPool(10)
        t.put_task(ThreadPool.template_loop, args=(1,))
        t.put_task(ThreadPool.template_loop, args=(5,))
        t.put_task(ThreadPool.template_loop, args=(2,))
        t.put_task(ThreadPool.template_loop, args=(4,))
        t.put_task(ThreadPool.template_loop, args=(3,))
        t.queue.join()
        endtime = time.time()
        self.assertAlmostEqual(endtime - starttime, 5, delta=0.1)
        
        
        

