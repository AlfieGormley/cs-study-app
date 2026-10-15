---
id: io-node-phases-workers
title: Node phases and libuv workers
level: advanced
minutes: 2
summary: Node phase ordering is runtime-version dependent.
sourceLesson: io-event-loops
---

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

Ordinary network socket readiness/completion for asynchronous APIs uses the platform backend rather than a blocked pool worker per socket. Unix often uses epoll/kqueue; Windows uses IOCP. DNS lookup can still use the pool.

## Key takeaways
- Node phase ordering is runtime-version dependent.
- The shared libuv worker pool can queue DNS behind other work.

## Further reading
- [The Node.js Event Loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Design overview — libuv documentation](https://docs.libuv.org/en/v1.x/design.html)
- [Thread pool work scheduling — libuv documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
- [Inside NGINX: How We Designed for Performance & Scale](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale)
- [aio and thread pools — nginx documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#aio)
- [Redis latency diagnosis — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [selectors — Python documentation](https://docs.python.org/3/library/selectors.html)
