---
id: sync-locks-futex-waiting
title: Sleep safely with futexes
level: intermediate
minutes: 3
summary: Explain the userspace fast path and the atomic compare-and-block that avoids a lost wakeup.
sourceLesson: sync-locks
---

When a lock holder may be descheduled, putting waiters to sleep usually avoids wasting their time slices. The difficult part is closing the gap between checking the lock and actually sleeping.

## Sleeping locks and the futex

For user programs the right answer to "lock is busy" is usually: **stop running and let the OS wake you when it is free**. That needs the kernel, because only the kernel can put a thread to sleep. Avoiding a kernel transition can reduce uncontended fast-path overhead; actual costs and contention rates are workload- and platform-dependent. You do not want a syscall when nobody else is waiting.

Linux solves this with the **futex** ("fast userspace mutex"). It has two halves:

1. A plain integer in user memory, manipulated with atomic instructions.
2. A syscall, `futex()`, with two key operations:
   - `FUTEX_WAIT(addr, val)`: "if `*addr` still equals `val`, put me to sleep". The check and the sleep are atomic with respect to wakers, which prevents a lost wakeup.
   - `FUTEX_WAKE(addr, n)`: "wake up to `n` threads sleeping on `addr`".

A mutex built on a futex uses three states: 0 = unlocked, 1 = locked with no waiters, 2 = locked and someone may be waiting. This is the design in Ulrich Drepper's paper *Futexes Are Tricky*:

```c
void lock(atomic_int *f) {
    int c = 0;
    if (atomic_compare_exchange_strong(
            f, &c, 1))
        return;            // fast path
    if (c != 2)
        // Record that sleeping may occur.
        c = atomic_exchange(f, 2);
    while (c != 0) {
        // Compare and block; retry on
        // return.
        futex_wait(f, 2);  // sleep
        // Record that sleeping may occur.
        c = atomic_exchange(f, 2);
    }
}

void unlock(atomic_int *f) {
    if (atomic_fetch_sub(f, 1) != 1) {
        // Publish freedom before waking.
        atomic_store(f, 0);
        futex_wake(f, 1);  // wake one
    }
}
```

(`futex_wait` and `futex_wake` are illustrative wrappers. A real Linux implementation needs a correctly aligned 32-bit futex word compatible with its atomic representation, the appropriate private/shared operation and handling for interruptions, spurious wakes and errors.)

The fast paths are the point. An uncontended `lock` is one CAS; an uncontended `unlock` is one atomic decrement. This teaching algorithm illustrates the fast-path principle. Ordinary glibc mutexes also use user-space atomic state plus futex slow paths, but exact instructions and control flow differ with mutex type, glibc version and optimizations. Windows (`SRWLOCK`, `WaitOnAddress`) and macOS (`os_unfair_lock`) also provide blocking synchronisation facilities; their APIs and implementation details differ from Linux futexes.

Many mutexes are also **adaptive**: on contention they spin briefly first, betting the holder is running on another core and will release soon, and only then sleep. The Linux kernel's own `mutex` does this "optimistic spinning" while the owner is running.

## Key takeaways

- A futex mutex can acquire and release an uncontended ordinary lock without a syscall.
- FUTEX_WAIT compares the word and queues the waiter atomically with respect to relevant futex operations.
- The three-state teaching mutex records possible waiters so unlock knows when to wake.

## Further reading

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper](https://www.akkadia.org/drepper/futex.pdf)
- [Linux futex manual](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Linux lock types and PREEMPT_RT](https://www.kernel.org/doc/html/latest/locking/locktypes.html)
- [PEP 703](https://peps.python.org/pep-0703/)
