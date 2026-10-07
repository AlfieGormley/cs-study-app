---
id: io-multiplexing
title: select, poll and epoll
level: intermediate
minutes: 15
summary: How select, poll, epoll and kqueue work inside, why their costs differ, level- versus edge-triggered notification, and how they solved the C10K problem.
---

In 1999 Dan Kegel published a web page titled *The C10K problem*: how do you make one server handle ten thousand simultaneous clients? Waiting interfaces, scheduling, memory and application design were among the scaling challenges.

This lesson walks through the three generations of that interface on Unix (`select`, `poll` and `epoll`), plus BSD's `kqueue`, and compares their costs when many descriptors are idle.

## The problem in one picture

A server has N open connections. At any moment only a few are active. The thread wants to sleep until *any* of them has data, and then learn *which* ones.

```
 conns:  1  2  3  4 ... 9998 9999 10000
 ready:     *                *
 want:   "wake me, and tell me 2, 9998"
```

The interesting question is how much work each API does per call, and whether that work scales with N (all connections) or with the number that are actually ready.

## select

`select` (4.2BSD, 1983) takes three **bitmaps** (`fd_set`): descriptors to watch for reading, writing and exceptional conditions. Bit *k* represents descriptor *k*.

```c
fd_set rfds;
for (;;) {
    FD_ZERO(&rfds);
    int maxfd = -1;
    for (int i = 0; i < n; i++) {
        if (fds[i] < 0 ||
            fds[i] >= FD_SETSIZE) abort();
        FD_SET(fds[i], &rfds);
        if (fds[i] > maxfd)
            maxfd = fds[i];
    }
    int r = select(maxfd + 1, &rfds,
                   NULL, NULL, NULL);
    if (r < 0) {
        if (errno == EINTR) continue;
        perror("select"); break;
    }
    for (int i = 0; i < n; i++)
        if (FD_ISSET(fds[i], &rfds))
            handle(fds[i]);
}
```

What happens on each call:

1. The bitmaps are copied from user space into the kernel.
2. The kernel walks the bitmap from descriptor 0 up to `nfds - 1` (here `maxfd`), checking each descriptor whose bit is set, asking its driver "are you ready?" and registering the thread on its wait queue.
3. If none is ready, the thread sleeps. When woken, it rescans.
4. The kernel **overwrites** the bitmaps with the ready set and copies them back.
5. User code scans all N descriptors to find the set bits.

So every call costs O(maxfd), even if only one connection is active. It has two more problems:

- **Hard limit.** `fd_set` is a fixed-size bitmap of `FD_SETSIZE` bits, which is **1024** on Linux glibc. Calling `FD_SET` on descriptor 1024 or above writes past the end of the structure: undefined behaviour, often memory corruption.
- **Destructive.** Because the kernel overwrites the sets, you must rebuild them before every call (hence the `FD_ZERO` loop above).

## poll

`poll` (System V, mid-1980s) replaces bitmaps with an array of structures:

```c
struct pollfd p[MAXCONN];
/* p[i].fd = fd; p[i].events = POLLIN; */

int r;
do {
    r = poll(p, n, -1);
} while (r < 0 && errno == EINTR);
if (r < 0) { perror("poll"); exit(1); }
for (int i = 0; i < n; i++) {
    if (p[i].revents != 0)
        handle_events(p[i].fd,
                      p[i].revents);
}
```

This removes the fixed fd_set bitmap limit (process and resource limits still apply) and the destructive update (results go in a separate `revents` field). It doesn't fix the scaling. The whole array is still copied into the kernel and every entry checked on every call: O(N).

## Why scanning idle descriptors can be costly

Suppose 10,000 connections, of which 10 are active at any moment, and the server calls `poll` 10,000 times a second.

- Entries examined per call: 10,000.
- Entries examined per second: 10,000 × 10,000 = **100 million**, to find about 100,000 events.
- With an 8-byte struct pollfd, the input array is 80,000 bytes. In Linux v6.12, the output path writes each 2-byte revents field rather than copying the whole structure back: 20,000 result bytes. These counts exclude other access and scan costs.

The model performs much more scanning than useful event delivery; how much CPU time that consumes requires measurement. The cost is proportional to *connections*, when it should be proportional to *activity*.

## epoll

Linux's answer, added in kernel 2.5.44 (2002), splits the job into **registering interest** once and **waiting** many times. The kernel keeps the interest set between calls.

```c
int ep = epoll_create1(0);
if (ep < 0) { perror("epoll"); exit(1); }

struct epoll_event ev = {
    .events  = EPOLLIN,
    .data.fd = lfd,
};
if (epoll_ctl(ep, EPOLL_CTL_ADD,
              lfd, &ev) < 0) {
    perror("epoll_ctl"); exit(1);
}

struct epoll_event evs[64];
for (;;) {
    int n = epoll_wait(ep, evs, 64, -1);
    if (n < 0) {
        if (errno == EINTR) continue;
        perror("epoll_wait"); break;
    }
    for (int i = 0; i < n; i++)
        handle_events(evs[i].data.fd,
                      evs[i].events);
}
```

### How it works inside

An epoll instance holds two structures:

- An **interest list**: every registered descriptor, indexed by a red-black tree in the cited Linux implementation. Tree lookup/update is O(log N); total epoll_ctl cost also includes allocation, locking and target-specific checks.
- A **ready list**: a linked list of descriptors that have events pending.

When you add a descriptor, epoll hooks a **callback** onto that file's wait queue. When a packet arrives on a socket, the networking code wakes the socket's wait queue as it always does. That fires epoll's callback, which appends the socket to the ready list and wakes anyone in `epoll_wait`.

```
 packet -> socket wait queue
             |  callback
             v
 ready list: [fd 7] -> [fd 9998]
             |
 epoll_wait  +--> copies 2 events out
```

`epoll_wait` processes ready-list candidates and rechecks readiness, returning up to maxevents results. It avoids an obligatory full interest-set scan. **O(ready)** is a useful simplified model, not an exact bound based only on returned events: stale candidates, contention and device callbacks add work. The `data` field is yours: most servers store a pointer to their per-connection struct rather than the fd.

| API | Per-wait cost | FD limit | State kept |
|---|---|---|---|
| select | Scan model O(maxfd) | fd numbers < 1024 in glibc fd_set | No persistent interest set |
| poll | Scan model O(N) | Process/resource limits | No persistent interest set |
| epoll | Ready-candidate work | Process/watch/resource limits | Persistent kernel state |

There is a trade-off. Every change of interest (say, starting to watch for `EPOLLOUT` while a write is pending) is an extra `epoll_ctl` syscall. For a handful of descriptors that churn constantly, `poll` can be just as good.

## Level-triggered versus edge-triggered

epoll offers two notification modes. The names come from electronics: a level-triggered signal reacts to the *state* being high; an edge-triggered one reacts to the *transition*.

- **Level-triggered (default)**: a ready descriptor remains eligible for reporting until the condition clears; maxevents, other ready descriptors and races affect which call returns it. If 4 KB is waiting and you read 1 KB, the next `epoll_wait` reports it again. This is how `select` and `poll` behave.
- **Edge-triggered (`EPOLLET`)**: notifications arise from activity/readiness changes, and multiple events can coalesce. It is not a promise of exactly one notification per empty-to-nonempty transition. If you leave data unread, another reminder is not guaranteed; a connection can stall.

With edge-triggered mode, the rule is: **use non-blocking descriptors and read (or write) until `EAGAIN`**.

```c
for (;;) {
    ssize_t n = read(fd, buf, sizeof buf);
    if (n > 0) {
        consume(buf, n);
    } else if (n == 0) {
        close(fd);          /* EOF */
        break;
    } else if (errno == EINTR) {
        continue;
    } else if (errno == EAGAIN) {
        break;              /* drained */
    } else {
        close(fd);          /* error */
        break;
    }
}
```

Edge-triggered handling can reduce repeated ready reports, especially for writable sockets. Level-triggered handling is often simpler; subscribe to EPOLLOUT only while needed. Library/server modes depend on version and backend, so inspect the actual implementation rather than assuming a universal setting.

> [!warning] Starvation with edge-triggered reads
> "Read until EAGAIN" can let one fast client monopolise the loop. A common pattern is to read up to a fixed budget per wake-up, then put the connection on your own "still has data" list so it's served again after others, without waiting for epoll.

### Other flags

- `EPOLLONESHOT`: report the descriptor once, then disable it until re-armed with `EPOLL_CTL_MOD`. Useful when several threads call `epoll_wait` on the same instance, as part of an ownership protocol: finish processing before rearming, and coordinate other code paths and duplicate registrations.
- `EPOLLEXCLUSIVE` (Linux 4.5): when several epoll instances watch the same descriptor (e.g. a listening socket shared by worker processes), wake one or more exclusive instances instead of necessarily waking all. This addresses the **thundering herd**. `SO_REUSEPORT` (one listening socket per worker, with the kernel spreading connections) is the other common fix.

## Pitfalls

- **epoll registrations are keyed by both fd number and open file description.** If you `dup()` or `fork()` and then close one copy, the registration survives as long as another descriptor refers to the same open file, and you may get events for an fd number you've closed. Remove it with `EPOLL_CTL_DEL` before closing.
- **Regular files** can't be added; `epoll_ctl` returns `EPERM`. Use a thread pool or io_uring.
- **Stale events.** If handling event A closes connection B, a later event in the same batch may refer to B. Check your connection state before acting.

## kqueue on BSD and macOS

FreeBSD introduced **kqueue** in 2000 (Jonathan Lemon's design), and macOS, NetBSD and OpenBSD have it too. Like epoll it keeps state in the kernel and returns only ready events, but its interface is more general.

```c
int kq = kqueue();
struct kevent ch, ev[64];
EV_SET(&ch, fd, EVFILT_READ, EV_ADD,
       0, 0, conn);

/* register and wait in one call */
int n = kevent(kq, &ch, 1, ev, 64, NULL);
```

Differences from epoll:

- **One call does both.** `kevent` takes a list of changes *and* returns events, so updating interest doesn't need a separate syscall per change.
- **Filters, not just fds.** `EVFILT_READ` and `EVFILT_WRITE` for sockets, but also `EVFILT_VNODE` (file changed), `EVFILT_PROC` (process exited), `EVFILT_SIGNAL` and `EVFILT_TIMER`. Linux achieves the same by turning these into descriptors: `signalfd`, `timerfd`, `pidfd`, `inotify`.
- **Extra information.** For `EVFILT_READ` on a socket, the returned `data` field says how many bytes are available.
- **Edge-like behavior** can use EV_CLEAR, with filter-specific semantics. EV_ONESHOT deletes the event after delivery; EV_DISPATCH disables it for later re-enabling, closer to epoll's one-shot rearm model.

Windows takes a different path: IOCP is completion-based (previous lesson). Solaris has event ports. Libraries such as libuv, libevent and Rust's mio wrap all of these behind one interface.

## C10K, and after

With epoll and kqueue, 10,000 connections became routine; a single nginx worker can hold far more. The bottleneck moved elsewhere: per-connection memory, syscall costs (wait results and multiple reads may be batched), and data copies. Those are the problems that io_uring (next lesson) and kernel bypass (lesson 6) attack. People now talk about **C10M**, ten million connections.

## Key takeaways
- glibc fd_set restricts select to descriptor numbers below 1024; scanning/copying costs depend on the range. poll removes that bitmap cap but still scans its input array.
- epoll keeps the interest set in the kernel (a red-black tree) and fills a ready list via wait-queue callbacks, avoiding an obligatory full interest-set scan; actual wait work depends on candidate readiness, callbacks and contention.
- Level-triggered keeps ready descriptors eligible; edge-triggered does not promise reminders for unread data. Drain non-blocking I/O to EAGAIN or maintain your own pending-work queue.
- `EPOLLONESHOT` and `EPOLLEXCLUSIVE` (or `SO_REUSEPORT`) handle multi-threaded loops and the thundering herd.
- kqueue is the BSD/macOS equivalent, with batched changes and filters for files, processes, signals and timers.

> [!note] Example scope and evidence gap
> C snippets show registration and dispatch fragments, not complete servers. Supply headers, non-blocking descriptors, initialized arrays, cleanup and handlers that process data plus EOF/error/hangup conditions. Complexity and byte-count examples are models; no benchmark establishes universal connection capacity or CPU speedup.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
