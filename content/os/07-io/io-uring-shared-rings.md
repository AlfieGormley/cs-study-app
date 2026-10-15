---
id: io-uring-shared-rings
title: Submission and completion rings
level: advanced
minutes: 4
summary: The application produces SQEs and consumes CQEs.
sourceLesson: io-uring
---

epoll reduces repeated interest-set scanning, but applications still perform I/O after readiness notifications. Waits can cover many reads, so the cost is not invariably two syscalls per read. Ordinary regular files do not provide useful storage-completion readiness through epoll. Linux native AIO predates io_uring but has operation/filesystem limitations; O_DIRECT is not a universal requirement or a guarantee of non-blocking submission.

In 2019, Jens Axboe (maintainer of the Linux block layer) merged **io_uring** into Linux 5.1. It is a general-purpose, **completion-based** interface: you describe operations, the kernel performs them, and you collect the results. It covers files, sockets, timers and, by now, a growing, version-dependent set of I/O operations.

## The core idea: two ring buffers in shared memory

An io_uring instance is a pair of **ring buffers** that both the application and the kernel can see, because they are `mmap`ped into the process:

- The **submission queue (SQ)**: the application writes **SQEs** (submission queue entries, normally 64 bytes; optional extended formats exist) describing operations.
- The **completion queue (CQ)**: the kernel writes **CQEs** (completion queue entries, normally 16 bytes; extended formats also exist) with results.

```
   application            kernel
  +-----------+  SQEs  +-----------+
  | writes    | -----> | consumes  |
  | SQ tail   |   SQ   | SQ head   |
  +-----------+        +-----------+
  | reads     | <----- | writes    |
  | CQ head   |   CQ   | CQ tail   |
  +-----------+  CQEs  +-----------+
```

Each ring has a **head** and a **tail**. One side only ever writes the tail (producer), the other only ever advances the head (consumer). In a single-user-producer/consumer design, index publication uses the required memory ordering rather than a userspace mutex. Multiple application threads must coordinate ring access, and kernel completion producers require their own synchronization; this is not a claim that the entire subsystem is lock-free. Ring sizes are powers of two. The head and tail are finite-width free-running counters that increase and eventually wrap, so each side turns a counter into an array slot by taking the remainder after dividing by the ring size, which for a power of two is a single bitwise AND:

```formula
k = i mod E
k = i & (E − 1)
k = 1,000 mod 256 = 232
where
k: the array slot (0 to E − 1) where entry number i lives
i: the free-running counter value (head or tail), here 1,000
E: the number of entries in the ring, a power of two, here 256
mod: modulo, the remainder after whole-number division
&: bitwise AND, keeping only the bits set in both numbers; E − 1 is a mask of all-ones low bits
In words: the counter just keeps counting, and the low bits of it pick the slot, so the ring wraps round with no division.
```

With 256 entries the mask is 255 (binary 11111111), so counter 1,000 lands in slot 232, because 1,000 = 3 × 256 + 232. The AND trick only works when the ring size is a power of two; for other sizes the low bits would not equal the remainder.

This is the same descriptor-ring-plus-doorbell design that NICs and NVMe drives use (covered elsewhere in this module), applied between user space and the kernel.

## What's in an entry

An SQE says what to do:

| Field | Meaning |
|---|---|
| `opcode` | READ, WRITE, ACCEPT, SEND... |
| `fd` | Target descriptor |
| `addr`, `len` | Buffer and length |
| `off` | File offset |
| `user_data` | 64-bit tag, yours |

A CQE gives the result:

| Field | Meaning |
|---|---|
| `user_data` | Copied from the SQE |
| `res` | Like a syscall return; `-errno` on error |
| `flags` | Extra info (e.g. buffer id) |

`user_data` is how you match completions to requests: typically a pointer to your request struct. Completions can arrive **out of order**: a read served from the page cache finishes before an earlier one that hit the disk.

## Key takeaways
- The application produces SQEs and consumes CQEs.
- Tags match results to requests even when completion order differs.
- Memory ordering and concurrent-access coordination still matter.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
