---
id: proc-switch-user-threads
sourceLesson: proc-context-switching
title: "User-level threads and blocking calls"
level: advanced
minutes: 2
summary: "M:N runtimes multiplex user threads onto kernel threads."
---

M:N runtimes multiplex user threads onto kernel threads. This lesson focuses on user-level threads and blocking calls.

## Preview: user threads versus kernel threads

Everything so far concerns tasks the *kernel* knows about. Threads can also be managed in user space.

| Model | Mapping | Example |
|---|---|---|
| 1:1 | each thread is a kernel task | Linux pthreads (NPTL), Java platform threads |
| N:1 | N user threads, one kernel task | early "green threads" |
| M:N | M user threads over a pool of N kernel threads | Go goroutines, Java virtual threads |

In these names the first number counts user threads and the second counts kernel threads. M is usually much larger than N: a Go program can run 100,000 goroutines on a handful of kernel threads.

A **user-level switch** saves a few registers and swaps stacks in a library function, with no kernel entry and no page-table change, avoiding kernel-scheduler work on that code path; the runtime and workload determine its cost. The catch: if a user thread makes a blocking syscall, the kernel thread under it blocks too, so M:N runtimes may use nonblocking I/O, park user threads or move runnable work to other OS threads around blocking calls. Threads, and how the scheduler chooses who runs next, are the subject of the next module.

## Key takeaways
- M:N runtimes multiplex user threads onto kernel threads.
- A user-level switch can avoid kernel scheduling, but blocking calls still affect the underlying kernel task.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Context switch — Wikipedia](https://en.wikipedia.org/wiki/Context_switch)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Page Table Isolation (PTI) — Linux kernel docs](https://docs.kernel.org/arch/x86/pti.html)
- [proc(5): /proc/pid/status — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Thread (computing) — Wikipedia](https://en.wikipedia.org/wiki/Thread_(computing))
