---
id: dl-fundamentals-dependencies
title: Deadlocks beyond ordinary locks
level: basic
minutes: 2
sourceLesson: dl-fundamentals
summary: Joins, bounded queues, nested pool submissions and pipes can form dependency cycles.
---

## Deadlock beyond mutexes

Anything a thread can wait on can be part of a deadlock cycle, not just mutexes.

- **Self-deadlock.** A thread takes a non-reentrant lock it already holds. A second blocking acquisition of a held `threading.Lock` waits; if no other thread releases it, this is self-deadlock. `threading.RLock` supports same-thread re-entry.
- **Joining.** Thread A calls `b.join()` while holding a lock that B needs before it can exit.
- **Bounded queues.** Producer P blocks on a full queue Q1 while consumer C blocks putting a reply onto full queue Q2 that P is supposed to drain.
- **Thread pools.** A task running on a pool of size 4 submits a sub-task to the same pool and waits for its result. If all 4 workers do this at once, no worker is free to run any sub-task. This is a classic in Java `ExecutorService` and Python `concurrent.futures` code.
- **Processes and pipes.** A parent writes a large input to a child's stdin and only then reads its stdout. The child fills its stdout pipe buffer (capacity depends on page size, limits and configuration) and blocks writing; the parent blocks writing because the child stopped reading. Python's `subprocess` docs warn about exactly this and recommend `communicate()`.

## Key takeaways
- Joins, bounded queues, nested pool submissions and pipes can form dependency cycles.
- A pool task waiting for work queued to the same exhausted pool cannot progress.
- Drain child output while supplying input; communicate() handles the pipe interaction.

## Further reading
- [Python: executor deadlock examples](https://docs.python.org/3/library/concurrent.futures.html)
- [Python: subprocess pipe interactions](https://docs.python.org/3/library/subprocess.html)
- [Python: primitive and re-entrant locks](https://docs.python.org/3/library/threading.html)
