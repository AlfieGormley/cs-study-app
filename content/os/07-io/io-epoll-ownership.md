---
id: io-epoll-ownership
title: epoll ownership, duplicate descriptors and herds
level: intermediate
minutes: 2
summary: One-shot rearming needs an ownership protocol.
sourceLesson: io-multiplexing
---

An epoll instance retains an interest list and reports ready descriptors in event batches. Correct dispatch also requires ownership rules and careful descriptor lifecycle management.

## Other flags

- `EPOLLONESHOT`: report the descriptor once, then disable it until re-armed with `EPOLL_CTL_MOD`. Useful when several threads call `epoll_wait` on the same instance, as part of an ownership protocol: finish processing before rearming, and coordinate other code paths and duplicate registrations.
- `EPOLLEXCLUSIVE` (Linux 4.5): when several epoll instances watch the same descriptor (e.g. a listening socket shared by worker processes), wake one or more exclusive instances instead of necessarily waking all. This addresses the **thundering herd**. `SO_REUSEPORT` (one listening socket per worker, with the kernel spreading connections) is the other common fix.

## Pitfalls

- **epoll registrations are keyed by both fd number and open file description.** If you `dup()` or `fork()` and then close one copy, the registration survives as long as another descriptor refers to the same open file, and you may get events for an fd number you've closed. Remove it with `EPOLL_CTL_DEL` before closing.
- **Regular files** can't be added; `epoll_ctl` returns `EPERM`. Use a thread pool or io_uring.
- **Stale events.** If handling event A closes connection B, a later event in the same batch may refer to B. Check your connection state before acting.

## Key takeaways
- One-shot rearming needs an ownership protocol.
- Exclusive watches or reuseport address listener herds.
- Duplicate descriptors and stale event batches require lifecycle care.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
