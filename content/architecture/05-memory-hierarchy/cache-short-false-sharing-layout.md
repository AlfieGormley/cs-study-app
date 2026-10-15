---
id: cache-short-false-sharing-layout
title: Avoid false sharing and write contention
level: advanced
minutes: 5
sourceLesson: cache-arch-coherence
summary: Independent variables can compete for one coherence line.
---

This unit builds on the earlier cache lessons and focuses on avoid false sharing and write contention. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## False sharing

This unit assumes the coherence granule is a cache line; real protocols can have implementation-specific granularity. Coherence tracks that granule rather than the individual language variables within it. If two threads write two *different* variables that happen to sit in the same line, the hardware requires ownership of the shared line, much as it does for contended writes to one variable: the line ping-pongs between their caches in M state.

```c
#include <pthread.h>
#include <stdalign.h>
#define ITERS 100000000L

alignas(64) struct {
    volatile long a, b;
} counters;
// Assume 8-byte longs, 64-byte lines.

// Only this thread writes scalar a.
void *inc_a(void *_) {
    for (long i = 0; i < ITERS; i++)
        counters.a++;
    return 0;
}
// Only this thread writes scalar b.
void *inc_b(void *_) {
    for (long i = 0; i < ITERS; i++)
        counters.b++;
    return 0;
}
```

`volatile` requires observable accesses according to the C implementation; it is not an atomic or thread-synchronisation mechanism. This example has one writer per distinct scalar object; read the final counts only after joining both threads. A shared counter written by both threads would need atomics or a lock.

Each store requires ownership, but a core may execute many increments before ownership changes. The following is one possible interleaving, not one transfer guaranteed per increment:



```
 core0: write a -> needs M -> invalidate c1
 core1: write b -> needs M -> invalidate c0
 core0: write a -> miss, fetch from c1 ...
```

False sharing can make the two-core run slower; the size of the effect requires measurement. Under this 64-byte-line model, separate the independently written variables:

```c
#include <stdalign.h>
// Each element begins at a new model line.
struct padded {
    alignas(64) volatile long v;
};  /* 64 bytes under the stated ABI */
struct padded counters[2];
```

## Padding in practice

- **C++17**: `std::hardware_destructive_interference_size` (where the library provides it) provides an implementation-defined separation hint, not a runtime measurement of every machine on which the binary may run.
- **Linux kernel**: `____cacheline_aligned_in_smp`.
- **Java**: `@Contended` (internal; user code needs `-XX:-RestrictContended`). `LongAdder` uses striped cells to reduce update contention; its `sum()` is not an atomic snapshot, and performance depends on contention and usage.
- **Rust**: `crossbeam_utils::CachePadded` documents a conservative 128-byte padding choice on x86-64, including concern about adjacent-line prefetching on some processors. This library heuristic is not proof that every x86 CPU requires 128 bytes or every other platform has the same line size.
- Go: `golang.org/x/sys/cpu.CacheLinePad`.

## Better than padding: don't share writes

Padding fixes *false* sharing. *True* sharing (many threads updating one counter) still ping-pongs. The real fix is structural:

- Give each thread a **private accumulator** and combine at the end.
- Use **sharded/striped** counters (like `LongAdder`) when approximate concurrent aggregation is acceptable; cells are not necessarily one per thread, and a concurrent sum need not be a single-time snapshot.
- Batch updates, e.g. publish every 1,000 local events, accepting delayed visibility and flushing remaining events before a final total.

## Finding it

False sharing does not show up in source code review easily. Tools:

- `perf c2c` on Linux reports cache lines with heavy cross-core "HITM" traffic (loads that hit a modified line in another core) and the offsets within the line being touched.
- A tell-tale sign: performance gets worse as you add threads, while CPU utilisation stays high.

## Spinlocks and coherence

A naive spinlock repeatedly performs an atomic exchange. Under contention, competing read-modify-write requests can repeatedly transfer exclusive ownership. An exchange by a core that already owns the line need not cause a fresh transfer.

**Test-and-test-and-set** first spins on an **atomic relaxed load**, then tries an acquire exchange when the lock appears free; unlocking uses a release store. An ordinary non-atomic C/C++ load racing with a write is invalid, even on coherent hardware. Read polling can hit locally while the line remains shared, but it still reacts to invalidations.

Queue locks such as MCS let each waiter poll its own node; laying out nodes to avoid false sharing preserves that advantage. This is a protocol overview, not a complete lock implementation.

## Key takeaways
- Independent variables can compete for one coherence line.
- Use target-appropriate separation, private accumulation and valid atomic lock polling, then measure the effect.

## Further reading
- [CMU: Multicore cache coherence](https://course.ece.cmu.edu/~ece600/fall16/lectures/lecture_21.pdf)
- [Linux kernel: False sharing](https://docs.kernel.org/kernel-hacking/false-sharing.html)
- [LongAdder API and snapshot semantics](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html)
- [MESI protocol — Wikipedia](https://en.wikipedia.org/wiki/MESI_protocol)
- [MOESI protocol — Wikipedia](https://en.wikipedia.org/wiki/MOESI_protocol)
- [Cache coherence — Wikipedia](https://en.wikipedia.org/wiki/Cache_coherence)
- [Directory-based cache coherence — Wikipedia](https://en.wikipedia.org/wiki/Directory-based_cache_coherence)
- [False sharing — Wikipedia](https://en.wikipedia.org/wiki/False_sharing)
- [perf-c2c(1) — Linux manual page](https://man7.org/linux/man-pages/man1/perf-c2c.1.html)
- [CachePadded — crossbeam-utils docs](https://docs.rs/crossbeam-utils/latest/crossbeam_utils/struct.CachePadded.html)
