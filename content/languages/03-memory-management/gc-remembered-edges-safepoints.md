---
id: gc-remembered-edges-safepoints
title: "Remembered edges and safepoints"
level: intermediate
minutes: 3
sourceLesson: gc-tracing
summary: "A write barrier records relevant stores so a partial collection cannot miss objects reached through older regions"
---

Collecting only part of a heap is safe only if references entering it are accounted for. A collector must also inspect threads and relocate objects using a protocol compatible with their changing state.

## The catch: old-to-young pointers

A minor collection only traces the young generation. But an old object can point at a young one:

```java
// Storing into an old cache may need a
// barrier.
cache.put(key, new Entry()); // old->young
```

If that `Entry` is reachable only through `cache`, a minor GC that ignored the old generation would free it while still in use. Scanning the whole old generation every time would defeat the point.

The answer is a **write barrier**: code associated with relevant reference stores, with redundant barriers sometimes eliminated. When the program writes a pointer into an old object, the barrier records it. A common HotSpot configuration divides memory into 512-byte cards; collector/version settings can change the granularity. A card-based collector records relevant reference stores in a card table. At a minor GC, only dirty cards are scanned as extra roots. A **remembered set** records relevant incoming locations, at slot or coarser region/card granularity depending on the collector.

This is the real cost of generational GC: relevant pointer writes may pay a small tax (some barriers are elided or use different mechanisms), in exchange for cheap minor collections.

## Stop-the-world and safepoints

Collectors move objects and read the stacks, so the classic approach is to **stop the world**: pause every application thread, collect, then resume. In a conventional precise stop-the-world design, threads are brought to safepoints, places where the compiler has recorded exactly where every pointer is (for example, at method calls and loop back-edges).

Pause length grows with the work: a minor GC pause tracks the survivors, while a full mark-compact of a 30 GB old generation can pause for seconds. The modern-collector units cover how modern collectors do most of that work concurrently.

## Diagnose the scanned work

A large old cache can point into many young objects without being collected itself. A young collection still needs to find those incoming references. Dirty-card scanning or remembered-set processing can therefore grow even if the young allocation area is unchanged. The live survivors, roots and scan workload matter more than the nursery size alone.

Safepoints make particular runtime state understandable to a precise collector; they are not a universal claim that every collector stops every thread for an entire collection. Modern collectors use barriers and additional protocols to do substantial marking or relocation concurrently. Here the stop-the-world design provides the simpler baseline.

## Key takeaways
- A write barrier records relevant stores so a partial collection cannot miss objects reached through older regions.
- Cards record coarse regions, while remembered sets may record slots or regions; implementations and granularity vary.
- Safepoints provide inspectable execution state for a conventional precise collector; actual pause time depends on the work performed.

## Further reading
- [Tracing garbage collection — Wikipedia](https://en.wikipedia.org/wiki/Tracing_garbage_collection)
- [Cheney's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Cheney%27s_algorithm)
- [HotSpot VM garbage collection tuning guide: generations — Oracle](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-collector-implementation.html)
- [The Garbage Collection Handbook (Jones, Hosking, Moss)](https://gchandbook.org/)
- [Boehm-Demers-Weiser conservative garbage collector](https://www.hboehm.info/gc/)
- [Primary verification source 2](https://go.dev/doc/gc-guide)
- [Primary verification source 3](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-garbage-collector-tuning.html)
