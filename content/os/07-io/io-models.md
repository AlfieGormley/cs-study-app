---
id: io-models
title: The five I/O models
level: intermediate
minutes: 12
summary: Blocking, non-blocking, multiplexed, signal-driven and asynchronous I/O as Stevens classified them, readiness versus completion, and what "async" actually means.
---

When a program asks to read from a socket, the data may not have arrived yet. What should happen? The program could wait, could be told "try again", could ask to be notified, or could ask the kernel to finish the whole job in the background.

W. Richard Stevens, in *Unix Network Programming*, sorted the options into **five I/O models**. They are still the clearest way to think about every server framework you will meet, from Apache to Node.js to io_uring.

## A two-phase model of ordinary socket input

For an ordinary buffered socket read, use this simplified two-phase model:

1. **Wait for the data to be ready.** For a socket, a packet must arrive and land in the kernel's receive buffer.
2. **Copy the data from kernel to user space.** The kernel copies bytes from its buffer into the buffer you passed to `read()` or `recv()`.

Phase 1 can take forever (a client that never sends). Phase 2 involves copying with a cost dependent on size, memory state and implementation; it has no fixed microsecond duration. The five models differ in how the process experiences each phase.

```
   app             kernel
    |   read()  -->  | no data yet
    |                |   ... wait ...  (1)
    |                | data arrives
    |                | copy to user    (2)
    |  <-- n bytes   |
```

## 1. Blocking I/O

For a blocking stream socket, a positive-length `read()` can wait for data, EOF or an error. Available data may return immediately, possibly as a short read; copying is completed before the call returns.

```c
char buf[4096];
ssize_t n = read(fd, buf, sizeof buf);
/* n > 0: got n bytes
   n == 0: peer closed (EOF)
   n < 0: error, see errno */
```

Blocking I/O is simple and efficient for one stream: the thread uses no CPU while asleep. The trouble starts with many streams. A thread blocked on client A cannot notice that client B has sent something.

The classic answer is **one thread (or process) per connection**, as in Apache's prefork and worker models. Its costs depend on the workload and resource limits:

- Each thread needs a stack (size determined by thread attributes and runtime limits, not a universal Linux 8 MB default; reserved address space differs from resident memory) and a kernel task structure.
- Runnable threads and wakeups add scheduler work; idle sleeping threads mainly consume memory and bookkeeping resources.
- Most of those threads are just asleep, waiting for slow clients.

## 2. Non-blocking I/O

Set `O_NONBLOCK` on the descriptor and `read()` never sleeps in phase 1. For supported socket operations with no available data, EOF or other result, it reports `EAGAIN` or `EWOULDBLOCK`. Portable code checks both; these constants need not be equal on every platform.

```c
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

The Python equivalent raises `BlockingIOError`:

```python
import socket

s = socket.create_connection(
    ("example.com", 80))
s.setblocking(False)
try:
    data = s.recv(4096)
except BlockingIOError:
    data = None   # EAGAIN: try later
```

A naive use of non-blocking I/O can lead to **busy-polling**: loop over every socket calling `read()`, getting `EAGAIN` from almost all of them, burning CPU. Its real value is as a building block for model 3.

Note that phase 2 is still synchronous. When data *is* ready, `read()` copies it before returning.

> [!warning] O_NONBLOCK does nothing for regular files
> On Linux, `O_NONBLOCK` is ignored for regular files and block devices. A `read()` that misses the page cache blocks for the disk regardless. select and poll always report regular files as ready, and epoll refuses them outright with `EPERM`. This is why Node.js runs file operations on a thread pool (lesson 5).

## 3. I/O multiplexing

Instead of blocking in `read()` on one descriptor, block in a call that watches **many** descriptors and returns when any is ready: `select`, `poll`, `epoll` on Linux, `kqueue` on BSD and macOS.

```
select/epoll_wait  --> blocks (phase 1)
   returns "fd 7 is readable"
read(7)            --> copies (phase 2)
```

One thread can now serve tens of thousands of connections. This is the foundation of nginx, Redis, Node.js and Python's `asyncio`. The next lesson covers these calls in detail.

Multiplexing tells you about **readiness**: "a read on fd 7 will not block now". You still do the I/O yourself. Descriptors are normally also set non-blocking, because readiness can become stale or be spurious. An ordinary stream read need not wait to fill its buffer, but flags such as MSG_WAITALL and concurrent readers require care.

## 4. Signal-driven I/O

Ask the kernel to send a `SIGIO` signal when a descriptor becomes ready:

```c
signal(SIGIO, on_sigio);
fcntl(fd, F_SETOWN, getpid());
int fl = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, fl | O_ASYNC);
```

The process carries on running; the signal handler (or a main loop it nudges) then calls `read()`. Phase 1 doesn't block; phase 2 still does.

Standard SIGIO notifications can coalesce, so programs must re-check descriptor state rather than count signals as events. Signal handlers have async-signal-safety restrictions. Linux `F_SETSIG` with `SA_SIGINFO` can include descriptor/event information, and real-time signals can queue subject to resource limits; fallback to SIGIO is possible. Multiplexing often makes per-descriptor event handling easier.

## 5. Asynchronous I/O

Request "read into this buffer and report when it is **done**". A completion interface separates submission from collecting the result. The operation may finish before submission returns or later, and the implementation may use kernel machinery or helper threads. Submission itself still has cost and possible errors.

POSIX defines `aio_read` for this:

```c
struct aiocb cb = {0};
cb.aio_fildes = fd;
cb.aio_buf    = buf;
cb.aio_nbytes = sizeof buf;
cb.aio_offset = 0;
cb.aio_sigevent.sigev_notify = SIGEV_NONE;

if (aio_read(&cb) == -1) {
    perror("aio_read"); exit(1);
}
do_other_work();
while (aio_error(&cb) == EINPROGRESS)
    ;                  /* or aio_suspend */
int status = aio_error(&cb);
ssize_t n = aio_return(&cb);
/* status: completion error, or 0. */
```

The catch on Linux: glibc's POSIX AIO is implemented in user space with a pool of threads doing ordinary blocking calls. Linux native AIO (`io_submit`) has operation/filesystem limitations, and submission can block even with direct I/O in some paths. **io_uring**, introduced in Linux 5.1 in 2019, provides a broader completion interface; it can also use worker threads and has operation-specific support rules (lesson 4). Windows has had it for decades as **I/O completion ports (IOCP)**.

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

- **Readiness-based** (models 2 to 4, and epoll and kqueue): the kernel says *when you can* do I/O without blocking. You then do it.
- **Completion-based** (model 5, IOCP, io_uring): you say *what* I/O to do. The kernel does it and tells you when it's *finished*.

The difference shapes everything above it:

| | Readiness | Completion |
|---|---|---|
| Buffer needed | At read time | At submit time |
| Ordinary regular files on Linux | Readiness is not storage completion | Supported operations can report completion |
| Syscall costs | Waits can cover many reads | Submission/completion can batch |
| Pattern | Reactor | Proactor |

With completion I/O you must hand over a buffer up front and keep it alive until the kernel finishes, which complicates memory management with 10,000 idle connections (io_uring's answer is provided buffer rings). With readiness I/O you can allocate the buffer only when data is actually there.

## What "async" really means

The word "async" is used for at least three different things:

1. **Asynchronous I/O interface**: completion is reported separately from submission; helper threads or kernel facilities may do the work (model 5).
2. **Non-blocking**: a call returns immediately rather than sleeping (model 2). Non-blocking is not the same as asynchronous; a non-blocking `read()` that finds data does the copy synchronously.
3. **async/await in a language**: a programming style where a function can pause at `await` and let an event loop run other tasks. On Unix, default selector-based asyncio and libuv commonly use readiness APIs for sockets, with worker mechanisms for some blocking work. Windows uses different backends: Python's default ProactorEventLoop and libuv use IOCP. Runtime version and event-loop choice matter.

For Node.js on a typical Unix libuv backend, asynchronous JavaScript APIs can sit above non-blocking socket readiness and worker-based file operations. That does not make every operation universally non-blocking or every platform use epoll; synchronous APIs and CPU-heavy callbacks can still block the event loop.

> [!tip] The question to ask
> Whenever a framework claims to be "asynchronous", ask: who is waiting, and where? Is a thread sleeping in `epoll_wait`, in a worker pool, or nowhere at all because the kernel is doing the work? The answer tells you how it will scale and where it can stall.

## Choosing a model

- **A few connections, simple code**: blocking I/O, possibly a thread per connection. Easy to reason about.
- **Thousands of mostly idle connections**: multiplexing with non-blocking sockets, in an event loop.
- **Linux workloads needing completion interfaces or batching**: evaluate supported io_uring operations against a measured baseline.
- **Implementation matters**: glibc POSIX AIO has asynchronous completion semantics even though workers perform the I/O; signal-driven designs require careful state and signal handling.

## Key takeaways
- The two-phase socket-read model separates waiting for readiness from copying; it is a teaching model, not every possible I/O path.
- In the first four models, the caller performs a read and receives its result when that call finishes. Completion interfaces separate submission from result collection.
- Readiness models (epoll, kqueue) tell you when you can act; completion models (IOCP, io_uring) tell you when the kernel has acted.
- `O_NONBLOCK` has no effect on regular files, which is why event loops use thread pools for disk I/O.
- Language async/await does not specify the underlying I/O mechanism; runtime, platform and operation determine readiness, completion or worker-based behavior.

> [!note] Deployment evidence gap
> No benchmark establishes connection-count limits, universal stack residency, copy latency or a fastest I/O model here. Numeric scenarios are assumptions; exact costs and runtime backends must be checked for the deployed version. C examples are fragments requiring headers, initialized descriptors/buffers and lifecycle cleanup. Keep asynchronous buffers/control blocks valid until completion.

## Further reading
- [read(2) — Linux manual page](https://man7.org/linux/man-pages/man2/read.2.html)
- [fcntl(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fcntl.2.html)
- [aio(7) — POSIX asynchronous I/O overview](https://man7.org/linux/man-pages/man7/aio.7.html)
- [Asynchronous I/O — Wikipedia](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
