---
id: io-readiness-notifications
title: Multiplexing and signal notifications
level: intermediate
minutes: 2
summary: A readiness notification asks the application to perform the read.
sourceLesson: io-models
---

For ordinary buffered socket input, phase 1 waits for readiness and phase 2 copies bytes into the caller’s buffer. The interfaces here change how readiness is reported, while the application still performs the read.

## 3. I/O multiplexing

Instead of blocking in `read()` on one descriptor, block in a call that watches **many** descriptors and returns when any is ready: `select`, `poll`, `epoll` on Linux, `kqueue` on BSD and macOS.

```
select/epoll_wait  --> blocks (phase 1)
   returns "fd 7 is readable"
read(7)            --> copies (phase 2)
```

One thread can now serve tens of thousands of connections. This is the foundation of nginx, Redis, Node.js and Python's `asyncio`. The multiplexing units below cover these calls in detail.

Multiplexing tells you about **I/O readiness**: "a read on fd 7 will not block now". You still do the I/O yourself. Descriptors are normally also set non-blocking, because readiness can become stale or be spurious. An ordinary stream read need not wait to fill its buffer, but flags such as MSG_WAITALL and concurrent readers require care.

## 4. Signal-driven I/O

Ask the kernel to send a `SIGIO` signal when a descriptor becomes ready:

```c
/* Handler must use signal-safe work. */
signal(SIGIO, on_sigio);
fcntl(fd, F_SETOWN, getpid());
int fl = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, fl | O_ASYNC);
```

This is a setup fragment: supply a handler and valid descriptor, check registration/fcntl failures and arrange cleanup.

The process carries on running; the signal handler (or a main loop it nudges) then calls `read()`. Phase 1 doesn't block; phase 2 still does.

Standard SIGIO notifications can be merged into one, so programs must re-check descriptor state rather than count signals as events. Signal handlers have async-signal-safety restrictions. Linux `F_SETSIG` with `SA_SIGINFO` can include descriptor/event information, and real-time signals can queue subject to resource limits; fallback to SIGIO is possible. Multiplexing often makes per-descriptor event handling easier.

In Stevens’ POSIX-based classification, these reads are synchronous: the calling thread completes its ordinary read and copy before using the returned result. Waiting on many descriptors or receiving a signal changes readiness notification, while a separate completion interface changes how the finished operation is collected.

## Key takeaways
- A readiness notification asks the application to perform the read.
- Readiness may become stale; signal notifications may merge and require signal-safe handling.

## Further reading
- [read(2) — Linux manual page](https://man7.org/linux/man-pages/man2/read.2.html)
- [fcntl(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fcntl.2.html)
- [aio(7) — POSIX asynchronous I/O overview](https://man7.org/linux/man-pages/man7/aio.7.html)
- [Asynchronous I/O — Wikipedia](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
