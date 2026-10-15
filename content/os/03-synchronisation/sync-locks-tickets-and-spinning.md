---
id: sync-locks-tickets-and-spinning
title: Ticket order and the cost of spinning
level: intermediate
minutes: 3
summary: Follow ticket admission and decide when busy waiting is appropriate.
sourceLesson: sync-locks
---

A lock can be correct yet waste most of the machine’s time. Fair admission and efficient waiting are separate design choices.

### Fairness: the ticket lock

A plain spinlock is unfair: when it is released, whichever core wins the race takes it, and an unlucky thread can starve. A **ticket lock** fixes this with fetch-and-add, like the numbered tickets at a deli counter:

```c
atomic_int next = 0, serving = 0;

void ticket_lock(void) {
    // Claim a distinct place in the queue.
    int me = atomic_fetch_add(&next, 1);
    while (atomic_load(&serving) != me)
        ;  // spin until our number
}

void ticket_unlock(void) {
    // Admit the next allocated ticket.
    atomic_fetch_add(&serving, 1);
}
```

Tickets order admission by ticket allocation, assuming holders and waiters keep progressing and counter wraparound does not alias outstanding tickets. Linux queued spinlocks use queue-based waiting, but their implementation and fairness properties are not the same as this simple ticket model.

## What spinning costs

Spinning burns CPU doing nothing useful. Worse, every `test_and_set` is a write, so each spinning core demands exclusive ownership of the lock's cache line. The line ping-pongs between cores, slowing down the holder too.

Two improvements:

- **Test-and-test-and-set**: spin on a plain atomic *load* (which all waiters can share in their caches) and only attempt the expensive exchange when the lock looks free.
- **Back off**: pause between attempts (x86's `pause` instruction, or an exponential delay).

The deeper problem is **preemption**. If the thread holding a spinlock is descheduled, every waiter spins for its whole time slice, achieving nothing. With 4 threads on 1 core and a 10 ms quantum, a waiting thread can burn the full 10 ms each time it is scheduled.

So spinlocks suit one niche: **very short critical sections on multicore machines, where the holder will not be preempted**. On non-PREEMPT_RT Linux, spinlock_t disables preemption while held; irqsave variants also mask local interrupts. Under PREEMPT_RT, spinlock_t instead has sleeping-lock semantics, while raw_spinlock_t remains a strict spinning lock.

## Key takeaways

- Tickets order admission by allocation, subject to progress and safe counter-wrap assumptions.
- Spinning on a held lock consumes CPU and can increase cache-line contention.
- Pure spinning requires a suitable execution context; Linux PREEMPT_RT changes spinlock_t semantics.

## Further reading

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper](https://www.akkadia.org/drepper/futex.pdf)
- [Linux futex manual](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Linux lock types and PREEMPT_RT](https://www.kernel.org/doc/html/latest/locking/locktypes.html)
- [PEP 703](https://peps.python.org/pep-0703/)
