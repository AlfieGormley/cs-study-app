---
id: io-uring-batching-polling
title: Batching and submission polling
level: advanced
minutes: 2
summary: Batching amortises system calls under explicit assumptions.
sourceLesson: io-uring
---

An io_uring submission queue contains requests and its completion queue contains results. This unit separates batching from polling: both can reduce entry overhead, but neither is a universal performance win.

## Where overhead can be reduced

### Batching amortises syscalls

With epoll, every ready socket still needs its own `read` call after the wait. With io_uring the receives go into the ring and one `io_uring_enter` submits them all:

```formula
S_epoll = 1 + R
S_epoll = 1 + 100 = 101
S_uring = 1
where
S_epoll: system calls to serve one batch with epoll (one epoll_wait plus one read per socket)
S_uring: system calls to submit and wait for the same batch with io_uring (one io_uring_enter)
R: the number of ready sockets in the batch, here 100
In words: epoll needs one extra system call per ready socket, while io_uring can submit a whole batch and wait for its completions in a single call.
```

So 100 ready sockets cost 101 syscalls with epoll and, in the best case, 1 with io_uring. The model assumes all 100 SQEs fit in the ring and that one wait collects every completion; real loops sometimes need extra waits or retries.

Batching amortises syscall overhead. Mitigations, CPU architecture and workload affect the size of the saving; this lesson supplies no universal measured syscall-cost increase.

### SQPOLL: fewer submission syscalls

With `IORING_SETUP_SQPOLL`, the kernel starts a thread that **polls the SQ** for new entries. The application just writes SQEs and bumps the tail; the kernel thread picks them up. Completions are read straight from the CQ. With the poller active and the application collecting CQEs from shared memory, suitable steady-state I/O **can avoid submission and completion-wait system calls**. A blocking wait, idle wakeup or other control operation can still require a syscall.

The cost: a kernel thread spinning on a CPU. It goes to sleep after an idle timeout (`sq_thread_idle`), and the application must then wake it with `io_uring_enter` (liburing checks the `IORING_SQ_NEED_WAKEUP` flag for you). It's the polling trade-off introduced earlier in this module again.

## Key takeaways
- Batching amortises system calls under explicit assumptions.
- SQPOLL trades polling CPU time for fewer enter calls and still needs idle wakeups.

## Further reading
- [io_uring(7) — Linux manual page](https://man7.org/linux/man-pages/man7/io_uring.7.html)
- [io_uring_setup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/io_uring_setup.2.html)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
- [Lord of the io_uring (tutorial)](https://unixism.net/loti/)
- [Learnings from kCTF VRP's 42 Linux kernel exploits — Google Security Blog](https://security.googleblog.com/2023/06/learnings-from-kctf-vrps-42-linux.html)
- [io_uring — Wikipedia](https://en.wikipedia.org/wiki/Io_uring)
