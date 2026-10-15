---
id: proc-ipc-atomic-fifos
sourceLesson: proc-ipc
title: "Atomic pipe writes and named FIFOs"
level: advanced
minutes: 2
summary: "PIPE_BUF limits interleaving guarantees, not pipe capacity or read boundaries."
---

PIPE_BUF limits interleaving guarantees, not pipe capacity or read boundaries. This lesson focuses on atomic pipe writes and named fifos.

## Atomic writes and `PIPE_BUF`


When several processes write to the same pipe, a write of at most **`PIPE_BUF`** bytes (4,096 on Linux; POSIX requires at least 512) is **atomic**: it won't be interleaved with other writers' data. Larger writes may be split and interleaved. This is why many processes can safely log short lines into one pipe.

### Named pipes (FIFOs)

Anonymous pipes commonly connect processes that inherit them, but descriptors can also be passed to unrelated processes over Unix sockets. A **FIFO** is a pipe with a name in the file system, so unrelated processes can find it:

```
$ mkfifo /tmp/jobs
$ cat /tmp/jobs &          # reader
$ echo "build" > /tmp/jobs # writer
build
```

The data still goes through a kernel buffer; nothing is written to disk.

## Key takeaways
- PIPE_BUF limits interleaving guarantees, not pipe capacity or read boundaries.
- A FIFO provides a filesystem name for a kernel byte stream.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
