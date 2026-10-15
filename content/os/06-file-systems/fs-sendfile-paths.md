---
id: fs-sendfile-paths
title: Sendfile, TLS and asynchronous I/O
level: intermediate
minutes: 3
summary: Sendfile can avoid copying payload through user space on suitable paths.
sourceLesson: fs-page-cache
---

This unit focuses on sendfile, TLS and asynchronous I/O. The preceding units provide the file and storage concepts used here.

## Zero-copy: sendfile

A static file server's inner loop looks like this:

```python
# Partial server loop: fd and sock exist.
# Empty read ends this regular-file scan.
while chunk := os.read(fd, 65536):
    # sendall handles short socket sends.
    sock.sendall(chunk)
```

Count the copies for each chunk:

```
 disk --DMA--> page cache
 page cache --CPU--> user buffer
 user buffer --CPU--> socket buffer
 socket buffer --DMA--> NIC
```

In this simplified uncached conventional path there are two CPU copies plus device transfers, with read/send calls per chunk. Actual copy and syscall counts depend on cache state, short transfers, offloads and implementation. The data never needed to visit user space.

`sendfile(out_fd, in_fd, offset, count)` asks the kernel to move data from a file to a socket directly:

```python
# Partial call: caller supplies values.
# Return value counts bytes actually sent;
# callers must handle short sends/errors.
os.sendfile(sock.fileno(), fd,
            offset, count)
```

```
 disk --DMA--> page cache
 page cache --> NIC (DMA gather)
```

With a network card that supports scatter-gather DMA, the kernel just hands the NIC pointers to the page cache pages. This can eliminate payload copies through user space and, with a suitable implementation, CPU payload copies on the transmit path. The exact copying depends on offloads, transforms and fallback paths; zero-copy is a path capability, not a universal count guarantee.

Real uses:

- **Kafka** can use file-transfer paths for suitable plaintext log delivery; encryption, conversion and configuration can select other paths.
- **nginx** has `sendfile on;` for static files.
- `splice` and `vmsplice` generalise the idea through pipes.

The catch: the kernel sends the bytes as they are. If you need to compress or encrypt them in user space, as with TLS, you lose the benefit, unless you use kernel TLS (kTLS), which lets the kernel encrypt during `sendfile`.

## Where async I/O fits

Buffered hits can avoid payload-storage latency. Writes can block on write throttling, allocation or I/O, and a read miss has to wait for its data. Thread pools, `epoll` (for sockets) and `io_uring` (for files and sockets) exist to overlap many such operations. They're the subject of the next module.

## Key takeaways
- Sendfile can avoid copying payload through user space on suitable paths.
- Encryption, offloads and fallback paths determine actual copying; async APIs overlap waiting work.

## Further reading
- [Page cache — Wikipedia](https://en.wikipedia.org/wiki/Page_cache)
- [Documentation for /proc/sys/vm (dirty_* settings) — kernel.org](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [open(2): O_DIRECT notes — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [posix_fadvise(2) — Linux manual page](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [sendfile(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sendfile.2.html)
- [Are You Sure You Want to Use MMAP in Your DBMS? — CIDR 2022](https://db.cs.cmu.edu/mmap-cidr2022/)
- [Zero-copy — Wikipedia](https://en.wikipedia.org/wiki/Zero-copy)
