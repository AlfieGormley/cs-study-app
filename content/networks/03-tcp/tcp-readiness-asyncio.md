---
id: tcp-readiness-asyncio
sourceLesson: tcp-sockets
title: Readiness pitfalls and asyncio backpressure
level: intermediate
minutes: 3
summary: Readiness pitfalls and asyncio backpressure, with worked examples and explicit assumptions.
---

## Scaling: threads versus an event loop

A thread per connection is simple, but stack reservations, task limits and scheduling costs constrain scale. Exact limits and stack sizes depend on the runtime and platform. Many mostly idle connections motivate multiplexing rather than one native thread each.

The alternative is **non-blocking sockets** and a **readiness API**: `select`/`poll`, `epoll` (Linux) or `kqueue` (BSD, macOS). Availability differs by platform: Python exposes `poll` on Unix, while Windows `select` handles sockets only. In the usual scanning-cost model, `select` scales with the highest descriptor number and `poll` with the number of supplied descriptors. One thread asks the kernel "which of these sockets can I read or write without blocking?" and handles only those. Python's `selectors` module chooses an available backend according to its platform policy. Readiness can become stale: operations on non-blocking sockets must still handle `BlockingIOError`.

**Deliberately faulty debugging example:** the next loop ignores partial writes and can exit on an unhandled would-block error. It is the subject of this unit’s partial-write quiz, not a correct echo-server template:

```python
import selectors, socket

EV = selectors.EVENT_READ
sel = selectors.DefaultSelector()
srv = socket.create_server(
    ("127.0.0.1", 9001))
srv.setblocking(False)
sel.register(srv, EV)

while True:
    for key, _ in sel.select():
        s = key.fileobj
        if s is srv:
            conn, _ = srv.accept()
            conn.setblocking(False)
            sel.register(conn, EV)
            continue
        try:
            data = s.recv(4096)
        except ConnectionError:
            data = b""
        if data:
            # BUG: the unsent suffix is
            # lost.
            s.send(data)  # may be partial
        else:
            # Remove this endpoint from the
            # loop.
            sel.unregister(s)
            s.close()
```

This loop can lose echo bytes or terminate. Correct readiness handling requires partial-write accounting, would-block/error handling for accept/read/write, bounded per-connection output queues, read backpressure, cleanup and half-close handling. Enable write interest only while output is pending and flush pending output before closing after input EOF. Frameworks provide parts of this machinery, but applications must still choose limits, framing and deadlines.

`asyncio` gives the same event-loop efficiency with sequential-looking code:

```python
import asyncio

async def handle(reader, writer):
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            # Queue the transformed reply.
            writer.write(data.upper())
            # Wait for transport buffer
            # capacity.
            await writer.drain()
    except ConnectionError:
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except ConnectionError:
            pass

async def main():
    srv = await asyncio.start_server(
        handle, "127.0.0.1", 9002)
    async with srv:
        await srv.serve_forever()

asyncio.run(main())
```

`writer.drain()` cooperates with the transport’s high/low watermarks: after writing is paused at the high watermark, it waits for the buffer to drain to the low watermark. It does not wait for a peer application acknowledgment. Slow readers, congestion or limited path capacity can cause backpressure; a zero receive window is not required. This echo sample has cleanup but still needs application deadlines and connection/resource limits for deployment.

## Key takeaways

- A readiness notification does not remove partial-write or would-block handling requirements.
- The selector loop is deliberately faulty and must not be copied as a correct server.
- asyncio drain cooperates with transport buffer watermarks; it does not acknowledge peer application processing.

## Further reading

- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html)
- [Python selectors module documentation](https://docs.python.org/3/library/selectors.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)

> [!note] Evidence limits
> Fixed thread-capacity and memory figures, universal restart behaviour and guaranteed load balancing are omitted: they require platform-specific measurements. The selector loop is retained only as an explicitly faulty exercise. Loopback example checks do not establish production scale, WAN behaviour or resistance to resource exhaustion.
