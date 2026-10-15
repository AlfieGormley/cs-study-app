---
id: sched-thread-kernel-mappings
title: Mapping user threads onto kernel tasks
level: basic
minutes: 4
sourceLesson: sched-threads
summary: N:1 cannot execute user threads on several cores and a blocking syscall can stop the whole runtime.
---

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
## 1:1 (one-to-one)

Each thread you create is a kernel thread. Simple, uses all cores, and blocking calls behave as expected. The costs are a system call per creation and a kernel-sized footprint per thread.

**Linux uses 1:1.** Since glibc 2.3.2 and Linux 2.6 (around 2003), pthreads are provided by **NPTL** (Native POSIX Thread Library), and every `pthread_create` makes a kernel task. Windows and modern macOS are also 1:1.
## N:1 (many-to-one)

All user threads are multiplexed onto one kernel thread. Switching is very fast, but:

- the process can never use more than one core;
- if any user thread makes a blocking system call (say a `read` on a socket), the single kernel thread blocks and every user thread stops.

Early Java on Solaris ("green threads") worked this way. The model has largely died out for general-purpose threads.
## M:N (many-to-many)

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

## Key takeaways
- N:1 cannot execute user threads on several cores and a blocking syscall can stop the whole runtime.
- Linux pthreads use 1:1 mappings; runtimes can instead multiplex user threads over kernel threads.
- Linux getpid identifies the thread group, while gettid identifies the calling kernel task.

## Further reading
- [Concurrency: An Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
- [pthreads(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [clone(2) — Linux manual page](https://man7.org/linux/man-pages/man2/clone.2.html)
- [Native POSIX Thread Library — Wikipedia](https://en.wikipedia.org/wiki/Native_POSIX_Thread_Library)
- [Green thread — Wikipedia](https://en.wikipedia.org/wiki/Green_thread)
- [JEP 444: Virtual Threads — OpenJDK](https://openjdk.org/jeps/444)
