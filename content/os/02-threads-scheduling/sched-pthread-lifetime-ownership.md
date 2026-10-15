---
id: sched-pthread-lifetime-ownership
title: Join, detach and preserve argument lifetimes
level: basic
minutes: 2
sourceLesson: sched-thread-apis
summary: Join or detach every successfully created joinable thread.
---

## Join, detach, or leak

A finished joinable thread retains resources and a result for a later join. Its automatic local objects have already ended their lifetimes; retained or cached stack storage does not keep those objects alive:

- **Joinable** (the default): another thread must call `pthread_join`. If nobody ever does, the finished thread's resources are never freed. It is the thread equivalent of a zombie process.
- **Detached**: call `pthread_detach(tid)` (or create it with the `PTHREAD_CREATE_DETACHED` attribute). Its resources are freed as soon as it exits. You can no longer join it or get its result.

Use join when you need the result or need to know the work is done. Use detach for fire-and-forget background threads.

> [!warning] Returning from `main` kills every thread
> Returning from `main` calls `exit()`, which ends the whole process, including threads still running. Join your threads first, or end `main` with `pthread_exit(NULL)`, which ends only the main thread and lets the others carry on.
## The bugs everyone writes first

**Passing the loop variable's address:**

```c
/* Bug: every worker gets the same &i. */
for (int i = 0; i < 4; i++)
    pthread_create(&t[i], NULL, f, &i);
```

All four threads get a pointer to the *same* `i`. Concurrent unsynchronized reads and writes constitute a C data race (undefined behavior), and use after the loop can also exceed its lifetime. Duplicates or `4` are possible symptoms, not guaranteed outcomes. Give each thread its own argument: an array element, a `malloc`'d struct, or a platform-supported value-through-pointer convention (not a universally portable integer transport).

**Returning a pointer to a local.** A thread that returns `&result`, where `result` is a local variable, hands back a pointer to an object whose lifetime has ended, regardless of whether its stack storage is physically reclaimed yet. Return a heap pointer or write into memory the caller owns.

**Assuming an order.** Thread creation order says nothing about execution order. Threads started 1, 2, 3 may run, print and finish in any order.

## Key takeaways
- Join or detach every successfully created joinable thread.
- Returning from main ends the whole process; detaching does not extend its lifetime.
- Each worker needs a stable argument and a result object that outlives its use.

## Further reading
- [pthread_create(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_create.3.html)
- [pthread_detach(3) — Linux manual page](https://man7.org/linux/man-pages/man3/pthread_detach.3.html)
- [Interlude: Thread API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-api.pdf)
- [concurrent.futures — Python docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Python support for free threading — Python docs](https://docs.python.org/3/howto/free-threading-python.html)
- [PEP 703: Making the GIL optional in CPython](https://peps.python.org/pep-0703/)
