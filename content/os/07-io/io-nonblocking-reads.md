---
id: io-nonblocking-reads
title: Non-blocking sockets and regular files
level: intermediate
minutes: 2
summary: EAGAIN means try again rather than end of stream.
sourceLesson: io-models
---

For ordinary buffered socket input, first wait for readiness, then copy available bytes into the caller’s buffer. Non-blocking mode changes the waiting part; a successful read still finishes its copy before returning.

## 2. Non-blocking I/O

Set `O_NONBLOCK` on the descriptor and `read()` never sleeps during phase 1. For supported socket operations with no available data, EOF or other result, it reports `EAGAIN` or `EWOULDBLOCK`. Portable code checks both; these constants need not be equal on every platform.

```c
/* Preserve existing status flags. */
int fl = fcntl(fd, F_GETFL, 0);
if (fl == -1) {
    perror("F_GETFL"); exit(1);
}
if (fcntl(fd, F_SETFL,
          fl | O_NONBLOCK) == -1) {
    perror("F_SETFL"); exit(1);
}

ssize_t n = read(fd, buf, sizeof buf);
if (n < 0 && (errno == EAGAIN ||
              errno == EWOULDBLOCK)) {
    /* nothing yet: do other work */
}
```

The Python equivalent raises `BlockingIOError`. This fragment performs a blocking connection setup first; its remote result is environment-dependent and it prints no fixed output:

```python
import socket

s = socket.create_connection(
    ("example.com", 80))
# Only the receive uses non-blocking mode.
s.setblocking(False)
try:
    # No bytes yet can mean try later.
    data = s.recv(4096)
except BlockingIOError:
    data = None   # EAGAIN: try later
```

A naive use of non-blocking I/O can lead to **busy-polling**: loop over every socket calling `read()`, getting `EAGAIN` from almost all of them, burning CPU. Its real value is as a building block for model 3.

Note that phase 2 is still synchronous. When data *is* ready, `read()` copies it before returning.

> [!warning] O_NONBLOCK does nothing for regular files
> On Linux, `O_NONBLOCK` is ignored for regular files and block devices. A `read()` that needs storage can still wait for it; a cache miss is not itself proof that a device read is necessary (for example, a sparse-file hole needs none). select and poll always report regular files as ready, and epoll refuses them outright with `EPERM`. This is why Node.js runs file operations on a thread pool (covered elsewhere in this module).

## Key takeaways
- EAGAIN means try again rather than end of stream.
- O_NONBLOCK does not turn ordinary Linux regular-file reads into storage-completion events.

## Further reading
- [read(2) — Linux manual page](https://man7.org/linux/man-pages/man2/read.2.html)
- [fcntl(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fcntl.2.html)
- [aio(7) — POSIX asynchronous I/O overview](https://man7.org/linux/man-pages/man7/aio.7.html)
- [Asynchronous I/O — Wikipedia](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
