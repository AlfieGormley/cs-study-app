---
id: sync-locks-atomic-lock-primitives
title: Build a spinlock from atomic operations
level: intermediate
minutes: 3
summary: Understand test-and-set and the expected-value update performed by C compare-exchange.
sourceLesson: sync-locks
---

The lock’s own admission step must be atomic. An ordinary read followed by an ordinary write would simply move the original race into the lock implementation.

## Option 2: atomic hardware instructions

Mainstream multiprocessors provide atomic read-modify-write facilities for supported memory types and operand sizes. Two are fundamental.

### Test-and-set

`test_and_set(addr)` writes 1 to `*addr` and returns the **old** value, atomically. On x86 this is `xchg`. If the old value was 0, you have just taken the lock; if it was 1, someone else already had it.

```c
#include <stdatomic.h>

atomic_flag f = ATOMIC_FLAG_INIT;

void spin_lock(void) {
    while (atomic_flag_test_and_set(&f))
        ;  // old value 1: held, retry
}

void spin_unlock(void) {
    // Clear only after protected work ends.
    atomic_flag_clear(&f);
}
```

This is a **spinlock**: a waiting thread loops ("spins") until the lock is free. It is correct because two threads can never both see the old value 0; the hardware serialises the two exchanges.

### Compare-and-swap

`CAS(addr, expected, new)` says: "if `*addr` still equals `expected`, set it to `new`; tell me whether it worked". On x86 it is `lock cmpxchg`.

```c
atomic_int l = 0;

void cas_lock(void) {
    // Only an observed zero permits entry.
    int expected = 0;
    while (!atomic_compare_exchange_weak(
               &l, &expected, 1))
        expected = 0;  // CAS wrote the seen
                       // value here; reset
}
```

Note the C11 quirk: on failure, `atomic_compare_exchange_*` stores the value it actually found into `expected`, so the loop must reset it. The `_weak` form may fail spuriously (on ARM's load-linked/store-conditional instructions), which is fine inside a retry loop.

For arbitrary thread counts, CAS has a stronger consensus power than test-and-set. It can implement a single-object read-modify-write update ("read the current value, compute the new value from it, CAS it in, retry if someone beat you"), which is the foundation of the later lock-free units, under their atomic-progress and memory-lifetime assumptions.

| Primitive | x86 | ARMv8 |
|---|---|---|
| test-and-set | `xchg` | `swp` / LL-SC |
| compare-and-swap | `lock cmpxchg` | `cas` / LL-SC |
| fetch-and-add | `lock xadd` | `ldadd` / LL-SC |

(ARMv8.0 builds these from `ldxr`/`stxr` pairs; ARMv8.1 added single-instruction atomics such as `cas` and `ldadd`.)

## Key takeaways

- An atomic test-and-set lets exactly one contender observe an unlocked flag.
- A failed C compare-exchange updates the expected argument, which a lock retry must reset.
- Weak compare-exchange may fail spuriously; the retry protocol must tolerate it.

## Further reading

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper](https://www.akkadia.org/drepper/futex.pdf)
- [Linux futex manual](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Linux lock types and PREEMPT_RT](https://www.kernel.org/doc/html/latest/locking/locktypes.html)
- [PEP 703](https://peps.python.org/pep-0703/)
