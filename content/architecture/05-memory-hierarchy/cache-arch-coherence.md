---
id: cache-arch-coherence
title: Cache coherence (MESI) and false sharing
level: advanced
minutes: 14
summary: How multicore CPUs keep private caches in agreement, the MESI protocol and its MOESI/MESIF variants, snooping vs directories, what coherence costs, and how false sharing silently destroys multithreaded performance.
---

Many multicore CPUs have private per-core caches, though which levels are private or shared depends on the design. If two cores both cache the line holding variable `x`, and one of them writes `x`, the other now holds a stale copy. Without a fix, two threads could see different values for the same address forever.

Within a hardware-coherent domain, **cache coherence** makes participating caches agree on a per-location write order. This does not make unsynchronised C/C++ data races valid, order accesses to different locations, or guarantee coherence with every device or memory type. Software still needs the language's atomics/synchronisation and any required device cache maintenance.

## The invariant

Coherence protocols maintain one rule per cache line:

> [!note] Single writer, multiple readers
> In a stable state, a line can have **one cache with exclusive write permission** (which can also read), or **multiple read-only cached copies**. It must not have a writable copy alongside independently usable shared copies.

In the **write-invalidate** protocol studied here, a writer must obtain exclusive permission and invalidate other usable copies. Write-update protocols instead distribute new data; their traffic trade-offs differ.

Note that coherence is about **one location**. The ordering rules across *different* locations are the **memory consistency model** (x86-TSO, Arm's weaker model), covered in the Parallel Hardware module.

## MESI

The classic simplified protocol assigns each participating cache-line entry one of four stable states:

| State | Valid | Dirty | Other copies? |
|---|---|---|---|
| **M**odified | yes | yes | none |
| **E**xclusive | yes | no | none |
| **S**hared | yes | no | maybe |
| **I**nvalid | no | - | - |

- **M**: this cache has the only copy and it has been written; the backing level may be stale. It must be written back (or handed over) before anyone else can read it.
- **E**: the only copy, clean. The core can write it **silently** (E → M) without telling anyone.
- **S**: clean, and other caches may have it too. A write first requires invalidating them.
- **I**: not usable; any access is a miss.

### Transitions

For this textbook snooping model, transactions are serialised and observed by the other participating caches. The table omits transient states, retries and simultaneous-request races:

- **BusRd**: "I want to read this line."
- **BusRdX**: "I want to write this line; everyone else invalidate" (a read-for-ownership).
- **BusUpgr**: "I already have it in S; everyone else invalidate."

| Now | Event | Action | Next |
|---|---|---|---|
| I | local read | BusRd | E (no sharers) or S |
| I | local write | BusRdX | M |
| S | local write | BusUpgr | M |
| E | local write | none | M |
| M | snoop BusRd | supply data | S |
| M | snoop BusRdX | supply data | I |
| E | snoop BusRd | - | S |
| E/S | snoop BusRdX/Upgr | - | I |

In this textbook MESI model, M → S also updates the backing level so shared copies are clean relative to it. That backing level can be another cache; a real transaction need not reach DRAM.

### Worked trace

Two cores, line X not cached anywhere.

```
 step            core0  core1  traffic
 0 read  X       E      I      BusRd
 1 read  X       S      S      BusRd
 0 write X       M      I      BusUpgr
 1 read  X       S      S      BusRd,
                                c0 supplies
 1 write X       I      M      BusUpgr
```

1. Core 0 reads: nobody else has it, so **E**.
2. Core 1 reads: core 0 sees the BusRd and drops to **S**; both S.
3. Core 0 writes: it must invalidate core 1 (BusUpgr). Core 0 **M**, core 1 **I**.
4. Core 1 reads: miss. Core 0 snoops, supplies the dirty data (and updates the backing level in this model), and both end in **S**.
5. Core 1 writes: invalidates core 0; core 1 **M**.

When a different core acquires write permission, coherence communication is required; data need not always be transferred directly from the previous writer. That is the cost to keep in mind.

### Why E exists

Without E (the simpler MSI protocol), a single-threaded program that reads then writes private data would pay two requests: BusRd to get it in S, then BusUpgr to write. E recognises "nobody else has this" and avoids a separate ownership-upgrade transaction for that write. The store still has local execution cost; how often this helps is workload-dependent.

## Variants used in real chips

- **MOESI**, used in some processor coherence designs: adds **Owned**: dirty but shared. A core in M that is snooped by a reader moves to O and keeps supplying the data, while retaining responsibility for the dirty data. This can defer a backing-level write-back for read-shared dirty data.
- **MESIF**, used in some processor coherence designs: adds **Forward**: among several S copies, one is designated F and is the one that answers requests, so a read gets one response rather than many.
- Arm's AMBA CHI interconnects use their own state names with equivalent ideas (unique/shared, clean/dirty).

## Snooping vs directories

How does a write find all the copies it must invalidate?

- **Snooping**: every request is broadcast and every cache checks its tags. Simple and fast with a few cores on a shared bus, but broadcast traffic grows with core count.
- **Directory**: a structure (often alongside the L3 or memory controller) tracks actual or possible sharers of a line. A write can target those candidates instead of broadcasting to every cache. Scales to many cores and sockets.

Modern many-core chips mix the two: **snoop filters** (Intel) and directory caches track which cores *might* hold a line, so most requests avoid broadcasting. An inclusive L3 can act as a natural snoop filter: if a line is absent from that inclusive L3, it cannot be resident in the upper caches covered by the inclusion guarantee.

## What coherence costs

A **coherence miss** is a miss caused by a coherence invalidation of a previously cached line. A first-ever access can also obtain dirty data from another core, but that fact alone does not make it an invalidation-caused miss.

Remote ownership/data transfers can be much slower than a local L1 hit. A representative nanosecond range is absent because processor topology, load, placement and measurement method have not been reliably specified here. Measure the target system rather than treating a universal range as a guarantee.

Read-only shared lines can produce local hits after warming and while resident; initial fills, evictions and replication still consume resources. Repeated writes by different cores are a particularly costly pattern because they require ownership changes.



## False sharing

Coherence works on **lines**, not variables. If two threads write two *different* variables that happen to sit in the **same line**, the hardware treats it exactly like a contended write to one variable: the line ping-pongs between their caches in M state.

```c
#include <pthread.h>
#include <stdalign.h>
#define ITERS 100000000L

alignas(64) struct {
    volatile long a, b;
} counters;
// Assume 8-byte longs, 64-byte lines.

void *inc_a(void *_) {
    for (long i = 0; i < ITERS; i++)
        counters.a++;
    return 0;
}
void *inc_b(void *_) {
    for (long i = 0; i < ITERS; i++)
        counters.b++;
    return 0;
}
```

`volatile` requires observable accesses according to the C implementation; it is **not** an atomic or thread-synchronisation mechanism. This example has one writer per distinct scalar object; read the final counts only after joining both threads. A shared counter written by both threads would need atomics or a lock.

Each store requires ownership, but a core may execute many increments before ownership changes. The following is one possible interleaving, not one transfer guaranteed per increment:



```
 core0: write a -> needs M -> invalidate c1
 core1: write b -> needs M -> invalidate c0
 core0: write a -> miss, fetch from c1 ...
```

False sharing can make the two-core run slower; the size of the effect requires measurement. Under this 64-byte-line model, separate the independently written variables:

```c
#include <stdalign.h>
struct padded {
    alignas(64) volatile long v;
};  /* 64 bytes under the stated ABI */
struct padded counters[2];
```

### Padding in practice

- **C++17**: `std::hardware_destructive_interference_size` (where the library provides it) provides an implementation-defined separation hint, not a runtime measurement of every machine on which the binary may run.
- **Linux kernel**: `____cacheline_aligned_in_smp`.
- **Java**: `@Contended` (internal; user code needs `-XX:-RestrictContended`). `LongAdder` uses striped cells to reduce update contention; its `sum()` is not an atomic snapshot, and performance depends on contention and usage.
- **Rust**: `crossbeam_utils::CachePadded` documents a conservative **128-byte** padding choice on x86-64, including concern about adjacent-line prefetching on some processors. This library heuristic is not proof that every x86 CPU requires 128 bytes or every other platform has the same line size.
- **Go**: `golang.org/x/sys/cpu.CacheLinePad`.

### Better than padding: don't share writes

Padding fixes *false* sharing. *True* sharing (many threads updating one counter) still ping-pongs. The real fix is structural:

- Give each thread a **private accumulator** and combine at the end.
- Use **sharded/striped** counters (like `LongAdder`) when approximate concurrent aggregation is acceptable; cells are not necessarily one per thread, and a concurrent sum need not be a single-time snapshot.
- Batch updates, e.g. publish every 1,000 local events, accepting delayed visibility and flushing remaining events before a final total.

### Finding it

False sharing does not show up in source code review easily. Tools:

- `perf c2c` on Linux reports cache lines with heavy cross-core "HITM" traffic (loads that hit a modified line in another core) and the offsets within the line being touched.
- A tell-tale sign: performance gets **worse** as you add threads, while CPU utilisation stays high.

## Spinlocks and coherence

A naive spinlock repeatedly performs an atomic exchange. Under contention, competing read-modify-write requests can repeatedly transfer exclusive ownership. An exchange by a core that already owns the line need not cause a fresh transfer.

**Test-and-test-and-set** first spins on an **atomic relaxed load**, then tries an acquire exchange when the lock appears free; unlocking uses a release store. An ordinary non-atomic C/C++ load racing with a write is invalid, even on coherent hardware. Read polling can hit locally while the line remains shared, but it still reacts to invalidations.

Queue locks such as MCS let each waiter poll its own node; laying out nodes to avoid false sharing preserves that advantage. This is a protocol overview, not a complete lock implementation.



## Key takeaways
- Coherence enforces single-writer/multiple-reader per line; writes invalidate all other copies.
- MESI: M (only, dirty), E (only, clean, silent write), S (clean, shared), I. MOESI adds Owned; MESIF adds Forward.
- Snooping broadcasts; directories and snoop filters track sharers to scale.
- Ownership changes and remote data transfers can be expensive; their latency is topology- and workload-dependent.
- False sharing occurs when independent writes contend for one coherence line. Use target-appropriate layout or private accumulation, and measure the effect.

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
