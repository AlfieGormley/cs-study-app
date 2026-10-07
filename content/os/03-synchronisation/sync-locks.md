---
id: sync-locks
title: Locks, spinlocks and futexes
level: intermediate
minutes: 14
summary: How mutexes and spinlocks are built from test-and-set and compare-and-swap, why Linux mutexes sit on futexes, and how contention and lock granularity decide whether your threads actually run in parallel.
---

A **lock** (or **mutex**, for mutual exclusion) turns a critical section into something only one thread can run at a time. You call `lock()` before touching shared data and `unlock()` afterwards. If another thread holds the lock, you wait.

```c
pthread_mutex_t m =
    PTHREAD_MUTEX_INITIALIZER;

void *work(void *arg) {
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&m);
        counter++;
        pthread_mutex_unlock(&m);
    }
    return NULL;
}
```

```python
import threading
lock = threading.Lock()

def work():
    global counter
    for _ in range(1_000_000):
        with lock:  # acquire, release
            counter += 1
```

Python's `with` releases the lock even if the body raises, which is the main reason to prefer it over calling `acquire()` and `release()` by hand.

The interesting question is how `lock()` itself avoids the race it is meant to prevent.

## Option 1: turn off interrupts

On a single CPU, disabling maskable interrupts can protect a short kernel section against relevant interrupt handlers, provided it cannot block, yield or otherwise schedule and the kernel's preemption rules are respected. It does not exclude every context, such as non-maskable interrupts.

This is genuinely used inside kernels for very short sections, but it fails as a general lock:

- It is a privileged operation; user programs cannot do it (and you would not trust them to).
- It does nothing on a **multiprocessor**: other cores keep running.
- Interrupt handling is delayed. Many interrupt sources remain pending, but excessive latency or finite device buffering can still lose events or data.

## Option 2: atomic hardware instructions

Every modern CPU provides instructions that read and write a memory location as one indivisible step, even across cores. Two are fundamental.

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
    atomic_flag_clear(&f);
}
```

This is a **spinlock**: a waiting thread loops ("spins") until the lock is free. It is correct because two threads can never both see the old value 0; the hardware serialises the two exchanges.

### Compare-and-swap

`CAS(addr, expected, new)` says: "if `*addr` still equals `expected`, set it to `new`; tell me whether it worked". On x86 it is `lock cmpxchg`.

```c
atomic_int l = 0;

void cas_lock(void) {
    int expected = 0;
    while (!atomic_compare_exchange_weak(
               &l, &expected, 1))
        expected = 0;  // CAS wrote the seen
                       // value here; reset
}
```

Note the C11 quirk: on failure, `atomic_compare_exchange_*` stores the value it actually found into `expected`, so the loop must reset it. The `_weak` form may fail spuriously (on ARM's load-linked/store-conditional instructions), which is fine inside a retry loop.

CAS is strictly more powerful than test-and-set. It can implement any read-modify-write update ("read x, compute f(x), CAS it in, retry if someone beat you"), which is the foundation of lock-free programming in lesson 6.

| Primitive | x86 | ARMv8 |
|---|---|---|
| test-and-set | `xchg` | `swp` / LL-SC |
| compare-and-swap | `lock cmpxchg` | `cas` / LL-SC |
| fetch-and-add | `lock xadd` | `ldadd` / LL-SC |

(ARMv8.0 builds these from `ldxr`/`stxr` pairs; ARMv8.1 added single-instruction atomics such as `cas` and `ldadd`.)

### Fairness: the ticket lock

A plain spinlock is unfair: when it is released, whichever core wins the race takes it, and an unlucky thread can starve. A **ticket lock** fixes this with fetch-and-add, like the numbered tickets at a deli counter:

```c
atomic_int next = 0, serving = 0;

void ticket_lock(void) {
    int me = atomic_fetch_add(&next, 1);
    while (atomic_load(&serving) != me)
        ;  // spin until our number
}

void ticket_unlock(void) {
    atomic_fetch_add(&serving, 1);
}
```

Tickets order admission by ticket allocation, assuming holders and waiters keep progressing and counter wraparound does not alias outstanding tickets. Linux queued spinlocks use queue-based waiting, but their implementation and fairness properties should not be equated with this simple ticket model.

## What spinning costs

Spinning burns CPU doing nothing useful. Worse, every `test_and_set` is a write, so each spinning core demands exclusive ownership of the lock's cache line. The line ping-pongs between cores, slowing down the holder too.

Two improvements:

- **Test-and-test-and-set**: spin on a plain atomic *load* (which all waiters can share in their caches) and only attempt the expensive exchange when the lock looks free.
- **Back off**: pause between attempts (x86's `pause` instruction, or an exponential delay).

The deeper problem is **preemption**. If the thread holding a spinlock is descheduled, every waiter spins for its whole time slice, achieving nothing. With 4 threads on 1 core and a 10 ms quantum, a waiting thread can burn the full 10 ms each time it is scheduled.

So spinlocks suit one niche: **very short critical sections on multicore machines, where the holder will not be preempted**. On non-PREEMPT_RT Linux, spinlock_t disables preemption while held; irqsave variants also mask local interrupts. Under PREEMPT_RT, spinlock_t instead has sleeping-lock semantics, while raw_spinlock_t remains a strict spinning lock.

## Sleeping locks and the futex

For user programs the right answer to "lock is busy" is usually: **stop running and let the OS wake you when it is free**. That needs the kernel, because only the kernel can put a thread to sleep. Avoiding a kernel transition can reduce uncontended-path overhead; actual costs and contention rates are workload- and platform-dependent. You do not want a syscall when nobody else is waiting.

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
        c = atomic_exchange(f, 2);
    while (c != 0) {
        futex_wait(f, 2);  // sleep
        c = atomic_exchange(f, 2);
    }
}

void unlock(atomic_int *f) {
    if (atomic_fetch_sub(f, 1) != 1) {
        atomic_store(f, 0);
        futex_wake(f, 1);  // wake one
    }
}
```

(`futex_wait` and `futex_wake` are illustrative wrappers. A real Linux implementation needs a correctly aligned 32-bit futex word compatible with its atomic representation, the appropriate private/shared operation and handling for interruptions, spurious wakes and errors.)

The fast paths are the point. An uncontended `lock` is one CAS; an uncontended `unlock` is one atomic decrement. This teaching algorithm illustrates the fast-path principle. Ordinary glibc mutexes also use user-space atomic state plus futex slow paths, but exact instructions and paths differ with mutex type, glibc version and optimizations. Windows (`SRWLOCK`, `WaitOnAddress`) and macOS (`os_unfair_lock`) use the same idea.

Many mutexes are also **adaptive**: on contention they spin briefly first, betting the holder is running on another core and will release soon, and only then sleep. The Linux kernel's own `mutex` does this "optimistic spinning" while the owner is running.

> [!note] Ownership
> A mutex has an owner: only the thread that locked it should unlock it. Unlocking a mutex you do not hold is undefined for a default pthread mutex (error-checking mutexes report it). Python's `threading.Lock` has no owner and can be released by any thread; `threading.RLock` has an owner and can be re-acquired by the same thread (re-entrant).

## Contention and granularity

A correctly implemented lock still needs a correct application protocol: all relevant accesses must participate, lifetimes must be valid and lock ordering must avoid deadlock. Performance then depends partly on contention.

No reproducible uncontended-lock timing is supplied here. When it is heavily contended, threads queue, sleep and wake, and the critical section becomes a serial bottleneck. Amdahl's law applies directly: if 10% of the work runs under one global lock, no number of cores can make the program more than 10 times faster.

The main lever is **granularity**, meaning how much data each lock protects.

| | Coarse-grained | Fine-grained |
|---|---|---|
| Example | one lock per table | one lock per bucket |
| Simplicity | easy to get right | many locks to order |
| Parallelism | low | high |
| Overhead | one lock op | more lock ops |

Real systems have moved from coarse to fine over time:

- **Linux's Big Kernel Lock** let only one CPU run most kernel code at a time when SMP support was first added. It was gradually replaced by fine-grained locks and finally removed in 2.6.39 (2011).
- **CPython's GIL** is the ultimate coarse lock: one lock around the whole interpreter. It makes the interpreter simple and single-threaded code fast, but stops CPU-bound Python threads running in parallel. PEP 703 introduced a free-threaded build that replaces it with fine-grained per-object locking.
- **Java's `ConcurrentHashMap`** originally used **lock striping** (16 segments by default, each with its own lock). Java 8 went further: CAS to fill an empty bin, and a lock on the first node of a bin only when it is already occupied.

Fine-grained locking has costs. More locks mean more chances to take them in inconsistent orders, which leads to deadlock (the subject of the next module), and operations spanning several items (resizing the whole table) become harder.

Practical rules:

1. **Keep critical sections short.** Never do I/O, logging or a network call while holding a hot lock.
2. **Measure before splitting.** Profilers and `perf lock` or mutex contention counters tell you which lock is actually hot.
3. **Avoid sharing instead of locking it.** Per-thread counters combined at the end can reduce contention when delayed aggregation preserves the required semantics.
4. **Watch for false sharing.** Independent writes sharing a cache line can cause coherence traffic even under separate locks. Cache-line size is architecture-dependent; 64 bytes is one common example.

> [!warning] Priority inversion
> A low-priority thread holds a lock, a high-priority thread waits for it, and a medium-priority thread preempts the low one. The high-priority thread is now effectively blocked by the medium one. This famously reset the Mars Pathfinder lander in 1997. The fix is **priority inheritance**: the holder temporarily runs at the waiter's priority (`PTHREAD_PRIO_INHERIT`).

> [!note] Content gap
> No reproducible lock or syscall benchmark accompanies this lesson, so exact nanosecond costs and universal speed-up claims are omitted. The futex code is a teaching sketch, not a portable production mutex.

## Key takeaways
- Locks are built on atomic hardware read-modify-write instructions: test-and-set (`xchg`), compare-and-swap (`lock cmpxchg`) and fetch-and-add (`lock xadd`).
- Spinlocks waste CPU and collapse if the holder is preempted; they suit short kernel critical sections with preemption disabled.
- A futex keeps the uncontended path in user space (one atomic op) and only calls into the kernel to sleep or wake when threads collide; glibc mutexes are built on it.
- Ticket locks order admission subject to progress and wraparound assumptions; queued-lock fairness is implementation-specific. Adaptive mutexes may spin before sleeping.
- Contention, not the lock itself, is the cost. Shrink critical sections, use finer granularity where it is measured to matter, or avoid sharing altogether.

## Further reading
- [OSTEP: Locks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper (PDF)](https://www.akkadia.org/drepper/futex.pdf)
- [futex(2) — Linux manual page](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Compare-and-swap — Wikipedia](https://en.wikipedia.org/wiki/Compare-and-swap)
- [Spinlock — Wikipedia](https://en.wikipedia.org/wiki/Spinlock)
- [PEP 703: Making the Global Interpreter Lock optional](https://peps.python.org/pep-0703/)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
