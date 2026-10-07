import threading, time

def spin(n):
    while n:
        n -= 1

N = 20_000_000
t0 = time.perf_counter()
spin(N); spin(N)
dt = time.perf_counter() - t0
print(f"serial:  {dt:.2f}s")

t0 = time.perf_counter()
ts = [threading.Thread(target=spin,
                       args=(N,))
      for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
dt = time.perf_counter() - t0
print(f"threads: {dt:.2f}s")
