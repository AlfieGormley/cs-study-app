---
id: io-nginx-worker-loops
title: nginx worker loops and connection slots
level: advanced
minutes: 2
summary: nginx spreads independent event loops across worker processes.
sourceLesson: io-event-loops
---

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
- `worker_connections` caps connections per worker (the default is 512; production configs often raise it to thousands). Multiplying the two gives the most connection slots nginx can hold at once:

```formula
C_max = W C_w
C_max = 4 × 512 = 2,048
where
C_max: the aggregate connection-slot ceiling for the whole nginx instance
W: the number of worker processes, here 4
C_w: the worker_connections setting, the slot limit per worker, here the default 512
In words: four workers with the default 512 slots each can hold at most 2,048 connections between them.
```

This is a ceiling, not a guarantee of that many clients: when nginx proxies, each client also uses a slot for the upstream connection, so if every client has a request in flight to an upstream server, 2,048 slots serve only about 1,024 clients at once. Descriptor and resource limits can cap it lower still.
- Workers share the listening sockets. With `listen ... reuseport`, each worker gets its own `SO_REUSEPORT` socket and the kernel spreads new connections between them, avoiding the thundering herd and lock contention on a shared accept queue.
- Per-worker connections reduce shared-state contention, but shared-memory zones and other coordination can still use locks.

Because each worker is a loop, a blocking disk read stalls every connection on that worker. nginx added **thread pools** (`aio threads`, version 1.7.11) to offload reads that miss the page cache. Performance depends on storage, files, concurrency and configuration; no benchmark reproduction is included here.

The master process never handles traffic. It re-reads config on `SIGHUP`, starts new workers, and lets old ones finish their connections: this supports graceful reloads, but errors, timeouts and worker shutdown limits mean zero dropped requests is not an unconditional guarantee.

## Key takeaways
- nginx spreads independent event loops across worker processes.
- Worker connection slots include upstream connections and face resource limits.
- Threaded file I/O can move supported blocking reads off a worker loop.

## Further reading
- [The Node.js Event Loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Design overview — libuv documentation](https://docs.libuv.org/en/v1.x/design.html)
- [Thread pool work scheduling — libuv documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
- [Inside NGINX: How We Designed for Performance & Scale](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale)
- [aio and thread pools — nginx documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#aio)
- [Redis latency diagnosis — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [selectors — Python documentation](https://docs.python.org/3/library/selectors.html)
