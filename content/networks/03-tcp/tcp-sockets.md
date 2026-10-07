---
id: tcp-sockets
title: The sockets API and a Python server
level: intermediate
minutes: 15
summary: How Berkeley socket calls map onto TCP's states and queues, why TCP has no message boundaries and how to frame messages, partial sends and EOF, SO_REUSEADDR, and building a correct Python server with threads and with an event loop.
---

Python's **socket API** wraps operating-system networking interfaces. Similar concepts appear in other languages, but high-level runtimes, platforms and socket modes differ in their errors, buffering and lifetime rules.

This lesson separates byte-stream framing from connection setup and demonstrates bounded-message helpers. The servers remain teaching examples; the selector example is deliberately faulty for a debugging exercise.

## The calls and what they do in TCP

```
Server                 Client
socket()               socket()
bind(port)
listen(backlog)        connect(addr)
   SYN queue  <-- SYN ----
              --- SYN+ACK -->
   accept q   <-- ACK ----  (returns)
accept()  (returns a new socket)
recv()/send()  <------>  send()/recv()
close()        <-FIN/ACK->  close()
```

| Call | What happens in the kernel |
|---|---|
| `socket()` | Creates an endpoint; state CLOSED |
| `bind()` | Associates a local address/port, subject to reuse rules |
| `listen(n)` | State LISTEN; creates the queues |
| `connect()` | Ordinary blocking TCP: initiates setup, then succeeds or fails; non-blocking mode differs |
| `accept()` | Returns a new connected socket from pending connections |
| `close()` | Releases this socket reference; final closure can initiate FIN or an abort, depending on state/options |

Two points surprise people:

- **`accept()` does not perform the handshake.** The kernel completes handshakes on its own, whether or not the application is calling `accept()`. In ordinary TCP it dequeues a completed connection and returns a **new** socket; the peer may already have sent FIN before acceptance. Fast Open can allow acceptance before the normal handshake finishes. The listener remains available.
- **Ordinary blocking `connect()` success means the client-side handshake progressed successfully**, not that the server application accepted you or processed data. Queue overflow can leave the server still waiting to complete its side.

## The backlog and the two queues

A useful Linux model distinguishes two kinds of pending state (SYN cookies can avoid allocating an entry per SYN):

1. The **SYN queue**: half-open connections waiting for the final ACK.
2. The **accept queue**: completed connections waiting for `accept()`.

The `backlog` argument to `listen()` sets the size of the **accept queue**, capped by `net.core.somaxconn` (4,096 by default since Linux 5.4; 128 before).

If the application is too slow to accept and that queue fills, one Linux path with `tcp_abort_on_overflow = 0` can **ignore** the client's final ACK; other overload paths can drop SYNs. The client thinks it's connected and may send its request; the server retransmits SYN+ACK and the connection completes later, or not. The symptom is clients seeing occasional multi-second delays on connect or first request. `nstat` shows `TcpExtListenOverflows` climbing.

> [!tip] Investigate queue overload
> Arrival bursts, slow acceptance, resource limits and backlog configuration can all contribute. Inspect application scheduling and queue/counter measurements. A growing overflow counter does not by itself identify a single cause or prove one packet-level sequence.

## A stream has no message boundaries

TCP delivers a **byte stream**. It does not preserve the boundaries of your `send()` calls:

```
client: send(b"hello")
client: send(b"world")

server recv(1024) may return:
  b"helloworld"         (coalesced)
  b"hel", then b"loworld" (split)
  b"hello", then b"world"
```

All three are correct TCP behaviour. Nagle, segmentation, retransmission and the timing of `recv()` calls all affect where the cuts fall. A one-read-per-message assumption can fail even on localhost; a passing local test does not establish framing correctness.

Protocols that distinguish messages need **framing**. A single stream-to-EOF transfer can use EOF as its boundary:

- **Length prefix**: send a fixed-size length, then that many bytes. For example, gRPC has its own message-length prefix inside HTTP/2 DATA frames; the HTTP/2 frame header is a separate framing layer.
- **Delimiter**: end each message with a marker, such as `\r\n` in SMTP and in HTTP/1.1 headers. The receiver buffers until it finds one.
- **Protocol-defined body rules**: HTTP/1.1 uses status/method rules, `Content-Length`, chunked encoding, or connection closure as applicable; not every response has a body.

## Partial reads, partial writes and EOF

Three rules for using the calls correctly:

1. For a positive `n`, ordinary blocking **`recv(n)` returns at most n bytes**. Short reads are allowed. Flags, low-water settings, timeouts and errors can change when it returns; loop for a specified length.
2. **`send()` may send only part of the buffer**, returning the count it accepted, for example because of limited buffer capacity. Python's `sendall()` handles partial writes on blocking sockets, but may raise; success means local acceptance, not peer processing.
3. With a positive read size and no local receive shutdown, **`recv()` returning `b""` indicates end of stream** after received bytes have been consumed: the peer closed its sending direction. It is not an error and not "no data yet". If you don't treat it as the end, you'll spin forever on a closed connection.

Error conditions show up as exceptions:

| Python exception | Usual meaning |
|---|---|
| `ConnectionRefusedError` | RST in reply to SYN |
| `ConnectionResetError` | Peer sent RST mid-connection |
| `BrokenPipeError` | Writing to a stream no longer usable for sending; peer half-close alone need not cause it |
| `TimeoutError` / `socket.timeout` | An operation exceeded its applicable timeout; `sendall()` has an overall timeout |

Choose operation timeouts and application deadlines. A silent peer can otherwise leave a blocking read waiting indefinitely. Linux’s documented default keepalive idle interval is 7,200 seconds when keepalive is enabled, but applications and configuration can change it. Keepalive is not a substitute for a request deadline.

## A length-prefixed server with threads

First, framing helpers. `recv_exact` loops until it has exactly `n` bytes, and treats EOF in the middle as an error:

```python
import socket, struct, threading

MAX_MSG = 1024 * 1024  # teaching limit

def recv_exact(sock, n):
    if type(n) is not int or n < 0:
        raise ValueError("invalid length")
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError
        buf += chunk
    return bytes(buf)

def recv_msg(sock):
    hdr = recv_exact(sock, 4)
    (n,) = struct.unpack("!I", hdr)
    if n > MAX_MSG:
        raise ValueError("too large")
    return recv_exact(sock, n)

def send_msg(sock, data):
    if len(data) > MAX_MSG:
        raise ValueError("too large")
    hdr = struct.pack("!I", len(data))
    sock.sendall(hdr + data)
```

`"!I"` is a 4-byte unsigned integer in network byte order (big-endian). Combining header and body avoids an application-created pause between two small writes, but one `sendall()` is not one packet and cannot guarantee freedom from Nagle, queueing or other delays.

Then the server, one thread per connection:

```python
def handle(conn, addr):
    with conn:
        conn.settimeout(5)
        try:
            while True:
                msg = recv_msg(conn)
                send_msg(conn, msg.upper())
        except (EOFError, OSError,
                ValueError):
            pass  # toy policy: close

srv = socket.create_server(
    ("127.0.0.1", 9000), backlog=128)
while True:
    conn, addr = srv.accept()
    threading.Thread(target=handle,
                     args=(conn, addr),
                     daemon=True).start()
```

And a client:

```python
with socket.create_connection(
        ("127.0.0.1", 9000),
        timeout=5) as s:
    s.settimeout(5)
    send_msg(s, b"hello")
    print(recv_msg(s))   # b'HELLO'
```

Details that make this correct:

- `with conn:` closes this socket when the handler exits. It cannot force a handler that never exits to finish; duplicated references and wrappers also affect lifetime.
- The helpers cap each body at 1 MiB. The handler has a per-operation timeout, not a total-message deadline: a trickling peer can keep a message in progress. Production code needs total deadlines, connection/thread limits and a deliberate error policy.
- `socket.create_server` sets **`SO_REUSEADDR`** on POSIX systems. Without suitable reuse settings, retained connection state can prevent immediate rebinding. This is not an inevitable outcome of every restart; address, platform and old/new socket options matter.

> [!note] SO_REUSEADDR vs SO_REUSEPORT
> `SO_REUSEADDR` relaxes platform-specific bind rules; it does not grant arbitrary sharing with an active listener. Linux generally requires the reuse option on both the previous and new sockets for the relevant reuse case. `SO_REUSEPORT` (Linux 3.9+) supports multiple eligible listeners at the same address/port, each with its own queue. Sockets must set it before binding; Linux requires matching effective user IDs. Default selection and optional BPF policies do not guarantee perfectly balanced work.

## Scaling: threads versus an event loop

A thread per connection is simple, but stack reservations, task limits and scheduling costs constrain scale. Exact limits and stack sizes depend on the runtime and platform. Many mostly idle connections motivate multiplexing rather than one native thread each.

The alternative is **non-blocking sockets** and a **readiness API**: `select`/`poll`, `epoll` (Linux) or `kqueue` (BSD, macOS). Availability differs by platform: Python exposes `poll` on Unix, while Windows `select` handles sockets only. In the usual scanning-cost model, `select` scales with the highest descriptor number and `poll` with the number of supplied descriptors. One thread asks the kernel "which of these sockets can I read or write without blocking?" and handles only those. Python's `selectors` module chooses an available backend according to its platform policy. Readiness can become stale: non-blocking operations must still handle `BlockingIOError`.

**Deliberately faulty debugging example:** the next loop ignores partial writes and can exit on an unhandled would-block error. It is the subject of quiz question 10, not a correct echo-server template:

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
            s.send(data)  # may be partial
        else:
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
            writer.write(data.upper())
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
- Ordinary TCP setup can progress without the application calling `accept()`; acceptance returns a separate socket.
- Linux backlog and queue overload require version/configuration-aware diagnosis.
- TCP delivers ordered bytes, not application messages. Handle short reads, partial writes and half-close explicitly.
- Bound messages and resource use, close owned sockets, and distinguish per-operation timeouts from total deadlines.
- Readiness loops must retain unsent output and apply backpressure; `asyncio.drain()` is a buffer-flow-control mechanism.

> [!note] Evidence limits
> Fixed thread-capacity and memory figures, universal restart behaviour and guaranteed load balancing are omitted: they require platform-specific measurements. The selector loop is retained only as an explicitly faulty exercise. Loopback example checks do not establish production scale, WAN behaviour or resistance to resource exhaustion.

## Further reading
- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html)
- [Python selectors module documentation](https://docs.python.org/3/library/selectors.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
