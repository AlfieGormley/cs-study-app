---
id: io-select-descriptor-sets
title: select and destructive descriptor sets
level: intermediate
minutes: 3
summary: select overwrites the supplied sets, so rebuild or restore them.
sourceLesson: io-multiplexing
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

`select()` (4.2BSD, 1983) takes three **bitmaps** (`fd_set`): descriptors to watch for reading, writing and exceptional conditions. Each bit represents the descriptor with that same number.

```c
fd_set rfds;
for (;;) {
    /* select replaces the supplied set. */
    FD_ZERO(&rfds);
    int maxfd = -1;
    for (int i = 0; i < n; i++) {
        if (fds[i] < 0 ||
            fds[i] >= FD_SETSIZE) abort();
        /* Check bitmap range first. */
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

So the work per call grows with the highest descriptor number, not with how many descriptors are busy:

```formula
W_select = O(maxfd)
where
W_select: the work one select() call does (copying, checking and scanning bitmap bits)
maxfd: the highest descriptor number being watched; the kernel checks bits 0 to maxfd
O(...): Big-O notation, "grows at most in proportion to" the quantity in brackets, ignoring constant factors
In words: one select() call costs time in proportion to the highest descriptor number, even if only one connection is active.
```

For example, if a server's descriptors reach number 900, every call walks about 900 bits even when a single connection has data. It has two more problems:

- **Fixed descriptor limit.** `fd_set` is a fixed-size bitmap of `FD_SETSIZE` bits, which is **1024** on Linux glibc. Calling `FD_SET` on descriptor 1024 or above writes past the end of the structure: undefined behaviour, often memory corruption.
- **Destructive.** Because the kernel overwrites the sets, you must rebuild them before every call (hence the `FD_ZERO` loop above).

## Key takeaways
- select overwrites the supplied sets, so rebuild or restore them.
- glibc fd_set limits descriptor numbers, including when only a few descriptors are watched.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
