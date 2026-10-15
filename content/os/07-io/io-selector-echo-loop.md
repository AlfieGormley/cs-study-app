---
id: io-selector-echo-loop
title: Callbacks and a buffered echo loop
level: advanced
minutes: 3
summary: Callbacks run serially on their owning loop.
sourceLesson: io-event-loops
---

Earlier units gave you the raw tools: non-blocking sockets, and a way to wait on thousands of them at once with epoll or kqueue. An **event loop** is the piece of code that turns those tools into a server.

Node.js, nginx, Redis, Python's asyncio, Netty, HAProxy and Envoy all have one at their heart. Once you have seen the shape, you can read any of them.

## A common event-loop model

A common design runs the following dispatch logic on one thread until shutdown:

```
while running:
    timeout = time_until_next_timer()
    events  = wait(fds, timeout)
    for ev in events:
        run_callback(ev)
    run_expired_timers()
```

Three ideas carry the whole design:

1. **One thread, many connections.** Each connection is a small state object (a parser state, a buffer), rather than requiring a dedicated waiting thread and stack for each connection.
2. **Callbacks run to completion.** While a callback runs, nothing else on that loop runs. Other threads can still run and the OS can preempt this thread. Data exclusively owned by the loop often needs no inter-thread lock, but callbacks that re-enter the loop and shared state require care.
3. **Keep blocking work off the dispatch thread.** If anything waits, the whole loop waits, and every connection stalls.

## A small buffered echo loop in Python

Python's `selectors` module wraps epoll on Linux and kqueue on macOS. This local teaching server retains partial sends, handles receive EOF after sending all queued output, and bounds each connection's queued payload. It omits production concerns such as idle timeouts and a global connection/memory limit:

```python
import selectors, socket

sel = selectors.DefaultSelector()
R = selectors.EVENT_READ
W = selectors.EVENT_WRITE
HIGH = 65536

def close(conn):
    sel.unregister(conn)
    conn.close()

def accept(lsock, mask):
    try:
        conn, _ = lsock.accept()
    except BlockingIOError:
        return
    conn.setblocking(False)
    # Retain bytes until send accepts them.
    out, eof = bytearray(), False

    def echo(conn, mask):
        nonlocal eof
        try:
            if mask & R and not eof:
                room = HIGH - len(out)
                if room:
                    try:
                        data = conn.recv(
                            min(4096, room))
                    except BlockingIOError:
                        data = None
                    if data == b"":
                        eof = True
                    elif data:
                        # Queue bytes.
                        out.extend(data)
            if mask & W and out:
                try:
                    n = conn.send(out)
                except BlockingIOError:
                    n = None
                if n == 0:
                    close(conn)
                    return
                if n:
                    # Retain unsent bytes.
                    del out[:n]
        except OSError:
            close(conn)
            return
        # Watch writes with queued data.
        events = W if out else 0
        # Pause reads at the payload bound.
        if not eof and len(out) < HIGH:
            events |= R
        if events:
            sel.modify(conn, events, echo)
        else:
            close(conn)

    sel.register(conn, R, echo)

ls = socket.socket()
ls.setsockopt(socket.SOL_SOCKET,
              socket.SO_REUSEADDR, 1)
ls.bind(("127.0.0.1", 9000))
ls.listen(128)
ls.setblocking(False)
sel.register(ls, R, accept)
try:
    while True:
        for key, mask in sel.select():
            # Dispatch the saved callback.
            key.data(key.fileobj, mask)
finally:
    for key in list(sel.get_map().values()):
        key.fileobj.close()
    sel.close()
```

`key.data` is whatever you stored at registration: here, the callback. That's the **dispatch step**: an event on a descriptor maps to the handler for it.

> [!warning] Preserve partial writes
> Non-blocking sendall can raise after sending some bytes without exposing a usable partial count. The loop above uses send, retains the unsent suffix, enables write interest while output remains and pauses reading at HIGH. That is a per-connection payload bound, not a total process memory bound.

## Key takeaways
- Callbacks run serially on their owning loop.
- Retain partial-send suffixes and pause reading at a high-water mark.
- Per-connection payload limits do not bound total server memory.

## Further reading
- [The Node.js Event Loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Design overview — libuv documentation](https://docs.libuv.org/en/v1.x/design.html)
- [Thread pool work scheduling — libuv documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
- [Inside NGINX: How We Designed for Performance & Scale](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale)
- [aio and thread pools — nginx documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#aio)
- [Redis latency diagnosis — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [selectors — Python documentation](https://docs.python.org/3/library/selectors.html)
