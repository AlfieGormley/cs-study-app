---
id: io-uring-request-lifecycle
title: Submitting and collecting one request
level: advanced
minutes: 2
summary: liburing wraps ring setup, submission and completion collection.
sourceLesson: io-uring
---

An io_uring application places requests in a shared submission queue and collects results from a shared completion queue. A request tag ties each result to application state.

## The three system calls

- `io_uring_setup(entries, params)` creates the instance and returns a file descriptor; you `mmap` the ring buffers from it.
- `io_uring_enter(fd, to_submit, min_complete, flags)` tells the kernel "I've added *n* SQEs" and optionally waits for at least *m* completions.
- `io_uring_register(...)` sets up long-lived resources: files, buffers, eventfds, restrictions.

Applications commonly use the **liburing** wrappers; direct use requires following the ABI and memory-ordering rules. A minimal single-request liburing fragment follows (supply fd, a 4096-byte buffer, request data and error callbacks):

```c
#include <liburing.h>

struct io_uring ring;
int ret = io_uring_queue_init(
    256, &ring, 0);
if (ret < 0) {
    fail(-ret); exit(1);
}

struct io_uring_sqe *sqe =
    io_uring_get_sqe(&ring);
if (!sqe) { fail(ENOSPC); exit(1); }
/* Buffer stays alive until completion. */
io_uring_prep_read(sqe, fd, buf,
                   4096, 0);
/* Recover request ownership from CQEs. */
io_uring_sqe_set_data(sqe, req);
ret = io_uring_submit(&ring);
if (ret != 1) {
    fail(ret < 0 ? -ret : EIO); exit(1);
}

struct io_uring_cqe *cqe;
do {
    ret = io_uring_wait_cqe(&ring, &cqe);
} while (ret == -EINTR);
if (ret < 0) { fail(-ret); exit(1); }
struct request *r =
    io_uring_cqe_get_data(cqe);
if (cqe->res < 0)
    report(r, -cqe->res);   /* errno */
else
    done(r, cqe->res);      /* bytes */
/* Release the consumed completion slot. */
io_uring_cqe_seen(&ring, cqe);
io_uring_queue_exit(&ring);
```

Note that errors come back as **negative errno values** in `res`, not via the global `errno`.

## Key takeaways
- liburing wraps ring setup, submission and completion collection.
- A completion result contains a byte count or negative errno value.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
