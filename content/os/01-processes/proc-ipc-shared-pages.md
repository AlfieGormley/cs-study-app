---
id: proc-ipc-shared-pages
sourceLesson: proc-ipc
title: "Sharing pages and publishing data"
level: advanced
minutes: 3
summary: "Shared mappings avoid conventional channel payload copies."
---

Shared mappings avoid conventional channel payload copies. This lesson focuses on sharing pages and publishing data.

## Shared memory: avoiding payload copies

Conventional pipe and socket read/write transfers normally copy payload from the sender into a kernel buffer and then into the receiver. Zero-copy APIs and shared-buffer descriptor passing can change that path. **Shared memory** maps the *same physical pages* into both processes' address spaces. After setup, payload can be accessed with loads and stores without copying it through a kernel channel. Synchronisation, notification, cache coherence and page faults still have costs.

```c
/* creator initialises; peers attach */
int fd = shm_open("/stats",
                  O_CREAT | O_RDWR, 0600);
/* Size the object before mapping its */
/* pages. */
ftruncate(fd, 4096);
long *p = mmap(NULL, 4096,
               PROT_READ | PROT_WRITE,
               MAP_SHARED, fd, 0);
p[0] = 42; /* publish with proper sync */
```

On Linux, POSIX shared memory objects live in the `tmpfs` at `/dev/shm`. You can also share memory by `mmap`ing an ordinary file with `MAP_SHARED`, or by creating an anonymous `MAP_SHARED` mapping before `fork`.

The speed comes with responsibility:

- **No synchronisation is provided.** Two processes doing `p[0]++` can lose updates, exactly like two threads. Use a process-shared mutex or semaphore. Atomics require a platform/implementation that supports the chosen atomic representation across processes; non-lock-free atomics may use unsuitable process-local locks.
- **No notification.** The reader doesn't know new data has arrived. You need a semaphore, a futex, or a separate pipe or socket to say "look now".
- **Pointers don't travel.** The region may be mapped at different virtual addresses in each process, so store validated offsets or another relocatable representation rather than assuming raw pointers are usable.
- **Names outlive processes.** An object stays in `/dev/shm` until `shm_unlink` or reboot. A crashed process can leak it.

PostgreSQL is a classic user: each client connection is a separate backend process, and they all share the buffer cache and lock tables in shared memory. Chromium and many audio and video pipelines use shared memory to move large buffers between processes.

## Key takeaways
- Shared mappings avoid conventional channel payload copies.
- Processes still need synchronisation, notification and relocatable data representations.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
