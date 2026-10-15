---
id: sync-lock-free-seqlock-retries
title: Validate seqlock snapshots
level: advanced
minutes: 3
summary: Use an even unchanged sequence value to decide whether a retry-safe copy is usable.
sourceLesson: sync-lock-free
---

A short update to several plain values can overlap a reader’s copy. A sequence counter lets a reader detect that overlap and discard the speculative copy under a memory model that permits the protocol.

## Seqlocks

A **seqlock** lets readers proceed without writing anything. The writer increments a sequence counter before and after each update, so the counter is odd while a write is in progress. Readers read the counter, read the data, then read the counter again, and retry if it was odd or has changed.

```text
writer (writers serialised by a lock):
  increment sequence counter: now odd
  update the protected fields
  increment sequence counter: even again

reader:
  read the initial sequence counter
  retry if it is odd
  copy the protected fields
  read the final sequence counter
  accept only if even and unchanged
```

The acceptance rule can be expressed precisely. This model assumes the counter cannot wrap back to the same value during one read attempt:

```formula
(s_start mod 2) = 0
s_end = s_start
where
s_start: the sequence-counter value read before copying the fields
s_end: the sequence-counter value read after copying the fields
mod: modulo, the remainder after integer division; a remainder of zero on division by two means the count is even
In words: accept the copy only when both conditions hold: the first count is even, and the final count matches it. For example, counts ten and twelve require a retry despite both being even.
```


This is algorithm pseudocode. Portable C requires a race-free representation (for example atomic fields) plus a proven ordering protocol; retrying does not undo undefined behavior. Linux seqlock APIs follow the Linux kernel memory model and do not magically make arbitrary plain C fields portable atomic objects. Writers must also meet the API's serialization and non-preemption requirements.

These readers do not take the writer lock or update a shared reader count, reducing contention. They do not scale perfectly: cache traffic and repeated retries still cost time. The cost: a reader may read torn, inconsistent data and must throw it away and retry, so it must never follow pointers inside that data (they might point to memory that was already freed). Seqlocks suit small, plain values updated often and read constantly. Linux timekeeping uses sequence-counter protocols for consistent snapshots. Clock-specific fast paths, tickless operation and clocksource handling differ; not every clock query or time update follows one universal path.

## Key takeaways

- Accept a copy only when the sequence value was even and is unchanged.
- Readers may need retries and must not dereference pointers that an update could invalidate.
- Portable C and kernel seqlock implementations need their own proven race-free/order protocols.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
