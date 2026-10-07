---
id: sched-threads
title: Threads
level: basic
minutes: 11
summary: Why threads exist, what they share and what they keep private, kernel versus user threads, the 1:1, N:1 and M:N models, and how goroutines fit in.
---

A **process** is a running program with its own address space, open files and other resources. A **thread** is a single sequence of execution *inside* a process: its own program counter, registers and stack, running through the process's code.

Every process starts with one thread. A **multithreaded** process has several, all running the same program and all seeing the same memory.

A useful picture: the process is a kitchen (ingredients, utensils, ovens), and threads are cooks. Adding cooks lets several dishes progress at once, but they share the fridge, so they can get in each other's way.

## Why bother with threads?

You could get concurrency from several processes instead. Threads exist because they make some things much easier or cheaper:

- **Parallelism.** A machine with 16 cores can run 16 threads of one program at the same instant. A single-threaded program uses one core, however many you have.
- **Overlapping waiting with work.** While one thread blocks on a disk read or network reply, another can keep computing or serve another user.
- **Responsiveness.** A GUI keeps a thread free to handle input while a worker thread does the slow job.
- **Cheap sharing.** Threads communicate by reading and writing the same memory. Processes need pipes, sockets or explicitly shared memory.
- **Cheaper to create and switch.** A new thread does not need a new address space. Switching between two threads of the same process keeps the page tables, so the TLB's cached translations stay valid.

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
    hits++;        /* shared: racy */
    printf("mine=%d\n", mine);
    return NULL;
}
```

Each call has its own `mine`, but the unsynchronised accesses to shared `hits` create a C data race and therefore undefined behaviour: this program has no guaranteed output. The read/add/write lost-update model illustrates one possible failure, not the full language semantics. Use an atomic counter or lock before relying on the output.

> [!warning] One thread's crash is everyone's crash
> Threads share fate. A signal with a terminating disposition (such as ordinary default-action SIGSEGV), or a call to exit(), terminates the whole process. Not every uncaught signal has a terminating default action. Processes isolate failures; threads do not.

## Kernel threads and user threads

There are two places a thread can be implemented.

**Kernel threads** are known to the OS. The kernel schedules each one independently, so they can run on different cores, and one blocking in a system call does not stop the others.

**User threads** (also called user-level or green threads) are managed by a library or language runtime inside the process. The kernel sees only the process (or a few kernel threads). The runtime switches between user threads itself, by saving and restoring registers, without a system call.

| | Kernel threads | User threads |
|---|---|---|
| Create / switch | OS-managed work | Runtime-managed work |
| Use many cores | Yes | Only via kernel threads |
| Blocking syscall | Blocks one thread | May block all |
| Scheduling | OS policy | Runtime's policy |

## Threading models: 1:1, N:1 and M:N

The models describe how user-visible threads map onto kernel threads.

```
1:1         N:1          M:N
U U U       U U U U      U U U U U
| | |        \ | | /      \ |/ \|/
K K K          K           K    K
```

### 1:1 (one-to-one)

Each thread you create is a kernel thread. Simple, uses all cores, and blocking calls behave as expected. The costs are a system call per creation and a kernel-sized footprint per thread.

**Linux uses 1:1.** Since glibc 2.3.2 and Linux 2.6 (around 2003), pthreads are provided by **NPTL** (Native POSIX Thread Library), and every `pthread_create` makes a kernel task. Windows and modern macOS are also 1:1.

### N:1 (many-to-one)

All user threads are multiplexed onto one kernel thread. Switching is very fast, but:

- the process can never use more than one core;
- if any user thread makes a blocking system call (say a `read` on a socket), the single kernel thread blocks and every user thread stops.

Early Java on Solaris ("green threads") worked this way. The model has largely died out for general-purpose threads.

### M:N (many-to-many)

M user threads run on N kernel threads, with N usually around the number of cores. It promises the best of both: cheap threads and real parallelism. It is also the hardest to build, because two schedulers (the runtime's and the kernel's) must cooperate, and blocking calls need special handling.

Solaris used M:N before Solaris 9 and then switched to 1:1. Linux had a competing M:N project (NGPT) that lost to NPTL. For OS-level threads, 1:1 won because the kernel made kernel threads cheap enough.

## How Linux actually does it

To the Linux kernel there is no separate "thread" object. Both processes and threads are **tasks** (`struct task_struct`), created by the `clone()` system call. The flags decide what is shared:

```
fork():   private address space
          (memory copied on write)

thread:   clone(CLONE_VM | CLONE_FS |
                CLONE_FILES |
                CLONE_SIGHAND |
                CLONE_THREAD | ...)
```

`CLONE_VM` shares the address space, `CLONE_FILES` shares the file descriptor table and `CLONE_THREAD` puts the new task in the same **thread group**. What user space calls the PID is really the thread group ID (TGID). Each thread has its own ID, which `gettid()` returns.

You can see this from the shell:

```
$ ps -eLf | head -3     # -L shows threads
$ ls /proc/1234/task/   # one dir per thread
```

Because each thread is a separate task, the Linux scheduler schedules threads, not processes. A process with 8 runnable threads competes as 8 tasks (unless cgroups group them, as later lessons show).

## Green threads return: goroutines and virtual threads

M:N came back, not in the OS but in language runtimes, where the runtime controls the whole stack and can avoid the classic pitfalls.

**Go's goroutines** are the best-known example:

- A goroutine starts with a small stack (a few KB, currently 2 KB) that grows as needed, so a program can run hundreds of thousands or millions of them.
- The runtime runs them on a small set of OS threads. `GOMAXPROCS` limits simultaneous Go execution. Go 1.25 introduced defaults that also consider container CPU limits; explicit settings and compatibility controls can override that policy.
- When a goroutine does network I/O, the runtime parks it and uses non-blocking sockets plus `epoll` behind the scenes, so the OS thread is free for other goroutines. For genuinely blocking system calls, the runtime hands the thread's work to another thread.
- Since Go 1.14, the runtime can **preempt** a goroutine stuck in a tight loop, improving responsiveness for ordinary tight loops; this is not an unconditional scheduling-latency guarantee.

**Java virtual threads** (final in JDK 21) do the same for Java: lightweight threads mounted on carrier OS threads; achievable counts and carrier behavior depend on memory, runtime version and workload. Erlang's lightweight processes are an older example of the same idea.

> [!tip] Why not just make OS threads cheaper?
> An OS thread needs a kernel stack, a `task_struct` and a user stack. On Linux the default user stack is typically 8 MB of reserved virtual memory (from `ulimit -s`), though only touched pages use real RAM. The feasible thread count depends on resource limits, stack configuration and workload. A goroutine's few KB scale much further.

## Pitfalls to remember

- **Shared by default.** Globals and heap objects are visible to every thread. Accidental sharing is the most common source of bugs.
- **More threads is not more speed.** For CPU-bound work, start from available logical CPUs and measure; SMT, quotas, memory bandwidth and serial work affect the useful concurrency.
- **`fork()` in a threaded program** copies only the calling thread. Any lock another thread held is copied in its locked state, with no thread left to unlock it. After `fork()` in a multithreaded process, call only async-signal-safe functions until `exec()`.
- **Thread IDs are not process IDs.** Tools like `top` (press `H`) or `htop` can show per-thread CPU use, which is often where the hot spot hides.

> [!note] Content gap: thread capacity and timing
> No reproducible benchmark supports universal thread creation/switch timings, maximum thread counts or a fixed Go OS-thread count. These figures are omitted; limits and costs depend on runtime, platform and workload.

## Key takeaways
- A thread is an execution context (PC, registers, stack) inside a process; threads of a process share code, heap, globals and open files.
- Threads give parallelism and overlap I/O with computation cheaply, at the cost of shared-state bugs and shared fate on crashes.
- Kernel threads are scheduled by the OS and use many cores; user threads are switched by a runtime and are cheaper.
- Linux is 1:1 (NPTL): each pthread is a kernel task created with `clone()`, and the scheduler schedules threads.
- M:N lives on in language runtimes: Go's goroutines and Java's virtual threads multiplex many cheap threads onto a few OS threads.

## Further reading
- [Concurrency: An Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [pthreads(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [clone(2) — Linux manual page](https://man7.org/linux/man-pages/man2/clone.2.html)
- [Native POSIX Thread Library — Wikipedia](https://en.wikipedia.org/wiki/Native_POSIX_Thread_Library)
- [Green thread — Wikipedia](https://en.wikipedia.org/wiki/Green_thread)
- [JEP 444: Virtual Threads — OpenJDK](https://openjdk.org/jeps/444)
