---
id: io-kqueue-portability
title: kqueue and portable server waits
level: intermediate
minutes: 2
summary: kqueue batches changes and events and supports multiple filter types.
sourceLesson: io-multiplexing
---

## kqueue on BSD and macOS

FreeBSD introduced **kqueue** in 2000 (Jonathan Lemon's design), and macOS, NetBSD and OpenBSD have it too. Like epoll it keeps state in the kernel and returns only ready events, but its interface is more general.

```c
int kq = kqueue();
struct kevent ch, ev[64];
/* Watch read readiness for this object. */
EV_SET(&ch, fd, EVFILT_READ, EV_ADD,
       0, 0, conn);

/* register and wait in one call */
int n = kevent(kq, &ch, 1, ev, 64, NULL);
```

Differences from epoll:

- **One call does both.** `kevent` takes a list of changes *and* returns events, so updating interest doesn't need a separate syscall per change.
- **Filters, not just fds.** `EVFILT_READ` and `EVFILT_WRITE` for sockets, but also `EVFILT_VNODE` (file changed), `EVFILT_PROC` (process exited), `EVFILT_SIGNAL` and `EVFILT_TIMER`. Linux achieves the same by turning these into descriptors: `signalfd`, `timerfd`, `pidfd`, `inotify`.
- **Event type matters.** EVFILT_READ reports readiness; other supported filters, such as FreeBSD EVFILT_AIO, can report asynchronous completion. It is too broad to classify every kqueue event as a socket-readiness event.
- **Extra information.** For `EVFILT_READ` on a socket, the returned `data` field says how many bytes are available.
- **Edge-like behavior** can use EV_CLEAR, with filter-specific semantics. EV_ONESHOT deletes the event after delivery; EV_DISPATCH disables it for later re-enabling, closer to epoll's one-shot rearm model.

Windows takes a different approach: IOCP is completion-based (introduced earlier). Solaris has event ports. Libraries such as libuv, libevent and Rust's mio wrap all of these behind one interface.

## C10K, and after

With epoll and kqueue, 10,000 connections became routine; a single nginx worker can hold far more. The bottleneck moved elsewhere: per-connection memory, syscall costs (wait results and multiple reads may be batched), and data copies. Those are the problems that io_uring (covered next) and kernel bypass (covered elsewhere in this module) attack. People now talk about **C10M**, ten million connections.

> [!note] Example scope and evidence gap
> C snippets show registration and dispatch fragments, not complete servers. Supply headers, non-blocking descriptors, initialized arrays, cleanup and handlers that process data plus EOF/error/hangup conditions. Complexity and byte-count examples are models; no benchmark establishes universal connection capacity or CPU speedup.

## Key takeaways
- kqueue batches changes and events and supports multiple filter types.
- Scalable waits still leave memory, syscall and copy costs to measure.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
