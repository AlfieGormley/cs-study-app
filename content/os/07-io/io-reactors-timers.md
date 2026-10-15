---
id: io-reactors-timers
title: Reactor, proactor and timer scheduling
level: advanced
minutes: 3
summary: Reactors dispatch readiness; proactors dispatch completion.
sourceLesson: io-event-loops
---

## Reactor and proactor

Two named patterns describe the two I/O models introduced earlier in this module:

| Pattern | Loop tells you | Built on |
|---|---|---|
| Reactor | "fd is ready, you do it" | epoll, kqueue |
| Proactor | "your op is done" | IOCP, io_uring |

The `selectors` example is a reactor. Windows IOCP and submitted io_uring reads/writes provide completion interfaces suitable for proactors. Interpret the operation, not only the API name: io_uring also has readiness-poll requests, and some kqueue filters can report AIO completions. Libraries often present a proactor-style API ("call me back with the data") on top of a reactor: libuv's `uv_read_start` gives you bytes, though underneath it waited on epoll and called `read()` itself.

## Timers

Servers need timeouts: idle connections, retries, `setTimeout`. A loop keeps pending timers in a **min-heap** keyed by expiry time (libuv uses a binary min-heap; nginx uses a red-black tree).

A min-heap keeps the earliest expiry at its root, which gives these costs and the wait timeout:

```formula
C_insert = O(log_2(n))
C_next = O(1)
t_wait = max(0 ms, t_next − t_now)
t_wait = 120 ms − 100 ms = 20 ms
where
C_insert: the work to add one timer to the min-heap
C_next: the work to find the earliest expiry (read the root)
n: the number of pending timers in the min-heap
log_2: logarithm base 2, how many times n can be halved before reaching 1
O(...): Big-O notation, "grows at most in proportion to" the quantity in brackets; O(1) means constant, independent of n
t_wait: the timeout the loop passes to its wait call (for example epoll_wait), in milliseconds (ms)
t_next: the expiry time of the earliest pending timer, here 120 ms on the loop's clock
t_now: the current time on the same clock, here 100 ms
max: chooses the larger argument, ensuring an already-due timer requests no wait
ms: millisecond, one thousandth of a second
In words: adding a timer costs about one extra step each time the timer count doubles, finding the next one is instant, and the loop asks to sleep until the next timer is due unless I/O wakes it sooner.
```

With a million pending timers an insert takes at most about 20 min-heap steps, because twenty binary levels cover that many timers. The loop requests a wait no longer than the time to the next expiry; interruption, timer granularity and scheduling can alter actual wakeup time, and the loop must re-read the clock after every wait rather than reuse its previous current-time value.

A timer establishes a scheduling threshold, not an exact deadline. Long callbacks can delay it substantially. Runtime clock granularity and rounding mean a nominal millisecond value is not a precision timing contract.

## Key takeaways
- Reactors dispatch readiness; proactors dispatch completion.
- The earliest timer determines a non-negative wait request.
- Scheduling thresholds do not guarantee an exact firing time.

## Further reading
- [The Node.js Event Loop — Node.js docs](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [Design overview — libuv documentation](https://docs.libuv.org/en/v1.x/design.html)
- [Thread pool work scheduling — libuv documentation](https://docs.libuv.org/en/v1.x/threadpool.html)
- [Inside NGINX: How We Designed for Performance & Scale](https://blog.nginx.org/blog/inside-nginx-how-we-designed-for-performance-scale)
- [aio and thread pools — nginx documentation](https://nginx.org/en/docs/http/ngx_http_core_module.html#aio)
- [Redis latency diagnosis — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/latency/)
- [selectors — Python documentation](https://docs.python.org/3/library/selectors.html)
