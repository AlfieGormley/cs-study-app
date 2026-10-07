from concurrent.futures import (
    ThreadPoolExecutor)
import time

def fetch(i):
    time.sleep(0.5)  # stands in for I/O
    return i * i

start = time.perf_counter()
pool = ThreadPoolExecutor(max_workers=10)
with pool as ex:
    results = list(ex.map(fetch, range(20)))
took = time.perf_counter() - start
print(results[:5], f"{took:.1f}s")
