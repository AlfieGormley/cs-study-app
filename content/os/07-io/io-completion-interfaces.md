---
id: io-completion-interfaces
title: Submission, completion and helper threads
level: intermediate
minutes: 3
summary: A completion interface separates requesting work from collecting its result.
sourceLesson: io-models
---

The earlier units separated waiting for socket readiness (phase 1) from copying into the caller’s buffer (phase 2). Completion interfaces instead expose the finished operation separately from its submission.

## 5. Asynchronous I/O

Request "read into this buffer and report when it is **done**". A completion interface separates submission from collecting the result. The operation may finish before submission returns or later, and the implementation may use kernel machinery or helper threads. Submission itself still has cost and possible errors.

POSIX defines `aio_read` for this:

```c
struct aiocb cb = {0};
cb.aio_fildes = fd;
cb.aio_buf    = buf;
cb.aio_nbytes = sizeof buf;
cb.aio_offset = 0;
/* Collect status explicitly: no signal. */
cb.aio_sigevent.sigev_notify = SIGEV_NONE;

if (aio_read(&cb) == -1) {
    perror("aio_read"); exit(1);
}
do_other_work();
while (aio_error(&cb) == EINPROGRESS)
    ;                  /* or aio_suspend */
int status = aio_error(&cb);
/* Collect the result exactly once. */
ssize_t n = aio_return(&cb);
/* status: completion error, or 0. */
```

The catch on Linux: glibc's POSIX AIO is implemented in user space with a pool of threads doing ordinary blocking calls. Linux native AIO (`io_submit`) has operation/filesystem limitations, and submission can block even with direct I/O in some code paths. **io_uring**, introduced in Linux 5.1 in 2019, provides a broader completion interface; it can also use worker threads and has operation-specific support rules (covered elsewhere in this module). Windows has had it for decades as **I/O completion ports (IOCP)**.

## The models side by side

| Model | Phase 1 (wait) | Phase 2 (copy) |
|---|---|---|
| Blocking | Blocks | Blocks |
| Non-blocking | Returns EAGAIN | Blocks |
| Multiplexing | Blocks in select | Blocks |
| Signal-driven | Signal arrives | Blocks |
| Asynchronous interface | Separate submission/completion | Implementation completes it |

Stevens' crucial observation: POSIX defines a **synchronous** I/O operation as one that blocks the requesting process until the operation completes. By that definition, the first four models are all synchronous, because the calling thread cannot use the returned result until the read finishes. Here synchronous does not mean the scheduler necessarily puts that thread to sleep during copying. Model 5 instead separates submission and completion.

## Readiness versus completion

That table boils down to two families:

- **Readiness-based** (models 2 to 4, and epoll and kqueue socket-readiness filters): the kernel says *when you can* do I/O without blocking. You then do it.
- **Completion-based** (model 5, IOCP, io_uring): you say *what* I/O to do. The kernel does it and tells you when it's *finished*.

The difference shapes everything above it:

| | Readiness | Completion |
|---|---|---|
| Buffer needed | At read time | At submit time |
| Ordinary regular files on Linux | Readiness is not storage completion | Supported operations can report completion |
| Syscall costs | Waits can cover many reads | Submission/completion can batch |
| Pattern | Reactor | Proactor |

With completion I/O you must hand over a buffer up front and keep it alive until the kernel finishes, which complicates memory management with 10,000 idle connections (io_uring's answer is provided buffer rings). With readiness I/O you can allocate the buffer only when data is actually there.

## Key takeaways
- A completion interface separates requesting work from collecting its result.
- Completion semantics do not imply a thread-free implementation.
- Submitted buffers need an appropriate lifetime.

## Further reading
- [read(2) — Linux manual page](https://man7.org/linux/man-pages/man2/read.2.html)
- [fcntl(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fcntl.2.html)
- [aio(7) — POSIX asynchronous I/O overview](https://man7.org/linux/man-pages/man7/aio.7.html)
- [Asynchronous I/O — Wikipedia](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
