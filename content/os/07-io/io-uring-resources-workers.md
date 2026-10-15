---
id: io-uring-resources-workers
title: Registered resources, workers and multishot I/O
level: advanced
minutes: 2
summary: Fixed resources amortise setup work with explicit ownership.
sourceLesson: io-uring
---

An io_uring SQE describes a requested operation; a CQE reports a result. The operation’s implementation and memory ownership depend on its opcode, flags and supported kernel features.

## Registered files and buffers

Ordinary descriptor resolution and resource management have costs, though optimized paths can avoid some reference work. Page pinning is required by some I/O paths, not every buffered copy into user memory. With `io_uring_register` you can set up in advance:

- **Fixed files**: refer to them by index; avoid ordinary per-operation descriptor-table resolution while retaining registration/resource bookkeeping.
- **Fixed buffers**: pages pinned once, reused for every `READ_FIXED` and `WRITE_FIXED`.

### Completion interfaces for files

Because it's completion-based, io_uring works for regular files, buffered or `O_DIRECT`, which epoll cannot. Execution depends on opcode, flags and kernel/filesystem support. One common path tries the operation **inline**, then defers if needed:

- For pollable files (sockets, pipes), it arms an internal poll handler and retries when ready. This can avoid dedicating a blocked worker to the wait; threads still execute submission and completion work.
- For things that can't be polled (e.g. a buffered read that misses the page cache on some file systems), it hands the work to an internal pool of kernel workers called **io-wq**.

### Fewer submissions for repetitive work

Newer kernels add features that cut per-operation overhead further:

- **Multishot accept** (5.19) and **multishot receive** (6.0): one SQE produces a stream of CQEs, one per accepted connection or received chunk.
- **Provided buffer rings**: instead of attaching a buffer to every receive up front, the app gives the kernel a pool, and the kernel picks a buffer only when data actually arrives. This can reduce dedicated per-connection buffer retention, but the shared pool still consumes memory and needs capacity/recycling controls.
- **Linked SQEs** (`IOSQE_IO_LINK`): order supported operations without a userspace round trip; errors can cancel subsequent soft-linked requests. Linking does not automatically replace a write length with the preceding read's result.
- **Zero-copy send** (`IORING_OP_SEND_ZC`, 6.0).

> [!example] Versioned integration examples
> PostgreSQL 18 documents an optional `io_method = io_uring` backend when built with support. libuv documents `UV_LOOP_USE_IO_URING_SQPOLL`, added in 1.49.0, for supported asynchronous filesystem operations. Availability and defaults depend on the deployed runtime, build and platform; inspect those settings.

## Key takeaways
- Fixed resources amortise setup work with explicit ownership.
- Completion-based file I/O may use io-wq workers.
- Multishot and provided-buffer features need version and capacity checks.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
