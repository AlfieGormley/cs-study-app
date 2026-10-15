---
id: io-async-runtime-backends
title: What async means in a runtime
level: intermediate
minutes: 2
summary: Language async syntax does not choose the I/O backend.
sourceLesson: io-models
---

## What "async" really means

The word "async" is used for at least three different things:

1. **Asynchronous I/O interface**: completion is reported separately from submission; helper threads or kernel facilities may do the work (model 5).
2. **Non-blocking**: an operation avoids waiting for readiness and can report try-again (model 2). This is not a fixed elapsed-time guarantee. Non-blocking is not the same as asynchronous; a non-blocking `read()` that finds data does the copy synchronously.
3. **async/await in a language**: a programming style where a function can pause at `await` and let an event loop run other tasks. On Unix, default selector-based asyncio and libuv commonly use readiness APIs for sockets, with worker mechanisms for some blocking work. Windows uses different backends: Python's default ProactorEventLoop and libuv use IOCP. Runtime version and event-loop choice matter.

For Node.js on a typical Unix libuv backend, asynchronous JavaScript APIs can sit above non-blocking socket readiness and worker-based file operations. That does not make every operation universally non-blocking or every platform use epoll; synchronous APIs and CPU-heavy callbacks can still block the event loop.

> [!tip] The question to ask
> Whenever a framework claims to be "asynchronous", ask: who is waiting, and where? Is a thread sleeping in `epoll_wait`, in a worker pool, or nowhere at all because the kernel is doing the work? The answer tells you how it will scale and where it can stall.

## Choosing a model

- **A few connections, simple code**: blocking I/O, possibly a thread per connection. Easy to reason about.
- **Thousands of mostly idle connections**: multiplexing with non-blocking sockets, in an event loop.
- **Linux workloads needing completion interfaces or batching**: evaluate supported io_uring operations against a measured baseline.
- **Implementation matters**: glibc POSIX AIO has asynchronous completion semantics even though workers perform the I/O; signal-driven designs require careful state and signal handling.

> [!note] Deployment evidence gap
> No benchmark establishes connection-count limits, universal stack residency, copy latency or a fastest I/O model here. Numeric scenarios are assumptions; exact costs and runtime backends must be checked for the deployed version. C examples are fragments requiring headers, initialized descriptors/buffers and lifecycle cleanup. Keep asynchronous buffers/control blocks valid until completion.

## Key takeaways
- Language async syntax does not choose the I/O backend.
- Choose readiness, completion or workers using operation, platform and measured workload.

## Further reading
- [read(2) — Linux manual page](https://man7.org/linux/man-pages/man2/read.2.html)
- [fcntl(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fcntl.2.html)
- [aio(7) — POSIX asynchronous I/O overview](https://man7.org/linux/man-pages/man7/aio.7.html)
- [Asynchronous I/O — Wikipedia](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
