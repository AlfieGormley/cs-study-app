---
id: dl-debugging-lockdep
title: Detecting observed lock-order cycles
level: advanced
minutes: 2
sourceLesson: dl-debugging
summary: Lockdep records class dependencies and can combine orders observed at different times.
---

## Catching cycles before they happen: lockdep

Waiting for a deadlock to happen in production is the worst way to find it. The Linux kernel's **lockdep** (runtime locking correctness validator, `CONFIG_PROVE_LOCKING`) finds lock-order bugs the first time the *order* is observed, whether or not the threads collide.

How it works:

1. Locks are grouped into **classes**: every `inode->i_lock` is one class, however many inodes exist. That keeps the graph small and makes one observation apply to all instances.
2. Every time a task takes lock B while holding lock A, lockdep records the dependency `A → B`.
3. Before adding an edge, it checks whether the edge would close a cycle in the dependency graph. If so, it reports it immediately.

```
WARNING: possible circular locking
         dependency detected
...
 Possible unsafe locking scenario:

       CPU0            CPU1
       ----            ----
  lock(&a->lock);
                       lock(&b->lock);
                       lock(&a->lock);
  lock(&b->lock);

 *** DEADLOCK ***
```

(Abridged.) The key property: one code path can run on Monday and the opposite code path on Friday, on different CPUs, never overlapping. Lockdep still connects `A → B` and `B → A` and reports the cycle.

It also checks **interrupt-context rules**. If a lock is ever taken in a hardirq handler, and elsewhere taken with interrupts *enabled*, an interrupt could arrive while the lock is held and spin on it forever on the same CPU. Lockdep flags this as an inconsistent lock state.

Costs and limits:

- Significant overhead, so it's enabled in debug and CI kernels (and by fuzzers such as syzbot), with deployment depending on overhead and diagnostic needs.
- It only knows about orders it has **seen**. Code paths that never run in testing are unchecked.
- Legitimate same-class nesting needs a real hierarchy and correctly mapped annotations such as `mutex_lock_nested()`. Incorrect annotations can hide genuine bugs as well as create false reports.

## Key takeaways
- Lockdep records class dependencies and can combine orders observed at different times.
- Interrupt-context rules can expose same-CPU re-entry deadlocks.
- Unexecuted code paths and incorrect nesting annotations remain limits.

## Further reading
- [Linux: runtime locking correctness validator](https://docs.kernel.org/locking/lockdep-design.html)
