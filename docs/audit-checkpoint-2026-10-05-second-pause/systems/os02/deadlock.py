from concurrent.futures import (
    ThreadPoolExecutor)
from threading import Barrier

pool = ThreadPoolExecutor(max_workers=2)
barrier = Barrier(2)

def child():
    return 1

def parent():
    barrier.wait()
    f = pool.submit(child)
    return f.result()

fs = [pool.submit(parent)
      for _ in range(2)]
print([f.result() for f in fs])
