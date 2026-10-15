---
id: sync-lock-free-rcu-grace-period
title: RCU publication and grace periods
level: advanced
minutes: 4
summary: Publish a replacement object and wait for pre-existing readers before reclamation.
sourceLesson: sync-lock-free
---

An RCU reader may keep using an old object after another thread publishes a replacement. Safe reclamation therefore depends on reader lifetimes as well as pointer visibility.

## RCU: read-copy-update

**RCU** supports efficient read-side access to linked, pointer-based data; its exact read-side cost depends on flavour and configuration. It has been used throughout the Linux kernel since 2002 (Paul McKenney and others), for routing tables, the directory-entry cache, module lists and much more.

The idea is in the name. In this immutable-configuration example, a writer does not modify a published object. Instead it:

1. **Reads** the current version.
2. **Copies** it and modifies the copy.
3. **Updates** the shared pointer using the RCU publication API, providing the ordering required for readers of the new object.
4. Waits for an **RCU grace period**: until every reader that might still be using the old version has finished.
5. Frees the old version.

```c
struct config *cur;   // RCU-protected

int get_timeout(void) {
    rcu_read_lock();
    struct config *c =
        rcu_dereference(cur);
    // Keep dereference inside the read
    // section.
    int t = c->timeout;
    rcu_read_unlock();
    return t;
}

void set_timeout(int t) {   // under a mutex
    struct config *old = cur;
    struct config *new =
        malloc(sizeof *new);
    if (!new) return;  // report failure
    // Modify a private copy, never the old
    // one.
    *new = *old;
    new->timeout = t;
    rcu_assign_pointer(cur, new);
    synchronize_rcu();   // grace period
    // Pre-existing readers no longer need
    // old.
    free(old);
}
```

This is RCU-style pseudocode: a real kernel implementation uses kernel allocation and protected pointer-access APIs; a liburcu application needs its selected flavor's headers, registration, start-up and shutdown rules. Assume cur initially refers to a valid object and writers hold the same mutex.

For this publication pattern, `rcu_assign_pointer` supplies release-style ordering and `rcu_dereference` supplies the required pointer-dependency/compiler ordering. It is not a blanket claim that every RCU dereference is a C11 acquire load. That is the double-checked-locking lesson again.

```
time ---------------------------------->
R1  [--- reads old ---]
R2      [--- reads old ---]
pub         ^ new pointer published
R3              [-- reads new --]
GP          |<-- grace period -->|
free                             ^ old
```

synchronize_rcu waits for read-side sections that pre-exist its invocation, not necessarily every later reader. In the simplified diagram publication and the start of the grace-period wait are adjacent; R1/R2 may retain the old object. R3 is drawn as observing the replacement, which is one possible execution, not an immediate-visibility guarantee from its wall-clock start time. The RCU implementation must also supply the ordering that prevents a reader from using reclaimed old storage after the grace period. Actual grace-period completion need not coincide with the last illustrated unlock.

How can the kernel identify completion? In non-preemptible RCU, a context switch is one kind of quiescent state showing that a CPU is no longer executing a pre-existing read-side section; idle and user-mode transitions can also supply quiescent states. Preemptible RCU additionally tracks preempted readers. Readers must obey their flavour’s blocking and lifetime rules; read-side overhead varies with configuration. Costs and grace-period duration depend on RCU flavor, configuration and workload; no fixed timing is supplied here. `call_rcu()` lets a writer register a callback to free the old data later instead of blocking.

The trade-offs:

- Readers that retained an old version can see **stale data**. RCU supplies no fixed maximum age: whether that is acceptable depends on the application’s consistency and lifetime requirements.
- This copy-update example serialises writers with a mutex. Other RCU algorithms can use different update protocols; update/reclamation cost is workload-dependent.
- Old versions stay in memory until their RCU grace period ends, so a rapid run of updates can raise memory use.

In user space, `liburcu` provides RCU for applications.

## Key takeaways

- RCU publication orders construction before readers use the newly observed pointer.
- A grace-period wait covers pre-existing read-side sections; later readers need not delay it.
- Reader cost, grace-period duration and permitted operations depend on the RCU flavour and configuration.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
