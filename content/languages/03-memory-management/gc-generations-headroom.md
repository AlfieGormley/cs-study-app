---
id: gc-generations-headroom
title: "Young survival and heap headroom"
level: intermediate
minutes: 5
sourceLesson: gc-tracing
summary: "Generational collection relies on workload-dependent survival patterns; promotion and collection terminology vary across runtimes"
---

Two different observations can reduce tracing overhead: young allocations may have low survival, and a larger allocation allowance can buy more time between collections. Keep empirical survival patterns separate from the assumptions of a cost model.

## The generational hypothesis

Many workloads have the useful empirical pattern that most allocations become unreachable quickly, but survival rates and lifetimes are workload-dependent. Temporary strings, iterators, boxed numbers and request-scoped objects are common examples. A minority, such as caches and configuration, live for the whole run.

**Generational collectors** exploit this by splitting the heap by age:

```
 young generation        old generation
 +------+-----+-----+    +---------------+
 | eden | S0  | S1  | -> |  tenured      |
 +------+-----+-----+    +---------------+
  new objects here        survivors promoted
```

- New objects are bump-allocated in the **young generation** (classic HotSpot generational collectors use eden and survivor spaces; G1 uses regions).
- When it fills, a **minor collection** copies its few survivors out. Because the young generation is small and mostly dead, this is fast, with a pause depending on live bytes, root scanning and the implementation.
- Objects that survive several minor collections are moved to the **old generation**; this is called **object promotion** or **tenuring**.
- The old generation is usually examined less often. Terminology varies: an old-generation or major cycle need not be a full-heap stop-the-world collection.

> [!example] Rough numbers
> In a simplified fill-and-collect model, a service allocates 500 MB/s into 250 MB of available young allocation space. Ignoring pause time and survivor-space overhead, it fills in 0.5 s. If 2% of those bytes survive, each collection copies about 5 MB. The other 245 MB is reclaimed without being touched.

The two numbers in that example come from one division and one multiplication:

```formula
t = Y / A
t = 250 MB / (500 MB/s) = 0.5 s
C = f × Y
C = 0.02 × 250 MB = 5 MB
where
t: the time between minor collections, in seconds (s)
Y: the young-generation space available for new objects, in megabytes (MB)
A: the allocation rate: how fast the program creates new objects, in MB per second (MB/s)
C: the bytes copied out by each minor collection, in MB
f: the survival fraction: the share of young bytes still live at collection time (2% = 0.02)
MB: megabyte, 1,000,000 bytes
s: seconds
In words: the young generation fills in its size divided by the allocation rate, and each collection copies only the small surviving fraction of it.
```

Double the allocation rate and collections come twice as often; double the survival fraction and each one copies twice as much. Real collectors also scan roots and dirty cards, so a minor collection has a cost even when almost nothing survives.

## The space-time trade-off

In a steady model with fixed live size, allocation rate and dominant marking cost, each collection costs roughly the live data and yields about the spare room. Ignoring sweep, root and fixed overhead:

```formula
W ≈ L / (H − L)
W ≈ 1 GB / (1.5 GB − 1 GB) = 2
W ≈ 1 GB / (3 GB − 1 GB) = 0.5
where
W: GC work per byte allocated: roughly how many bytes the collector traces for every byte the program allocates (a ratio, no unit)
L: the live data: bytes still reachable, which every collection must trace, in gigabytes (GB)
H: the total heap size, in GB
H − L: the headroom: free space the program can allocate into before the next collection
GB: gigabyte, 1,000,000,000 bytes
≈: approximately equal to; this is a rough model, not an exact law
In words: each collection costs about the live data and buys about the headroom, so GC work per allocated byte is live data divided by headroom.
```

Here the total heap doubles, but headroom grows from 0.5 GB to 2 GB: fourfold, so this model predicts four times less work per allocated byte. That is why GC languages often run with heaps two or more times their live data, and why Go exposes the trade-off directly as `GOGC`. Tracing GC buys safety and throughput with memory.

## Key takeaways
- Generational collection relies on workload-dependent survival patterns; promotion and collection terminology vary across runtimes.
- In the simplified nursery model, divide allocation space by allocation rate for the fill time and multiply by survival fraction for copied bytes.
- With fixed live size and dominant tracing cost, more headroom reduces work per allocated byte; roots, sweeping and pacing limit the model.

## Further reading
- [Tracing garbage collection — Wikipedia](https://en.wikipedia.org/wiki/Tracing_garbage_collection)
- [Cheney's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Cheney%27s_algorithm)
- [HotSpot VM garbage collection tuning guide: generations — Oracle](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-collector-implementation.html)
- [The Garbage Collection Handbook (Jones, Hosking, Moss)](https://gchandbook.org/)
- [Boehm-Demers-Weiser conservative garbage collector](https://www.hboehm.info/gc/)
- [Primary verification source 2](https://go.dev/doc/gc-guide)
- [Primary verification source 3](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-garbage-collector-tuning.html)
