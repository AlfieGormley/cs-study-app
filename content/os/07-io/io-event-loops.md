---
id: io-event-loops
title: Event loops (libuv, nginx, Redis)
level: advanced
minutes: 14
summary: How an event loop turns epoll or kqueue into a server, the reactor and proactor patterns, timers, libuv's phases and thread pool, nginx's worker model, Redis's single-threaded design, and the cardinal rule of never blocking the loop.
---

The previous lessons gave you the raw tools: non-blocking sockets, and a way to wait on thousands of them at once with epoll or kqueue. An **event loop** is the piece of code that turns those tools into a server.

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
2. **Callbacks run to completion.** While a callback runs, nothing else on that loop runs. Other threads can still run and the OS can preempt this thread. Data exclusively owned by the loop often needs no inter-thread lock, but reentrant callbacks and shared state require care.
3. **Keep blocking work off the dispatch thread.** If anything waits, the whole loop waits, and every connection stalls.

## A small buffered echo loop in Python

Python's `selectors` module wraps epoll on Linux and kqueue on macOS. This local teaching server retains partial sends, handles receive EOF after flushing queued output, and bounds each connection's queued payload. It omits production concerns such as idle timeouts and a global connection/memory limit:

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
                    del out[:n]
        except OSError:
            close(conn)
            return
        events = W if out else 0
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
            key.data(key.fileobj, mask)
finally:
    for key in list(sel.get_map().values()):
        key.fileobj.close()
    sel.close()
```

`key.data` is whatever you stored at registration: here, the callback. That's the **dispatch** step: an event on a descriptor maps to the handler for it.

> [!warning] Preserve partial writes
> Non-blocking sendall can raise after sending some bytes without exposing a usable partial count. The loop above uses send, retains the unsent suffix, enables write interest while output remains and pauses reading at HIGH. That is a per-connection payload bound, not a total process memory bound.

## Reactor and proactor

Two named patterns describe the two I/O models from lesson 2:

| Pattern | Loop tells you | Built on |
|---|---|---|
| Reactor | "fd is ready, you do it" | epoll, kqueue |
| Proactor | "your op is done" | IOCP, io_uring |

The `selectors` example is a reactor. Windows IOCP and io_uring are proactors. Libraries often present a proactor-style API ("call me back with the data") on top of a reactor: libuv's `uv_read_start` gives you bytes, though underneath it waited on epoll and called `read()` itself.

## Timers

Servers need timeouts: idle connections, retries, `setTimeout`. A loop keeps pending timers in a **min-heap** keyed by expiry time (libuv uses a binary min-heap; nginx uses a red-black tree).

- Insert a timer: O(log n).
- Next expiry: O(1), the root.
- The wait timeout is `next_expiry - now`, so the loop requests a wait no longer than the time to the next expiry; interruption, timer granularity and scheduling can alter actual wakeup time.

A timer establishes a scheduling threshold, not an exact deadline. Long callbacks can delay it substantially. Runtime clock granularity and rounding mean a nominal millisecond value is not a precision timing contract.

## libuv and Node.js

libuv is the C library under Node.js. The main recurring phases in modern Node/libuv can be sketched as follows; startup behavior and version details matter. Since libuv 1.45 (used by Node 20), timers run after polling in the recurring loop rather than both before and after it:

```
 +--> pending        (deferred I/O cbs)
 |    idle, prepare  (internal)
 |    poll           (wait; I/O cbs)
 |    check          (setImmediate)
 |    close          (on 'close' cbs)
 +--- timers         (setTimeout)
```

Node also services nextTick and promise microtask queues. In typical CommonJS callback contexts, nextTick processing precedes promise microtasks; ES-module evaluation is itself microtask-driven and can produce a different apparent order. Recursive nextTick or endlessly replenished microtasks can starve normal I/O progress.

One consequence often asked about: inside an I/O callback, `setImmediate` always fires before `setTimeout(f, 0)`, because after the poll phase comes check, then the loop wraps round to timers. From the main module the order isn't guaranteed; it depends on whether 1 ms has passed when the loop starts.

### The thread pool

libuv uses a shared **thread pool** for several asynchronous APIs, with results delivered back to the originating loop. Alternative supported filesystem backends can exist:

- File system operations (`fs.readFile` and friends), since epoll can't wait on regular files
- DNS via `getaddrinfo` (`dns.lookup`)
- Some CPU-heavy crypto (`pbkdf2`, `scrypt`) and `zlib`

The pool has **4 threads by default**, set with `UV_THREADPOOL_SIZE` (up to 1,024). That small default is a classic production surprise: four slow NFS reads or four `pbkdf2` calls and every `dns.lookup` queues behind them, so outbound HTTP requests appear to hang.

Ordinary asynchronous network socket readiness/completion uses the platform backend rather than a blocked pool worker per socket. Unix often uses epoll/kqueue; Windows uses IOCP. DNS lookup can still use the pool.

## nginx

nginx uses one loop per process rather than one process overall:

```
        master (root: config,
          |      binds ports)
   +------+------+------+
 worker worker worker worker
 (loop)  (loop)  (loop)  (loop)
```

- worker_processes auto attempts to detect available CPUs; inspect the actual count under affinity/cgroup constraints. Each worker has its own event loop, with platform-specific backends and optional worker threads.
- `worker_connections` caps connections per worker (the default is 512; production configs often raise it to thousands). Workers × worker_connections is an aggregate connection-slot ceiling, not a guarantee of that many clients: upstream connections and descriptor/resource limits also consume capacity.
- Workers share the listening sockets. With `listen ... reuseport`, each worker gets its own `SO_REUSEPORT` socket and the kernel spreads new connections between them, avoiding the thundering herd and lock contention on a shared accept queue.
- Per-worker connections reduce shared-state contention, but shared-memory zones, caches and other coordination can still use locks.

Because each worker is a loop, a blocking disk read stalls every connection on that worker. nginx added **thread pools** (`aio threads`, version 1.7.11) to offload reads that miss the page cache. Performance depends on storage, files, concurrency and configuration; no benchmark reproduction is included here.

The master process never handles traffic. It re-reads config on `SIGHUP`, starts new workers, and lets old ones finish their connections: this supports graceful reloads, but errors, timeouts and worker shutdown limits mean zero dropped requests is not an unconditional guarantee.

## Redis

Redis illustrates serial command execution combined with event-driven I/O and background work.

- Its own small event library, **ae**, picks epoll, kqueue, evport or select at build time.
- Commands execute one at a time on the main thread. Serial command execution avoids interleaving ordinary command handlers on one instance; it does not make all server code lock-free or turn multi-command client workflows into transactions.
- Command cost depends on command complexity, data size, persistence, networking and hardware. Pipelining can amortize round trips without removing command work.

The flip side is the cardinal rule in action:

- `KEYS *` on 10 million keys, a big `SMEMBERS`, or a slow Lua script blocks **every** client for its duration. Use `SCAN` and keep scripts short.
- Ordinary synchronous deletion of a large aggregate can be expensive. UNLINK (introduced in Redis 4.0) detaches keys and defers expensive freeing; small objects and lazy-free configuration affect which work runs in the background.
- Snapshots use `fork()`: the child writes the RDB file while copy-on-write keeps the parent serving. A large heap can make the fork itself take noticeable time.

Redis 6.0 introduced configurable I/O threads. In that version, threaded reads additionally require io-threads-do-reads yes; they are not automatically enabled merely by raising io-threads. Ordinary command execution remains serial on the main thread. Benefits depend on the actual I/O bottleneck; later versions can change implementation details.

## Using all the cores

A single loop uses one core. The common ways out:

| Approach | Example |
|---|---|
| One loop per process | nginx, Node `cluster` |
| One loop per thread | Netty, Seastar, Envoy |
| Partitioned service instances | Redis Cluster shards |
| Pool for blocking work | libuv, nginx aio |

Seastar (behind ScyllaDB) takes "loop per core" to the limit: a **shard-per-core** design where each core owns its data and talks to others only by message passing.

## Pitfalls

- **Blocking the loop.** A synchronous file read, a CPU-heavy JSON parse, a regex with catastrophic backtracking or a `time.sleep()` freezes every connection. Measure **event-loop lag** (how late a periodic timer fires) as a health metric.
- **Unfairness.** One connection sending a flood can monopolise the loop. Cap the work per wake-up, e.g. read at most N bytes before moving on.
- **No backpressure.** If you read faster than you can write, per-connection buffers grow without bound. Stop reading from the source (unregister `EVENT_READ`) while the outgoing buffer is above a high-water mark.
- **Callback hell and lost errors.** `async`/`await` (Python asyncio, JavaScript, Rust) is syntax over the same loop: an await can suspend, but an already-completed operation may continue immediately (for example in Python); language/runtime behavior differs.

> [!tip] Know which thread you're on
> Most event-loop libraries aren't thread-safe. To hand work back to a loop from another thread, use its wake-up mechanism: `uv_async_send` in libuv, `loop.call_soon_threadsafe` in asyncio. The backend wakeup mechanism is platform-specific, such as an eventfd, pipe or completion notification.

## Key takeaways
- An event loop is one thread that waits for I/O or the next timer, then runs callbacks to completion; callbacks should avoid blocking the dispatch thread.
- Reactors dispatch readiness (epoll, kqueue); proactors dispatch completions (IOCP, io_uring).
- Timers live in a heap or tree; the next expiry sets the wait timeout, and timer thresholds do not guarantee exact wakeup time.
- libuv runs fixed phases and sends files, DNS and some crypto to a 4-thread pool by default; nginx runs one loop per worker process; ordinary Redis commands execute serially, while background/I/O work has separate synchronization.
- Scale across cores with one loop per core, and measure event-loop lag to catch anything that blocks.

> [!note] Workload evidence gap
> Fixed Redis latency/throughput, universal connection capacities and an unreproduced nginx speedup figure are omitted. Measure the deployed workload and runtime. The echo example bounds queued payload per connection; it does not implement production admission control, timeouts or global memory limits.

## Further reading
- [The Node.js Event Loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Design overview — libuv documentation](https://docs.libuv.org/en/v1.x/design.html)
- [Thread pool work scheduling — libuv documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
- [Inside NGINX: How We Designed for Performance & Scale](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale)
- [aio and thread pools — nginx documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#aio)
- [Redis latency diagnosis — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [selectors — Python documentation](https://docs.python.org/3/library/selectors.html)
