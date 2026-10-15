---
id: io-blocking-read-phases
title: Blocking reads and connection threads
level: intermediate
minutes: 3
summary: Separate waiting for readiness from copying the result.
sourceLesson: io-models
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
/* Returns bytes, EOF or an error. */
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

## Key takeaways
- Separate waiting for readiness from copying the result.
- Blocking threads sleep rather than consume CPU, but still need stack and task resources.

## Further reading
- [read(2) — Linux manual page](https://man7.org/linux/man-pages/man2/read.2.html)
- [fcntl(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fcntl.2.html)
- [aio(7) — POSIX asynchronous I/O overview](https://man7.org/linux/man-pages/man7/aio.7.html)
- [Asynchronous I/O — Wikipedia](https://en.wikipedia.org/wiki/Asynchronous_I/O)
- [Ringing in a new asynchronous I/O API — LWN.net](https://lwn.net/Articles/776703/)
