---
id: cache-short-mesi-permissions
title: Coherence permissions and MESI states
level: advanced
minutes: 3
sourceLesson: cache-arch-coherence
summary: Coherence orders writes per location without making language data races valid.
---

Many multicore CPUs have private per-core caches, though which levels are private or shared depends on the design. If two cores both cache the line holding variable `x`, and one of them writes `x`, the other now holds a stale copy. Without a fix, two threads could see different values for the same address forever.

Within a hardware-coherent domain, **cache coherence** makes participating caches agree on a per-location write order. This does not make unsynchronised C/C++ data races valid, order accesses to different locations, or guarantee coherence with every device or memory type. Software still needs the language's atomics/synchronisation and any required device cache maintenance.

## The invariant

Coherence protocols maintain one rule per cache line:

> [!note] Single writer, multiple readers
> In a stable state, a line can have one cache with exclusive write permission (which can also read), or multiple read-only cached copies. It must not have a writable copy alongside independently usable shared copies.

In the **write-invalidate** protocol studied here, a writer must obtain exclusive permission and invalidate other usable copies. Write-update protocols instead distribute new data; their traffic trade-offs differ.

Note that coherence is about one location. The ordering rules across *different* locations are the **memory consistency model** (x86-TSO, Arm's weaker model), covered in the Parallel Hardware module.

## MESI

The classic simplified protocol assigns each participating cache-line entry one of four stable states:

| State | Valid | Dirty | Other copies? |
|---|---|---|---|
| Modified | yes | yes | none |
| Exclusive | yes | no | none |
| Shared | yes | no | maybe |
| Invalid | no | - | - |

- M: this cache has the only copy and it has been written; the backing level may be stale. A request by another cache must obtain the current data through the protocol, potentially causing a write-back or ownership handover.
- E: the only copy, clean. The core can write it silently (E → M) without telling anyone.
- S: clean, and other caches may have it too. A write first requires invalidating them.
- I: not usable; any access is a miss.

## Key takeaways
- Coherence orders writes per location without making language data races valid.
- MESI distinguishes private clean, private dirty, clean shared and invalid line entries.

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
