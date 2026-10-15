---
id: cache-short-coherence-routing
title: Route coherence and share dirty data
level: advanced
minutes: 3
sourceLesson: cache-arch-coherence
summary: Owned can defer a backing-level write-back; Forward designates a clean responder.
---

This unit builds on the earlier cache lessons and focuses on route coherence and share dirty data. Keep each example’s stated hardware geometry and model assumptions when applying its result.

Recall the preceding textbook MESI model: Modified means one writable dirty owner, Shared means clean read-only copies, and Exclusive means a sole clean copy. The variants below change how clean or dirty shared data is supplied.

## Variants used in real chips

- **MOESI**, used in some processor coherence designs: adds an **Owned (O) state**: dirty but shared. A core in M that is snooped by a reader moves to O and keeps supplying the data, while retaining responsibility for the dirty data. This can defer a backing-level write-back for read-shared dirty data.
- **MESIF**, used in some processor coherence designs: adds a **Forward (F) state**: a clean copy can be designated to supply later sharing requests. This avoids requiring every clean sharer to respond; exact routing, including service when no Forward copy remains, is implementation-specific.
- Arm's AMBA CHI interconnects use their own state names with equivalent ideas (unique/shared, clean/dirty).

## Snooping vs directories

How does a write find all the copies it must invalidate?

- **Snooping**: every request is broadcast and every cache checks its tags. Simple and fast with a few cores on a shared bus, but broadcast traffic grows with core count.
- Directory: a structure (often alongside the L3 or memory controller) tracks actual or possible sharers of a line. A write can target those candidates instead of broadcasting to every cache. Scales to many cores and CPU sockets.

Modern many-core chips mix the two: **snoop filters** (Intel) and directory caches track which cores *might* hold a line, so most requests avoid broadcasting. An inclusive L3 can act as a natural snoop filter: if a line is absent from that inclusive L3, it cannot be resident in the upper caches covered by the inclusion guarantee.

## What coherence costs

A **coherence miss** is a miss caused by a coherence invalidation of a previously cached line. A first-ever access can also obtain dirty data from another core, but that fact alone does not make it an invalidation-caused miss.

Remote ownership/data transfers can be much slower than a local L1 hit. A representative nanosecond range is absent because processor topology, load, placement and measurement method have not been reliably specified here. Measure the target system rather than treating a universal range as a guarantee.

Read-only shared lines can produce local hits after warming and while resident; initial fills, evictions and replication still consume resources. Repeated writes by different cores are a particularly costly pattern because they require ownership changes.

## Key takeaways
- Owned can defer a backing-level write-back; Forward designates a clean responder.
- Directories and snoop filters narrow candidate sharers, while read-only resident hits need no ownership change.

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
