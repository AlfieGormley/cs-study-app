---
id: cache-short-mesi-transitions
title: Trace ownership transitions
level: advanced
minutes: 3
sourceLesson: cache-arch-coherence
summary: Textbook serialised requests model reads, ownership acquisition and upgrades.
---

This unit builds on the earlier cache lessons and focuses on trace ownership transitions. Keep each example’s stated hardware geometry and model assumptions when applying its result.

Recall MESI’s stable states: Modified is the sole writable dirty copy; Exclusive is the sole clean copy; Shared is clean and may have peer copies; Invalid cannot serve an access. This unit traces those permissions for one line.

## Transitions

For this textbook snooping model, coherence transactions are serialised and observed by the other participating caches. The table omits transient states, retries and simultaneous-request races:

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

In this textbook MESI model, M → S also updates the backing level so shared copies are clean relative to it. That backing level can be another cache; a real coherence transaction need not reach DRAM.

## Worked trace

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

1. Core 0 reads: nobody else has it, so E.
2. Core 1 reads: core 0 sees the BusRd and drops to S; both S.
3. Core 0 writes: it must invalidate core 1 (BusUpgr). Core 0 M, core 1 I.
4. Core 1 reads: miss. Core 0 snoops, supplies the dirty data (and updates the backing level in this model), and both end in S.
5. Core 1 writes: invalidates core 0; core 1 M.

When a different core acquires write permission, coherence communication is required; data need not always be transferred directly from the previous writer. That is the cost to keep in mind.

## Why E exists

Without E (the simpler MSI protocol), a single-threaded program that reads then writes private data would pay two requests: BusRd to get it in S, then BusUpgr to write. E recognises "nobody else has this" and avoids a separate ownership-upgrade coherence transaction for that write. The store still has local execution cost; how often this helps is workload-dependent.

## Key takeaways
- Textbook serialised requests model reads, ownership acquisition and upgrades.
- Exclusive permits a private clean-to-dirty transition without a separate coherence request.

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
