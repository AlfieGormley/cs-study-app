from pathlib import Path
p=Path('content/networks/03-tcp/tcp-sockets.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:70]
 s=s.replace(a,b)
a=s.index('Everything in this module');b=s.index('\n## The calls',a)
s=s[:a]+'''Python's **socket API** wraps operating-system networking interfaces. Similar concepts appear in other languages, but high-level runtimes, platforms and socket modes differ in their errors, buffering and lifetime rules.

This lesson separates byte-stream framing from connection setup and demonstrates bounded-message helpers. The servers remain teaching examples; the selector example is deliberately faulty for a debugging exercise.
''' +s[b:]
r('| `bind()` | Claims a local address and port |','| `bind()` | Associates a local address/port, subject to reuse rules |')
r('| `connect()` | Sends SYN; returns when ESTABLISHED |','| `connect()` | Ordinary blocking TCP: initiates setup, then succeeds or fails; non-blocking mode differs |')
r('| `accept()` | Takes a finished connection off the queue |','| `accept()` | Returns a new connected socket from pending connections |')
r('| `close()` | Sends FIN (or RST if data is unread) |','| `close()` | Releases this socket reference; final closure can initiate FIN or an abort, depending on state/options |')
r('Accept only dequeues connections that are already ESTABLISHED, and returns a **new** socket for each one; the listening socket stays in LISTEN.','In ordinary TCP it dequeues a completed connection and returns a **new** socket; the peer may already have sent FIN before acceptance. Fast Open can allow acceptance before the normal handshake finishes. The listener remains available.')
r('**`connect()` succeeding means the handshake finished**, not that the server application has seen you. If the server is overloaded and never calls `accept()`, your connection still exists.','**Ordinary blocking `connect()` success means the client-side handshake progressed successfully**, not that the server application accepted you or processed data. Queue overflow can leave the server still waiting to complete its side.')
r('A listening socket on Linux has two queues (lesson 2):','A useful Linux model distinguishes two kinds of pending state (SYN cookies can avoid allocating an entry per SYN):')
r('Linux by default **ignores** the client\'s final ACK.','one Linux path with `tcp_abort_on_overflow = 0` can **ignore** the client\'s final ACK; other overload paths can drop SYNs.')
r('> [!tip] A full accept queue is an application problem\n> The kernel has done the handshakes; your process is not calling `accept()` fast enough. Look at blocked event loops and thread pools before tuning sysctls.','> [!tip] Investigate queue overload\n> Arrival bursts, slow acceptance, resource limits and backlog configuration can all contribute. Inspect application scheduling and queue/counter measurements. A growing overflow counter does not by itself identify a single cause or prove one packet-level sequence.')
r('Code that assumes one `recv()` returns one message works on localhost in testing and fails in production.','A one-read-per-message assumption can fail even on localhost; a passing local test does not establish framing correctness.')
r('So every protocol on TCP needs **framing**:','Protocols that distinguish messages need **framing**. A single stream-to-EOF transfer can use EOF as its boundary:')
r('Used by gRPC (HTTP/2 frames), Kafka, PostgreSQL and many binary protocols.','For example, gRPC has its own message-length prefix inside HTTP/2 DATA frames; the HTTP/2 frame header is a separate framing layer.')
r('**Self-describing**: HTTP/1.1 bodies use `Content-Length` or chunked encoding.','**Protocol-defined body rules**: HTTP/1.1 uses status/method rules, `Content-Length`, chunked encoding, or connection closure as applicable; not every response has a body.')
r('**`recv(n)` returns up to n bytes**, as soon as **any** are available. Loop until you have what you need.','For a positive `n`, ordinary blocking **`recv(n)` returns at most n bytes**. Short reads are allowed. Flags, low-water settings, timeouts and errors can change when it returns; loop for a specified length.')
r('when the socket\'s send buffer is nearly full. Python\'s `sendall()` loops for you on blocking sockets.','for example because of limited buffer capacity. Python\'s `sendall()` handles partial writes on blocking sockets, but may raise; success means local acceptance, not peer processing.')
r('**`recv()` returning `b""` means end of stream**: the peer sent FIN.','With a positive read size and no local receive shutdown, **`recv()` returning `b""` indicates end of stream** after received bytes have been consumed: the peer closed its sending direction.')
r('| `BrokenPipeError` | Writing after the peer closed |','| `BrokenPipeError` | Writing to a stream no longer usable for sending; peer half-close alone need not cause it |')
r('| `TimeoutError` / `socket.timeout` | No progress within `settimeout()` |','| `TimeoutError` / `socket.timeout` | An operation exceeded its applicable timeout; `sendall()` has an overall timeout |')
r('Always set timeouts on client sockets. A blocking `recv()` on a connection whose peer has vanished can wait for a very long time; TCP keepalive is off by default and, when enabled on Linux, first probes only after two hours.','Choose operation timeouts and application deadlines. A silent peer can otherwise leave a blocking read waiting indefinitely. Linux’s documented default keepalive idle interval is 7,200 seconds when keepalive is enabled, but applications and configuration can change it. Keepalive is not a substitute for a request deadline.')
r('import socket, struct, threading\n\ndef recv_exact(sock, n):\n    buf', 'import socket, struct, threading\n\nMAX_MSG = 1024 * 1024  # teaching limit\n\ndef recv_exact(sock, n):\n    if type(n) is not int or n < 0:\n        raise ValueError("invalid length")\n    buf')
r('    (n,) = struct.unpack("!I", hdr)\n    return recv_exact(sock, n)','    (n,) = struct.unpack("!I", hdr)\n    if n > MAX_MSG:\n        raise ValueError("message too large")\n    return recv_exact(sock, n)')
r('def send_msg(sock, data):\n    hdr', 'def send_msg(sock, data):\n    if len(data) > MAX_MSG:\n        raise ValueError("message too large")\n    hdr')
r('Header and body go out in **one** `sendall`, so Nagle and delayed ACK can\'t stall us (lesson 4).','Combining header and body avoids an application-created pause between two small writes, but one `sendall()` is not one packet and cannot guarantee freedom from Nagle, queueing or other delays.')
r('    with conn:\n        try:', '    with conn:\n        conn.settimeout(5)\n        try:')
r('        except (EOFError, ConnectionError):\n            pass  # client went away','        except (EOFError, OSError, ValueError):\n            pass  # toy policy: close connection')
r('srv = socket.create_server(("", 9000),\n                           backlog=128)','srv = socket.create_server(\n    ("127.0.0.1", 9000), backlog=128)')
r('        ("127.0.0.1", 9000)) as s:', '        ("127.0.0.1", 9000), timeout=5) as s:')
r('- `with conn:` closes the socket on every path, so no connections leak into CLOSE_WAIT (lesson 2).','- `with conn:` closes this socket when the handler exits. It cannot force a handler that never exits to finish; duplicated references and wrappers also affect lifetime.')
r('- A real server should also bound message sizes (a malicious 4 GB length prefix would make `recv_exact` try to buffer it) and set a read timeout per connection.','- The helpers cap each body at 1 MiB. The handler has a per-operation timeout, not a total-message deadline: a trickling peer can keep a message in progress. Production code needs total deadlines, connection/thread limits and a deliberate error policy.')
r('Without it, restarting a server that had live connections fails with `OSError: Address already in use` while those connections sit in TIME_WAIT on its port.','Without suitable reuse settings, retained connection state can prevent immediate rebinding. This is not an inevitable outcome of every restart; address, platform and old/new socket options matter.')
r('`SO_REUSEADDR` lets a listener bind a port even though old connections on that port are in TIME_WAIT. `SO_REUSEPORT` (Linux 3.9+) lets **several** sockets listen on the same port at once, with the kernel spreading new connections between them. Nginx and Envoy use it to give each worker process its own accept queue.','`SO_REUSEADDR` relaxes platform-specific bind rules; it does not grant arbitrary sharing with an active listener. Linux generally requires the reuse option on both the previous and new sockets for the relevant reuse case. `SO_REUSEPORT` (Linux 3.9+) supports multiple eligible listeners at the same address/port, each with its own queue. Sockets must set it before binding; Linux requires matching effective user IDs. Default selection and optional BPF policies do not guarantee perfectly balanced work.')
r('A thread per connection is simple and fine for hundreds or a few thousand connections. Each thread has a stack (often 8 MB of reserved virtual memory on Linux, much less actually used) and context switches add up. At tens of thousands of mostly idle connections, the famous **C10K problem**, it becomes wasteful.','A thread per connection is simple, but stack reservations, task limits and scheduling costs constrain scale. Exact limits and stack sizes depend on the runtime and platform. Many mostly idle connections motivate multiplexing rather than one native thread each.')
r('Python\'s `selectors` module picks the best one available:','Python\'s `selectors` module chooses an available backend according to its platform policy. Readiness can become stale: non-blocking operations must still handle `BlockingIOError`.\n\n**Deliberately faulty debugging example:** the next loop ignores partial writes and can exit on an unhandled would-block error. It is the subject of quiz question 10, not a correct echo-server template:')
r('srv = socket.create_server(("", 9001))','srv = socket.create_server(\n    ("127.0.0.1", 9001))')
r('This echo server handles thousands of connections in one thread. It has one known simplification: a non-blocking `send()` may accept only part of the data (or raise `BlockingIOError` if the send buffer is full). A production loop keeps a per-connection output buffer and registers for `EVENT_WRITE` until it drains. That bookkeeping, plus framing and timeouts, is what frameworks such as `asyncio`, Netty, libuv (Node.js) and Go\'s runtime do for you.','This loop can lose echo bytes or terminate. Correct readiness handling requires partial-write accounting, would-block/error handling for accept/read/write, bounded per-connection output queues, read backpressure, cleanup and half-close handling. Enable write interest only while output is pending and flush pending output before closing after input EOF. Frameworks provide parts of this machinery, but applications must still choose limits, framing and deadlines.')
a=s.index('async def handle(reader, writer):');b=s.index('\nasync def main():',a)
s=s[:a]+'''async def handle(reader, writer):
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
''' +s[b:]
r('        handle, "", 9002)','        handle, "127.0.0.1", 9002)')
r('`await writer.drain()` is flow control surfacing in application code: it pauses this coroutine while the socket\'s send buffer is full, which happens when the client\'s receive window (lesson 4) is closed.','`writer.drain()` cooperates with the transport’s high/low watermarks: after writing is paused at the high watermark, it waits for the buffer to drain to the low watermark. It does not wait for a peer application acknowledgment. Slow readers, congestion or limited path capacity can cause backpressure; a zero receive window is not required. This echo sample has cleanup but still needs application deadlines and connection/resource limits for deployment.')
a=s.index('## Key takeaways');b=s.index('## Further reading',a)
s=s[:a]+'''## Key takeaways
- Ordinary TCP setup can progress without the application calling `accept()`; acceptance returns a separate socket.
- Linux backlog and queue overload require version/configuration-aware diagnosis.
- TCP delivers ordered bytes, not application messages. Handle short reads, partial writes and half-close explicitly.
- Bound messages and resource use, close owned sockets, and distinguish per-operation timeouts from total deadlines.
- Readiness loops must retain unsent output and apply backpressure; `asyncio.drain()` is a buffer-flow-control mechanism.

> [!note] Evidence limits
> Fixed thread-capacity and memory figures, universal restart behaviour and guaranteed load balancing are omitted: they require platform-specific measurements. The selector loop is retained only as an explicitly faulty exercise. Loopback example checks do not establish production scale, WAN behaviour or resistance to resource exhaustion.

''' +s[b:]
p.write_text(s)
p=Path('content/networks/03-tcp/tcp-performance.md');s=p.read_text().replace('    """Ideal Reno-model estimate in bits/s."""','    """Reno-model estimate in bits/s."""').replace('    if mss <= 0 or rtt <= 0 or not 0 < p < 1:','    valid = mss > 0 and rtt > 0 and 0 < p < 1\n    if not valid:').replace('        raise ValueError("invalid parameters")','        raise ValueError("invalid input")');p.write_text(s)
