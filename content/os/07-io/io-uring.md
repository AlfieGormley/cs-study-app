---
id: io-uring
title: io_uring
level: advanced
minutes: 14
summary: Linux's completion-based I/O interface, how its shared submission and completion rings work, how it can reduce per-operation overhead, and why Google, Docker and others restrict it.
---

epoll reduces repeated interest-set scanning, but applications still perform I/O after readiness notifications. Waits can cover many reads, so the cost is not invariably two syscalls per read. Ordinary regular files do not provide useful storage-completion readiness through epoll. Linux native AIO predates io_uring but has operation/filesystem limitations; O_DIRECT is not a universal requirement or a guarantee of non-blocking submission.

In 2019, Jens Axboe (maintainer of the Linux block layer) merged **io_uring** into Linux 5.1. It is a general-purpose, **completion-based** interface: you describe operations, the kernel performs them, and you collect the results. It covers files, sockets, timers and, by now, a growing, version-dependent set of I/O operations.

## The core idea: two rings in shared memory

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

Each ring has a **head** and a **tail**. One side only ever writes the tail (producer), the other only ever advances the head (consumer). In a single-user-producer/consumer design, index publication uses the required memory ordering rather than a userspace mutex. Multiple application threads must coordinate ring access, and kernel completion producers require their own synchronization; this is not a claim that the entire subsystem is lock-free. Ring sizes are powers of two, so the index of entry *i* is `i & (entries - 1)`.

This is the same descriptor-ring-plus-doorbell design that NICs and NVMe drives use (lesson 1), applied between user space and the kernel.

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

`user_data` is how you match completions to requests: typically a pointer to your request struct. Completions can arrive **out of order**: a cached read finishes before an earlier one that hit the disk.

## The three system calls

- `io_uring_setup(entries, params)` creates the instance and returns a file descriptor; you `mmap` the rings from it.
- `io_uring_enter(fd, to_submit, min_complete, flags)` tells the kernel "I've added *n* SQEs" and optionally waits for at least *m* completions.
- `io_uring_register(...)` registers long-lived resources: files, buffers, eventfds, restrictions.

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
io_uring_prep_read(sqe, fd, buf,
                   4096, 0);
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
io_uring_cqe_seen(&ring, cqe);
io_uring_queue_exit(&ring);
```

Note that errors come back as **negative errno values** in `res`, not via the global `errno`.

## Where overhead can be reduced

### 1. Batching amortises syscalls

With epoll, serving 100 ready sockets is 1 `epoll_wait` plus 100 `read` calls: 101 syscalls. With io_uring you can queue 100 receive SQEs and submit them in **one** `io_uring_enter`, which can also wait for completions in the same call.

Batching amortises syscall overhead. Mitigations, CPU architecture and workload affect the size of the saving; this lesson supplies no universal measured syscall-cost increase.

### 2. SQPOLL: fewer submission syscalls

With `IORING_SETUP_SQPOLL`, the kernel starts a thread that **polls the SQ** for new entries. The application just writes SQEs and bumps the tail; the kernel thread picks them up. Completions are read straight from the CQ. In steady state, I/O needs **zero** system calls.

The cost: a kernel thread spinning on a CPU. It goes to sleep after an idle timeout (`sq_thread_idle`), and the application must then wake it with `io_uring_enter` (liburing checks the `IORING_SQ_NEED_WAKEUP` flag for you). It's the polling trade-off from lesson 1 again.

### 3. Registered files and buffers

Ordinary descriptor resolution and resource management have costs, though optimized paths can avoid some reference work. Page pinning is required by some I/O paths, not every buffered copy into user memory. With `io_uring_register` you can pre-register:

- **Fixed files**: refer to them by index; avoid ordinary per-operation descriptor-table resolution while retaining registration/resource bookkeeping.
- **Fixed buffers**: pages pinned once, reused for every `READ_FIXED` and `WRITE_FIXED`.

### 4. Completion interfaces for files

Because it's completion-based, io_uring works for regular files, buffered or `O_DIRECT`, which epoll cannot. Execution depends on opcode, flags and kernel/filesystem support. One common path tries the operation **inline**, then defers if needed:

- For pollable files (sockets, pipes), it arms an internal poll handler and retries when ready. This can avoid dedicating a blocked worker to the wait; threads still execute submission and completion work.
- For things that can't be polled (e.g. a buffered read that misses the page cache on some file systems), it hands the work to an internal pool of kernel workers called **io-wq**.

### 5. Fewer submissions for repetitive work

Newer kernels add features that cut per-operation overhead further:

- **Multishot accept** (5.19) and **multishot receive** (6.0): one SQE produces a stream of CQEs, one per accepted connection or received chunk.
- **Provided buffer rings**: instead of attaching a buffer to every receive up front, the app gives the kernel a pool, and the kernel picks a buffer only when data actually arrives. This can reduce dedicated per-connection buffer retention, but the shared pool still consumes memory and needs capacity/recycling controls.
- **Linked SQEs** (`IOSQE_IO_LINK`): order supported operations without a userspace round trip; errors can cancel subsequent soft links. Linking does not automatically replace a write length with the preceding read's result.
- **Zero-copy send** (`IORING_OP_SEND_ZC`, 6.0).

> [!example] Versioned integration examples
> PostgreSQL 18 documents an optional `io_method = io_uring` backend when built with support. libuv documents `UV_LOOP_USE_IO_URING_SQPOLL`, added in 1.49.0, for supported asynchronous filesystem operations. Availability and defaults depend on the deployed runtime, build and platform; inspect those settings.

## Getting the numbers right

> [!note] Performance evidence gap
> No reproducible benchmark accompanies the original percentage gaps, per-core IOPS figures or workload ranking table. Those claims are omitted. Compare the actual kernel, operation mix, queue depth, CPU budget and storage/network configuration against a measured baseline; batching or polling can help some workloads and hurt others.

## Pitfalls

- **Buffer lifetime.** Keep ordinary read/receive buffers valid until the matching operation completes. For zero-copy send, the first CQE may not release the buffer: if MORE is set, await the notification CQE. Multishot operations and provided-buffer ownership have their own rules.
- **SQE consumption and referenced data lifetimes differ.** Follow each opcode's rules and SUBMIT_STABLE feature behavior; SQPOLL submission return does not necessarily prove the kernel already consumed the SQE. Payload buffers generally live through operation completion.
- **CQ overflow.** If you submit faster than you reap, the CQ can fill. With IORING_FEAT_NODROP, the kernel normally backlogs overflowed CQEs, at a memory/performance cost. Allocation failure can still lose events; NODROP is not an absolute no-loss guarantee. The CQ is twice the SQ size by default for this reason.
- **Cancellation** is asynchronous too (`IORING_OP_ASYNC_CANCEL`); the original operation may still complete.

## Security concerns

io_uring is a large, fast-moving subsystem that runs complex code on behalf of unprivileged processes, and it has had many serious bugs.

- In June 2023, Google reported that **60% of the Linux kernel exploits** submitted to its kCTF vulnerability reward programme in the previous year used io_uring, accounting for about **$1 million** of payouts. The same June 2023 post described then-current restrictions on ChromeOS, production servers and Android apps. This is historical reporting, not proof of every current Google deployment policy.
- The inspected upstream **Moby default seccomp profile** uses an allowlist that omits io_uring syscalls, denying them under that profile. Actual Docker/container policy depends on version, capabilities and the selected profile.
- **Visibility.** A monitor limited to ordinary syscall-entry events does not automatically see one read/open/send syscall per SQE. It may see setup/enter/register calls, while SQPOLL can process submissions without an enter call. Other hooks, audit support and io_uring-aware instrumentation may observe operations; syscall-entry visibility alone is not a complete security model.

Mitigations:

- `sysctl kernel.io_uring_disabled` (Linux 6.6): `0` allows everyone, `1` limits creation to privileged processes or members of the `kernel.io_uring_group` group, and `2` disables new ring creation for everyone. Existing rings remain usable under either restrictive value.
- `IORING_REGISTER_RESTRICTIONS` lets a process constrain opcodes/flags on a ring created with IORING_SETUP_R_DISABLED, before enabling and handing it to less trusted code. It is an allowlist, not a complete sandbox by itself.
- Seccomp can block `io_uring_setup` altogether.

> [!warning] Know your deployment target
> If you build on io_uring, check that your production environment allows it. Many container platforms and hardened kernels do not, so keep an epoll or thread-pool fallback.

## Key takeaways
- io_uring is completion-based: the application writes SQEs into a shared submission ring and reaps CQEs from a shared completion ring, matched by `user_data`.
- Shared rings can reduce submission/completion transfer overhead; correct ordering and concurrent-access coordination remain necessary. Payload copying is a separate issue.
- Gains come from batching, SQPOLL (no syscalls in steady state), registered files and buffers, completion-based file I/O and multishot operations.
- Errors arrive as negative errno in `cqe->res`, completions can be out of order, and buffer lifetime follows the operation, including zero-copy-send notification and multishot rules.
- Historical vulnerabilities motivated deployment restrictions. Check actual container policy and instrumentation; kernel.io_uring_disabled controls new ring creation rather than revoking existing rings.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
