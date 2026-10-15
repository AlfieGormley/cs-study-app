---
id: gc-zgc-go-architectures
title: "ZGC relocation and Go marking"
level: advanced
minutes: 5
sourceLesson: gc-modern
summary: "Generational ZGC uses load barriers for relocated references and store barriers for additional generational and marking work"
---

Low pauses do not imply identical collector architecture. ZGC relocates heap objects concurrently; the standard Go runtime keeps heap objects in place and concentrates on concurrent marking and sweeping.

## ZGC: concurrent compaction

Concurrent marking alone isn't enough: someone still has to **move** objects to defragment, and moving objects while threads use them is the hard part. G1 does its moving in pauses. **ZGC** does it concurrently.

Its key mechanisms:

- **Coloured pointers.** ZGC stores a few metadata bits inside each 64-bit object reference, recording which GC phase the pointer is "good" for.
- **Load barriers.** Conceptually, relevant heap-reference loads check those bits; the compiler can eliminate redundant barriers. If the pointer is stale (say its object has been relocated), a slow path fixes it, finding or completing the move, and writes the corrected pointer back. Later loads can then take the fast path in that phase; future phases can require more work: the barrier is a **self-healing barrier**.

ZGC is designed for very short pauses that do not scale with heap size; this is a design goal, not a latency guarantee for your service. Generational ZGC arrived in JDK 21, became the default ZGC mode in JDK 23, and the non-generational mode was removed in JDK 24. Generational ZGC uses **store barriers as well as load barriers**; the simplified load-barrier description above explains concurrent relocation, not its entire barrier design.

```
 java -XX:+UseZGC -Xmx64g App
```

The costs include reference-load/store barriers (some checks can be optimized), extra CPU for the concurrent GC threads, and the need for headroom. If the application allocates faster than ZGC can reclaim, threads hit an **allocation stall** and wait, which is a pause by another name. Shenandoah is another concurrent-compaction design; actual pause comparisons require workload measurements.

## Go: concurrent, non-moving, with heap and memory goals

Go's collector is deliberately different. It is a concurrent **tri-colour mark-sweep** collector that is **non-moving** and, **non-generational**, unlike the generational HotSpot collectors discussed here. Go's escape analysis keeps many short-lived values on the stack, which weakens the case for a young generation, and fixed heap-object addresses simplify some runtime interactions. cgo still has strict pointer-passing and pinning rules; a non-moving heap does not make arbitrary Go pointers safe to retain in C.

A Go GC cycle:

1. A brief stop-the-world to turn on the write barrier.
2. Concurrent marking, using about 25% of `GOMAXPROCS` worth of CPU in background workers.
3. **Mark assists**: a goroutine that allocates heavily during marking is made to do some marking itself, so allocation can't outrun the collector.
4. A brief stop-the-world to finish marking.
5. Concurrent sweeping, done bit by bit as memory is reallocated.

The 25% background share in step 2 translates into whole CPUs like this:

```formula
P_bg = 0.25 × GOMAXPROCS
P_bg = 0.25 × 8 = 2
where
P_bg: the number of CPUs' worth of time the background mark workers aim to use during marking
0.25: the Go runtime's background-marking utilisation target, 25%
GOMAXPROCS: the Go setting for how many OS threads may run Go code at once; by default the number of logical CPUs the program may use, and since Go 1.25 the default can account for Linux cgroup CPU bandwidth (rounded up to whole CPUs, generally with a minimum of 2); affinity, compatibility settings and overrides also matter. Here the setting is explicitly 8
In words: with GOMAXPROCS explicitly set to 8, the background-marking utilisation target corresponds to about 2 CPUs of work; available hardware, scheduling and assists affect what the application actually receives.
```

Mark assists come on top of this when the application allocates faster than the background workers can mark.

Go targets short pauses, but no per-workload pause bound is guaranteed; measure pause distributions and assist time.

## Key takeaways
- Generational ZGC uses load barriers for relocated references and store barriers for additional generational and marking work.
- Concurrent work still costs CPU and needs headroom; insufficient reclaimed space can stall an allocating application thread.
- The standard Go collector is concurrent, non-moving and non-generational; its heap policy does not prevent goroutine stacks from moving.

## Further reading
- [HotSpot GC tuning guide: the G1 collector — Oracle](https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector1.html)
- [HotSpot GC tuning guide: the Z collector — Oracle](https://docs.oracle.com/en/java/javase/25/gctuning/z-garbage-collector1.html)
- [JEP 439: Generational ZGC — OpenJDK](https://openjdk.org/jeps/439)
- [A Guide to the Go Garbage Collector — go.dev](https://go.dev/doc/gc-guide)
- [Getting to Go: the journey of Go's garbage collector — go.dev blog](https://go.dev/blog/ismmkeynote)
- [Tri-color marking — Wikipedia](https://en.wikipedia.org/wiki/Tracing_garbage_collection#Tri-color_marking)
- [Primary verification source 2](https://go.dev/src/runtime/mbarrier.go)
- [Primary verification source 4](https://docs.oracle.com/en/java/javase/25/gctuning/garbage-first-g1-garbage-collector1.html)
- [Primary verification source 6](https://docs.oracle.com/en/java/javase/24/migrate/significant-changes-jdk-24.html)
- [Primary verification source 7](https://inside.java/2023/11/28/gen-zgc-explainer/)
- [Primary verification source 8](https://inside.java/2024/05/07/jep474-targeted-to-jdk23/)
