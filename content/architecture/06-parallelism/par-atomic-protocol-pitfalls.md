---
id: par-atomic-protocol-pitfalls
title: Atomic protocols, races and store-buffering pitfalls
level: intermediate
minutes: 3
sourceLesson: par-memory-models
summary: Acquire/release alone does not forbid both store-buffering loads reading initial values.
---

> [!warning] Acquire/release does not by itself forbid store buffering
> At the C/C++ language level, both acquire loads in SB may read the initial zeros, so neither reads from the other thread’s release store. There is no synchronises-with edge connecting the threads, and (0, 0) remains permitted. A particular target mapping may be stronger and forbid it. Making all four operations seq_cst is one sufficient solution; correctly placed seq_cst fences or a suitable lock protocol are alternatives. A hardware fence alone does not repair a C/C++ data race on ordinary objects.

## Pitfalls

- **`volatile` is not a synchronisation tool in C or C++.** Volatile accesses obey their language-specific observable-access rules, but do not supply C/C++ inter-thread atomicity or synchronisation. Java volatile has different synchronisation semantics; that does not make an arbitrary racy Java program sequentially consistent.
- **The compiler reorders too.** Even on x86, plain `data = 42; flag = 1;` may be swapped by the optimiser. A correctly designed atomic protocol constrains both compiler and hardware behaviour; merely changing a variable to atomic does not fix every protocol.
- **"Works on my machine."** Testing on x86 cannot find bugs that only weak ordering exposes. Run concurrency tests on ARM, and use ThreadSanitizer to catch data races.
- **Relaxed is for counters.** An atomic fetch_add with relaxed ordering can accumulate an independent statistic without lost increments; separate load-plus-store is not an atomic increment. Publishing unrelated data through a flag needs additional synchronisation.
- **seq_cst by default.** Use the default ordering unless profiling shows the barrier matters. Measure any claimed performance benefit before weakening a proven protocol.

> [!note] Evidence limits
> Rosetta performance attribution and a version-independent Linux spinlock instruction catalogue is omitted because the exact implementation contracts and representative measurements were not reliably established; model-level ordering is taught instead.

## Key takeaways
- Acquire/release alone does not forbid both store-buffering loads reading initial values.
- C/C++ volatile does not establish inter-thread synchronisation.

## Further reading
- [Lamport’s original sequential-consistency paper](https://lamport.azurewebsites.net/pubs/multi.pdf)
- [The x86-TSO model](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)
- [The revised Arm multicopy-atomic model](https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf)
- [C++ draft: races](https://eel.is/c++draft/intro.races)
- [C++ draft: atomic ordering](https://eel.is/c++draft/atomics.order)
