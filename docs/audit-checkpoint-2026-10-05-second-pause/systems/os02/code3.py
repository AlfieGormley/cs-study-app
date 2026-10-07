import threading

counter = 0

def bump(x):
    return x + 1

def work():
    global counter
    for _ in range(1_000_000):
        counter = bump(counter)

ts = [threading.Thread(target=work)
      for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print(counter)
