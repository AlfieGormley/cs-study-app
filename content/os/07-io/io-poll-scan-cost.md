---
id: io-poll-scan-cost
title: poll and the cost of scanning idle connections
level: intermediate
minutes: 3
summary: poll removes the fixed bitmap cap but scans its input array.
sourceLesson: io-multiplexing
---

## poll

`poll()` (System V, mid-1980s) replaces bitmaps with an array of structures:

```c
struct pollfd p[MAXCONN];
/* p[i].fd = fd; p[i].events = POLLIN; */

/* Initialize each watched entry first. */
int r;
do {
    r = poll(p, n, -1);
} while (r < 0 && errno == EINTR);
if (r < 0) { perror("poll"); exit(1); }
/* revents holds this call’s results. */
for (int i = 0; i < n; i++) {
    if (p[i].revents != 0)
        handle_events(p[i].fd,
                      p[i].revents);
}
```

This removes the fixed fd_set bitmap limit (process and resource limits still apply) and the destructive update (results go in a separate `revents` field). It doesn't fix the scaling. The whole array is still copied into the kernel and every entry checked on every call: O(N), where N is the number of array entries.

## Why scanning idle descriptors can be costly

Suppose 10,000 connections, of which 10 are active at any moment, and the server calls `poll()` 10,000 times a second. Because `poll()` checks every entry on every call, the work per second is the number of registered entries times the call rate, while the useful work is only the ready entries times the call rate:

```formula
E_scan = Nr
E_scan = 10,000 × 10,000 /s
E_scan = 100,000,000 /s
E_ready = Rr = 10 × 10,000 /s
E_ready = 100,000 /s
where
E_scan: entries the kernel examines per second
E_ready: events actually found per second
N: registered connections (entries in the pollfd array), here 10,000
R: connections that are ready on each call, here 10
r: poll() calls per second, here 10,000
s: second; "/s" means per second
In words: poll examines a thousand entries for every event it finds, because its work follows the number of connections rather than the number that are active.
```

The bytes copied per call follow the same pattern:

```formula
B_in = N × 8 B = 80,000 B
B_out = N × 2 B = 20,000 B
where
B_in: bytes copied into the kernel per call, in bytes (B)
B_out: bytes written back per call, in bytes (B)
N: entries in the array, here 10,000
B: byte, 8 bits
In words: each call copies the whole 80,000-byte array in and writes 20,000 bytes of results back, however few connections are busy.
```

The 8 bytes are the size of one `struct pollfd` on Linux (a 4-byte descriptor plus two 2-byte event fields). In Linux v6.12, the output path writes each 2-byte `revents` field rather than copying the whole structure back. These counts exclude other access and scan costs.

The model performs much more scanning than useful event delivery; how much CPU time that consumes requires measurement. The cost is proportional to *connections*, when it should be proportional to *activity*.

## Key takeaways
- poll removes the fixed bitmap cap but scans its input array.
- Entry and byte-count models describe work, rather than measured CPU speedup.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
