---
id: io-epoll-interest-ready
title: epoll interest and ready lists
level: intermediate
minutes: 4
summary: epoll retains registrations and wakes through ready-list callbacks.
sourceLesson: io-multiplexing
---

## epoll

Linux's answer, added in kernel 2.5.44 (2002), splits the job into **registering interest** once and **waiting** many times. The kernel keeps the interest set between calls.

```c
int ep = epoll_create1(0);
if (ep < 0) { perror("epoll"); exit(1); }

struct epoll_event ev = {
    .events  = EPOLLIN,
    .data.fd = lfd,
};
/* Retain interest across wait calls. */
if (epoll_ctl(ep, EPOLL_CTL_ADD,
              lfd, &ev) < 0) {
    perror("epoll_ctl"); exit(1);
}

struct epoll_event evs[64];
for (;;) {
    /* One batch can contain many fds. */
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

- An **interest list**: every registered descriptor, indexed by a red-black tree in the cited Linux implementation. Tree lookup/update is O(log N), where N is the number of registered descriptors; total epoll_ctl cost also includes allocation, locking and target-specific checks.
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

The three APIs can be compared with one simplified cost model per wait call:

```formula
W_select = O(maxfd)
W_poll = O(N)
W_epoll ≈ O(R)
C_ctl = O(log_2(N))
where
W_select, W_poll, W_epoll: the work one wait call does with each API
maxfd: the highest descriptor number passed to select()
N: the number of registered descriptors (connections being watched)
R: the number of ready candidates on epoll's ready list, the "O(ready)" of the text
C_ctl: the tree part of one epoll_ctl() change (insert, modify or delete in the red-black tree)
log_2: logarithm base 2, the number of times you can halve a number before reaching 1
O(...): Big-O notation, "grows at most in proportion to" the quantity in brackets, ignoring constant factors
≈: approximately; epoll's real cost also includes stale candidates, locking and callbacks
In words: select and poll pay for every watched descriptor on every call, epoll pays roughly for the ready ones, and epoll moves the per-descriptor cost into a logarithmic registration step.
```

With 10,000 connections of which 10 are ready, poll checks 10,000 entries per call while epoll handles about 10 candidates; the base-two logarithm of 10,000 is about 13.3, under a simplified logarithmic model. A real red-black tree can have a different height and each level can involve multiple operations. The model ignores constant factors, so for a handful of descriptors poll can be just as fast.

| API | Per-wait cost | FD limit | State kept |
|---|---|---|---|
| select | Scan model O(maxfd) | Descriptor numbers below 1024 in glibc | No persistent interest set |
| poll | Scan model O(N) | Process/resource limits | No persistent interest set |
| epoll | Ready-candidate work | Process/watch/resource limits | Persistent kernel state |

There is a trade-off. Every change of interest (say, starting to watch for `EPOLLOUT` while a write is pending) is an extra `epoll_ctl` syscall. For a handful of descriptors that churn constantly, `poll` can be just as good.

## Key takeaways
- epoll retains registrations and wakes through ready-list callbacks.
- Ready-candidate work and tree-index work are distinct costs.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
