---
id: io-redis-loop-scaling
title: Redis commands, loop scaling and backpressure
level: advanced
minutes: 3
summary: Ordinary Redis command execution is serial despite background and I/O work.
sourceLesson: io-event-loops
---

## Redis

Redis illustrates serial command execution combined with event-driven I/O and background work.

- Its own small event library, **ae**, picks epoll, kqueue, evport or select at build time.
- Commands execute one at a time on the main thread. Serial command execution avoids interleaving ordinary command handlers on one instance; it does not make all server code lock-free or turn multi-command client workflows into transactions.
- Command cost depends on command complexity, data size, persistence, networking and hardware. Redis pipelining can amortize round trips without removing command work.

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

Seastar (behind ScyllaDB) uses a **shard-per-core** design: each application shard owns its data and exchanges messages with other shards. This programming model reduces shared mutable application state; it is not a claim that the entire runtime and operating system contain no shared memory or locks.

## Pitfalls

- **Blocking the loop.** A synchronous file read, a CPU-heavy JSON parse, a regex with catastrophic backtracking or a `time.sleep()` freezes every connection. Measure **event-loop lag** (how late a periodic timer fires) as a health metric.
- **Unfairness.** One connection sending a flood can monopolise the loop. Cap the work per wake-up, e.g. read at most a fixed budget (say 64 KiB) from one connection before moving on.
- **No backpressure.** If you read faster than you can write, per-connection buffers grow without bound. Stop reading from the source (unregister `EVENT_READ`) while the outgoing buffer is above a high-water mark.
- **Callback hell and lost errors.** `async`/`await` (Python asyncio, JavaScript, Rust) is syntax over the same loop: an await can suspend, but an already-completed operation may continue immediately (for example in Python); language/runtime behavior differs.

> [!tip] Know which thread you're on
> Most event-loop libraries aren't thread-safe. To hand work back to a loop from another thread, use its wake-up mechanism: `uv_async_send` in libuv, `loop.call_soon_threadsafe` in asyncio. The backend wakeup mechanism is platform-specific, such as an eventfd, pipe or completion notification.

> [!note] Workload evidence gap
> Fixed Redis latency/throughput, universal connection capacities and an unreproduced nginx speedup figure are omitted. Measure the deployed workload and runtime. The echo example bounds queued payload per connection; it does not implement production admission control, timeouts or global memory limits.

## Key takeaways
- Ordinary Redis command execution is serial despite background and I/O work.
- Long commands or callbacks delay peers on their loop.
- Partition work across loops and preserve backpressure.

## Further reading
- [The Node.js Event Loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Design overview — libuv documentation](https://docs.libuv.org/en/v1.x/design.html)
- [Thread pool work scheduling — libuv documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
- [Inside NGINX: How We Designed for Performance & Scale](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale)
- [aio and thread pools — nginx documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#aio)
- [Redis latency diagnosis — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [selectors — Python documentation](https://docs.python.org/3/library/selectors.html)
