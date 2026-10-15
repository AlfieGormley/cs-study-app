---
id: sched-thread-lightweight-limits
title: Lightweight runtimes and thread resource limits
level: basic
minutes: 3
sourceLesson: sched-threads
summary: Goroutines and virtual threads share carrier threads; their counts do not determine an exact OS-thread count.
---

## Green threads return: goroutines and virtual threads

M:N came back, not in the OS but in language runtimes, where the runtime controls the whole stack and can avoid the classic pitfalls.

**Go's goroutines** are the best-known example:

- A goroutine starts with a small stack that grows as needed. The Go 1.25 source sets the minimum Go stack to 2048 bytes; platform overhead and allocation rounding can raise the actual initial allocation. Large goroutine counts remain limited by memory and workload.
- The runtime runs them on a small set of OS threads. `GOMAXPROCS` limits simultaneous Go execution. Go 1.25 introduced defaults that also consider container CPU limits; explicit settings and compatibility controls can override that policy.
- When a goroutine does network I/O, the runtime parks it and uses non-blocking sockets plus `epoll` behind the scenes, so the OS thread is free for other goroutines. For genuinely blocking system calls, the runtime hands the thread's work to another thread.
- Since Go 1.14, the runtime can **preempt** a goroutine stuck in a tight loop, improving responsiveness for ordinary tight loops; this is not an unconditional scheduling-latency guarantee.

**Java virtual threads** (final in JDK 21) do the same for Java: lightweight threads mounted on carrier OS threads; achievable counts and carrier behavior depend on memory, runtime version and workload. Erlang's lightweight processes are an older example of the same idea.

> [!tip] Why not just make OS threads cheaper?
> An OS thread needs a kernel stack, a `task_struct` and a user stack. For Linux NPTL, a finite RLIMIT_STACK soft limit at program start determines the default new-thread stack size; 8 MiB is one common configuration, not a universal default. Reserving stack address space does not mean every page is resident in RAM. The feasible thread count depends on resource limits, stack configuration and workload. A goroutine's few KB scale much further.
## Pitfalls to remember

- **Shared by default.** Globals and heap objects are visible to every thread. Accidental sharing is the most common source of bugs.
- **More threads is not more speed.** For CPU-bound work, start from available logical CPUs and measure; SMT, quotas, memory bandwidth and serial work affect the useful concurrency.
- **`fork()` in a threaded program** copies only the calling thread. Any lock another thread held is copied in its locked state, with no thread left to unlock it. After `fork()` in a multithreaded process, call only async-signal-safe functions until `exec()`.
- **Thread IDs are not process IDs.** Tools like `top` (press `H`) or `htop` can show per-thread CPU use, which is often where the hot spot hides.

> [!note] Content gap: thread capacity and timing
> No reproducible benchmark supports universal thread creation/switch timings, maximum thread counts or a fixed Go OS-thread count. These figures are omitted; limits and costs depend on runtime, platform and workload.

## Key takeaways
- Goroutines and virtual threads share carrier threads; their counts do not determine an exact OS-thread count.
- Reserved stack address space differs from physical memory committed to touched pages.
- After fork in a multithreaded child, use only async-signal-safe operations until exec.

## Further reading
- [Concurrency: An Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [pthreads(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [clone(2) — Linux manual page](https://man7.org/linux/man-pages/man2/clone.2.html)
- [Native POSIX Thread Library — Wikipedia](https://en.wikipedia.org/wiki/Native_POSIX_Thread_Library)
- [Green thread — Wikipedia](https://en.wikipedia.org/wiki/Green_thread)
- [JEP 444: Virtual Threads — OpenJDK](https://openjdk.org/jeps/444)
- [Go 1.25 runtime stack implementation](https://raw.githubusercontent.com/golang/go/go1.25.0/src/runtime/stack.go)
- [Container-aware GOMAXPROCS — Go team](https://go.dev/blog/container-aware-gomaxprocs)
