---
id: fs-unix-file-interface
title: What the Unix file interface covers
level: basic
minutes: 2
summary: Many resources support descriptor I/O, but their setup and special operations differ.
sourceLesson: fs-file-abstraction
---

This unit focuses on what the Unix file interface covers. The preceding units provide the file and storage concepts used here.

## "Everything is a file"

Unix's big idea is that one interface (open, read, write, close) works for nearly everything:

- **Devices**: `/dev/sda` is a whole disk, `/dev/null` discards writes, `/dev/urandom` produces random bytes.
- **Pipes**: `ls | wc -l` connects two processes with a pair of descriptors.
- **Sockets**: once connected, a TCP socket accepts `read` and `write`.
- **Kernel state**: `/proc/self/status` shows your own process; `/sys/block/nvme0n1/queue/scheduler` exposes the I/O scheduler.

```
$ head -c 8 /dev/urandom | xxd
$ cat /proc/loadavg
0.42 0.37 0.31 1/523 81234
```

The payoff is composability: `cat`, `grep` and your own programs can reuse byte-stream operations for many of these, while seeking, readiness and device-specific behavior can differ.

> [!warning] Not quite everything
> The slogan describes a broad interface convention, not literally every kernel resource. Sockets need `socket`, `bind` and `connect` before they behave like files, devices need `ioctl` for anything beyond reading and writing (setting a terminal's baud rate, ejecting a disk), and network interfaces such as eth0 are not ordinary /dev stream nodes; related attributes do appear under /sys/class/net. Plan 9, Unix's successor from Bell Labs, took the idea much further.

I/O APIs such as readiness-oriented `epoll` and submission/completion-oriented `io_uring` also work in terms of descriptors; they get their own treatment in the next module.

## Pitfalls

- **Assuming `read` fills the buffer.** Always loop, or use a buffered wrapper.
- **Leaking descriptors.** Use `with open(...)` in Python, or `try/finally` around `os.close`.
- **Expecting `close` to mean "on disk".** It doesn't. Data may sit in memory for many seconds (the durability units cover `fsync`).
- **Relying on `O_APPEND` over NFS.** On a local file system, "seek to end and write" happens as one atomic step. NFS has no atomic append, so concurrent appenders can overwrite each other.

## Key takeaways
- Many resources support descriptor I/O, but their setup and special operations differ.
- Close does not promise durability, and append semantics depend on the filesystem.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
