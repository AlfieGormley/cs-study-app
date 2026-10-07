import threading
lock = threading.Lock()

def f():
    with lock:
        g()

def g():
    with lock:
        print("hi")

f()
