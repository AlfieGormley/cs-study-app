---
id: par-sc-store-buffer
title: Sequential consistency and store buffering
level: intermediate
minutes: 3
sourceLesson: par-memory-models
summary: Sequential consistency preserves each thread’s program order within one interleaving.
---

Cache coherence (from the memory hierarchy module) guarantees that all cores agree on the history of writes to *one* address. It says nothing about the order in which a core sees writes to *different* addresses. That second question is the job of the **memory consistency model**, and mistakes can produce intermittent, platform-dependent bugs.

## The model you expect: sequential consistency

Leslie Lamport defined **sequential consistency** (SC) in 1979. A multicore is SC if the result of any run is the same as if all cores' operations were executed in *some single interleaving*, with each core's operations appearing in program order.

Take two threads and two variables, both initially 0. This is the **store buffering** (SB) litmus test:

```
x = y = 0
Thread 1       Thread 2
x = 1          y = 1
r1 = y         r2 = x
```

Under SC, at least one store must come first in the interleaving, so at least one thread must see a 1. The possible outcomes for `(r1, r2)` are `(0, 1)`, `(1, 0)` or `(1, 1)`. **`(0, 0)` is impossible.**

The x86-TSO model permits (0, 0) for the ordinary-memory accesses described below. A particular experiment need not observe every permitted outcome; failure to observe it does not prove SC.

## Why hardware breaks SC

A store may wait for cache-line ownership or other resources. A **store buffer** can decouple execution/retirement from making committed stores globally observable, allowing independent work to continue while capacity remains. Later loads can execute while earlier stores are still waiting in the buffer.

```
 Core 1               Core 2
 [store buf: x=1]     [store buf: y=1]
      |  r1=y reads 0      |  r2=x reads 0
      v                    v
 ======== shared memory: x=0, y=0 ========
```

Both stores are sitting in buffers, invisible to the other core. Both loads read memory and get 0. Each core's own view is consistent (a same-address load in the abstract model reads its newest buffered store; real **store-to-load forwarding** can require matching size/alignment or waiting), but globally the store appears to have happened after the load.

Out-of-order execution, non-blocking caches and compilers can reorder memory operations too. SC constrains observable outcomes, not necessarily speculative internal execution. Speculation, caches and store buffers can coexist with SC if violations are prevented or detected and recovered. Weaker models allow additional observable behaviours.

## Key takeaways
- Sequential consistency preserves each thread’s program order within one interleaving.
- Store buffers can permit observations excluded by sequential consistency.

## Further reading
- [Lamport’s original sequential-consistency paper](https://lamport.azurewebsites.net/pubs/multi.pdf)
- [The x86-TSO model](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)
- [The revised Arm multicopy-atomic model](https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf)
- [C++ draft: races](https://eel.is/c++draft/intro.races)
- [C++ draft: atomic ordering](https://eel.is/c++draft/atomics.order)
