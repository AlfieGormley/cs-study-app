---
id: io-uring-buffer-completion
title: Buffer lifetime, overflow and cancellation
level: advanced
minutes: 2
summary: Keep payload buffers valid until their operation releases ownership.
sourceLesson: io-uring
---

A submitted io_uring operation can remain pending after the submitting function returns. Its result arrives through a completion entry, so resource ownership must follow the documented operation lifecycle.

## Getting the numbers right

> [!note] Performance evidence gap
> No reproducible benchmark accompanies the original percentage gaps, per-core IOPS figures or workload ranking table. Those claims are omitted. Compare the actual kernel, operation mix, queue depth, CPU budget and storage/network configuration against a measured baseline; batching or polling can help some workloads and hurt others.

## Pitfalls

- **Buffer lifetime.** Keep ordinary read/receive buffers valid until the matching operation completes. For zero-copy send, the first CQE may not release the buffer: if IORING_CQE_F_MORE is set, await the notification CQE. Multishot operations and provided-buffer ownership have their own rules.
- **SQE consumption and referenced data lifetimes differ.** Follow each opcode's rules and SUBMIT_STABLE feature behavior; SQPOLL submission return does not necessarily prove the kernel already consumed the SQE. Payload buffers generally live through operation completion.
- **CQ overflow.** If you submit faster than you collect completions, the CQ can fill. With IORING_FEAT_NODROP, the kernel normally backlogs overflowed CQEs, at a memory/performance cost. Allocation failure can still lose events; NODROP is not an absolute no-loss guarantee. The CQ is twice the SQ size by default for this reason.
- **Cancellation** is asynchronous too (`IORING_OP_ASYNC_CANCEL`); the original operation may still complete.

## Key takeaways
- Keep payload buffers valid until their operation releases ownership.
- NODROP overflow backlogging is conditional, rather than an absolute no-loss guarantee.
- Cancellation itself has a completion race.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
