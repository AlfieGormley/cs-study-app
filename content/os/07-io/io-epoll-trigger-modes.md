---
id: io-epoll-trigger-modes
title: Level and edge notifications
level: intermediate
minutes: 2
summary: Edge mode does not guarantee another reminder for unread bytes.
sourceLesson: io-multiplexing
---

## Level-triggered versus edge-triggered

epoll offers two notification modes. The names come from electronics: a level-triggered signal reacts to the *state* being high; an edge-triggered one reacts to the *transition*.

- **Level-triggered (default)**: a ready descriptor remains eligible for reporting until the condition clears; maxevents, other ready descriptors and races affect which call returns it. If 4 KB is waiting and you read 1 KB, the next `epoll_wait` reports it again. This is how `select` and `poll` behave.
- **Edge-triggered (`EPOLLET`)**: notifications arise from activity/readiness changes, and multiple events can be merged into one report. It is not a promise of exactly one notification per empty-to-nonempty transition. If you leave data unread, another reminder is not guaranteed; a connection can stall.

With edge-triggered mode, the rule is: **use non-blocking descriptors and read (or write) until `EAGAIN`**.

```c
/* Keep reading until drained or closed. */
for (;;) {
    ssize_t n = read(fd, buf, sizeof buf);
    if (n > 0) {
        /* More bytes may remain. */
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

## Key takeaways
- Edge mode does not guarantee another reminder for unread bytes.
- Drain non-blocking I/O or preserve pending work locally.
- Watch writability only while output needs sending.

## Further reading
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [epoll(7) — Linux manual page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- [select(2) — Linux manual page](https://man7.org/linux/man-pages/man2/select.2.html)
- [poll(2) — Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Kqueue: A generic and scalable event notification facility — Jonathan Lemon (PDF)](https://people.freebsd.org/~jlemon/papers/kqueue.pdf)
- [kqueue(2) — FreeBSD manual page](https://man.freebsd.org/cgi/man.cgi?query=kqueue)
