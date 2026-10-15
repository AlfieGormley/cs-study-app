---
id: sched-thread-shared-private
title: What threads share and keep private
level: basic
minutes: 4
sourceLesson: sched-threads
summary: Threads have their own execution state while sharing the process address space and resources.
---

A **process** is a running program with its own address space, open files and other resources. A **thread** is a single sequence of execution *inside* a process: its own program counter, registers and stack, running through the process's code.

Every process starts with one thread. A **multithreaded** process has several, all running the same program and all seeing the same memory.

A useful picture: the process is a kitchen (ingredients, utensils, ovens), and threads are cooks. Adding cooks lets several dishes progress at once, but they share the fridge, so they can get in each other's way.
## Why bother with threads?

You could get concurrency from several processes instead. Threads exist because they make some things much easier or cheaper:

- **Parallelism.** A machine with 16 cores can run 16 threads of one program at the same instant. A single application thread cannot itself execute on several cores simultaneously; libraries or the kernel may do work on its behalf.
- **Overlapping waiting with work.** While one thread blocks on a disk read or network reply, another can keep computing or serve another user.
- **Responsiveness.** A GUI keeps a thread free to handle input while a worker thread does the slow job.
- **Cheap sharing.** Threads communicate by reading and writing the same memory. Processes need pipes, sockets or explicitly shared memory.
- **Cheaper to create and switch.** A new thread does not need a new address space. Sharing an address space can avoid changing memory maps and preserve useful translations. Cache residency and measured switch cost still depend on hardware and workload.

The price of cheap sharing is that **nothing stops two threads touching the same data at the same time**. That is the subject of the next module (synchronisation). For now, just remember that shared data needs a lock or similar protection.
## Shared versus private state

This table is the heart of the lesson. If you know which column something is in, you can predict most multithreading bugs.

| Shared by all threads | Private to each thread |
|---|---|
| Code (text segment) | Program counter |
| Global and static variables | Registers |
| Heap (`malloc`, Python objects) | Stack (locals, return addresses) |
| Open file descriptors | Thread ID |
| Current directory, user ID | Signal mask |
| Signal handlers, PID | Scheduling priority, `errno`, thread-local storage |

In memory it looks like this. Each thread gets its own stack somewhere in the shared address space:

```
high  +------------------------+
      | stack: main thread     |
      +------------------------+
      | stack: thread 2        |
      +------------------------+
      | stack: thread 3        |
      +------------------------+
      |          ...           |
      | heap (shared)          |
      +------------------------+
      | globals / static       |
      +------------------------+
low   | code                   |
      +------------------------+
```

Note that "private" stacks are private by convention, not by hardware. All threads share one address space, so a thread that is handed a pointer to another thread's local variable can read and corrupt it. Nothing is truly walled off.

A small C example makes the split concrete:

```c
#include <pthread.h>
#include <stdio.h>

int hits = 0;      /* global: shared */

void *work(void *arg) {
    int mine = 0;  /* on this stack */
    mine++;
    /* Unsafe update of a shared counter. */
    hits++;        /* C data race */
    printf("mine=%d\n", mine);
    return NULL;
}
```

Each call has its own `mine`, but the unsynchronised accesses to shared `hits` create a C data race and therefore undefined behaviour: this program has no guaranteed output. The read/add/write lost-update model illustrates one possible failure, not the full language semantics. Use an atomic counter or lock before relying on the output. The question uses C11 atomic_fetch_add for the shared counter: that indivisible update removes this race, while each call still has its own local mine value. Three completed calls then each print mine=1 and leave the atomic counter at 3.

> [!warning] One thread's crash is everyone's crash
> Threads share fate. A signal with a terminating disposition (such as ordinary default-action SIGSEGV), or a call to exit(), terminates the whole process. Not every uncaught signal has a terminating default action. Processes isolate failures; threads do not.

## Key takeaways
- Threads have their own execution state while sharing the process address space and resources.
- A pointer can expose one thread’s stack to another; “private stack” is not a memory-protection boundary.
- A C data race makes the program undefined; an atomic increment or lock is needed for a reliable shared counter.

## Further reading
- [Concurrency: An Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [pthreads(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [clone(2) — Linux manual page](https://man7.org/linux/man-pages/man2/clone.2.html)
- [Native POSIX Thread Library — Wikipedia](https://en.wikipedia.org/wiki/Native_POSIX_Thread_Library)
- [Green thread — Wikipedia](https://en.wikipedia.org/wiki/Green_thread)
- [JEP 444: Virtual Threads — OpenJDK](https://openjdk.org/jeps/444)
