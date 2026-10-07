---
id: gc-modern
title: "Modern GCs: G1, ZGC, Go and pause times"
level: advanced
minutes: 15
summary: How production collectors shrink pauses by working concurrently with the program, the tri-colour invariant and the barriers that protect it, and how Java's G1 and ZGC and Go's collector make different trade-offs between latency, throughput and memory.
---

A stop-the-world collector can be simple, but pause duration depends on live data, roots, heap work and hardware. Large full collections can take seconds; heap size alone does not determine a pause. For a trading system, a game or a web service with a 100 ms latency budget, that is unacceptable.

Modern collectors attack the pause by doing most of their work **while the program keeps running**. This lesson explains the core trick that makes that safe, then looks at how three real collectors use it.

## Three things you can't all maximise

Every collector balances:

- **Latency**: how long the program is paused (worst case and p99).
- **Throughput**: what fraction of CPU time goes to the application rather than to GC.
- **Footprint**: how much extra memory the heap needs beyond the live data.

| Collector | Optimises for |
|---|---|
| Parallel (JVM) | throughput |
| G1 (JVM default) | balance, pause goal |
| ZGC (JVM) | latency, big heaps |
| Go | latency, simplicity |

Concurrent collectors buy low latency with throughput (barriers cost the application CPU) and footprint (garbage piles up while the collector is still running).

> [!note] Terminology
> **Parallel** means several GC threads work at once. That work may be stop-the-world or concurrent; the JVM collector named Parallel GC is stop-the-world. **Concurrent** means GC threads run *at the same time as* the application. A collector can be both.

## The tri-colour abstraction

To mark concurrently, think of every object as one of three colours:

- **White**: not yet seen. At the end of marking, white means garbage.
- **Grey**: seen, but its fields haven't been scanned yet.
- **Black**: seen, and all its fields scanned.

Marking starts with the roots grey, then repeatedly picks a grey object, greys its white children and turns it black. When no grey objects remain, every white object is unreachable.

```
 [B]black -> [G]grey -> [W]white
 done         to scan    unseen
```

## The lost-object problem

Now let the program (the **mutator**, in GC jargon) run during marking. Suppose:

1. Black object `A` is already scanned.
2. The mutator stores a pointer to white object `C` into `A`.
3. The mutator then deletes the only other path to `C`, from grey object `B`.

```
 before:  A(black)   B(grey) --> C(white)
 step 2:  A(black) --> C <-- B(grey)
 step 3:  A(black) --> C      B(grey)
```

The collector will never rescan `A` (it's black) and can no longer reach `C` through `B`. `C` stays white and is **freed while live**. That is a memory-safety bug, not a performance problem.

The object is lost only if **both** things happen: a black-to-white pointer is created, **and** every grey path to the white object is removed. A barrier prevents one or the other:

| Barrier | On pointer write... |
|---|---|
| Insertion (Dijkstra) | shade the new target grey |
| Deletion / SATB (Yuasa) | shade the old target grey |

**Snapshot-at-the-beginning** (SATB), used by G1 and Shenandoah, treats everything reachable when marking began as live. It's conservative: objects that die during marking survive until the next cycle (**floating garbage**). Go uses a **hybrid** of both barriers, introduced in Go 1.8, which let it drop a stop-the-world stack rescan and cut typical pauses well below a millisecond.

## G1: regions and a pause-time goal

G1 ("Garbage-First") has been HotSpot's default collector since JDK 9. Instead of a few large contiguous generations, it divides the heap into many equal **regions** (ergonomically often 1–32 MB; JDK 25 also permits explicitly configured larger sizes). Regions have roles such as eden, survivor, old or free, with special handling for humongous allocations.

```
 +---+---+---+---+---+---+---+---+
 | E | O | S | O | E | F | O | H |
 +---+---+---+---+---+---+---+---+
 E eden  S survivor  O old
 F free  H humongous (big object)
```

- **Young collections** are stop-the-world but parallel. They evacuate (copy) live objects out of eden and survivor regions.
- **Concurrent marking** runs alongside the application once the heap reaches an occupancy threshold, using SATB barriers, and works out how much live data each old region holds.
- **Mixed collections** then evacuate the young regions plus the old regions with the **most garbage**: hence "garbage first". Fewer live bytes to copy means more space freed per millisecond of pause.

You give G1 a **pause-time goal** (`-XX:MaxGCPauseMillis`, default 200 ms) and it sizes the young generation and the number of old regions per mixed collection to try to meet it. It's a soft goal, not a guarantee. Objects of half a region or more are **humongous** and get their own contiguous regions, which can cause trouble if you allocate many of them.

## ZGC: concurrent compaction

Concurrent marking alone isn't enough: someone still has to **move** objects to defragment, and moving objects while threads use them is the hard part. G1 does its moving in pauses. **ZGC** does it concurrently.

Its key mechanisms:

- **Coloured pointers.** ZGC stores a few metadata bits inside each 64-bit object reference, recording which GC phase the pointer is "good" for.
- **Load barriers.** Every time the application loads a reference from the heap, a short check tests those bits. If the pointer is stale (say its object has been relocated), a slow path fixes it, finding or completing the move, and writes the corrected pointer back. The next load of that field takes the fast path: the barrier is **self-healing**.

ZGC is designed for very short pauses that do not scale with heap size; this is a design goal, not a latency guarantee for your service. Generational ZGC arrived in JDK 21, became the default ZGC mode in JDK 23, and the non-generational mode was removed in JDK 24. Generational ZGC uses **store barriers as well as load barriers**; the simplified load-barrier description above explains concurrent relocation, not its entire barrier design.

```
 java -XX:+UseZGC -Xmx64g App
```

The costs include reference-load/store barriers (some checks can be optimized), extra CPU for the concurrent GC threads, and the need for headroom. If the application allocates faster than ZGC can reclaim, threads hit an **allocation stall** and wait, which is a pause by another name. Shenandoah is another concurrent-compaction design; actual pause comparisons require workload measurements.

## Go: concurrent, non-moving, with heap and memory goals

Go's collector is deliberately different. It is a concurrent **tri-colour mark-sweep** collector that is **non-moving** and, unlike the JVM collectors, **non-generational**. Go's escape analysis keeps many short-lived values on the stack (lesson 1), which weakens the case for a young generation, and not moving objects keeps interior pointers and cgo simple.

A Go GC cycle:

1. A brief stop-the-world to turn on the write barrier.
2. Concurrent marking, using about 25% of `GOMAXPROCS` worth of CPU in background workers.
3. **Mark assists**: a goroutine that allocates heavily during marking is made to do some marking itself, so allocation can't outrun the collector.
4. A brief stop-the-world to finish marking.
5. Concurrent sweeping, done lazily as memory is reallocated.

Go targets short pauses, but no per-workload pause bound is guaranteed; measure pause distributions and assist time.

### GOGC and GOMEMLIMIT

You tune Go's GC mostly with `GOGC` (default 100). Ignoring roots for a moment, `GOGC` sets a heap-size **goal** based on growth since the last live-heap measurement. The pacer starts collection before reaching that goal so concurrent marking has time to finish:

```
 target = live + live x GOGC/100

 live 400 MB, GOGC=100 -> 800 MB
 live 400 MB, GOGC=50  -> 600 MB
 live 400 MB, GOGC=200 -> 1200 MB
```

(Since Go 1.18 the formula is live heap + (live heap + GC roots) × GOGC/100; roots include scannable stacks and globals. The examples above neglect roots.) In the guide’s steady-state model, changing GOGC adjusts the allocation allowance and the dominant GC frequency/cost. Roots, memory limits, changing liveness and fixed costs can alter the simple inverse relationship.

`GOMEMLIMIT` (Go 1.19) adds a **soft memory limit**: as Go-runtime-managed memory approaches it, the GC runs more often regardless of `GOGC`. In containers, leave measured headroom below the container limit for memory outside the runtime; a fixed percentage cannot suit every application, and this soft limit cannot guarantee avoidance of an OOM kill. Setting `GOGC=off` disables automatic growth-triggered collection but leaves memory-limit-driven collection enabled; explicit `runtime.GC()` can still request a collection. Beware: if live data really approaches the limit, the GC runs almost continuously (a **death spiral**), so Go caps GC CPU at about 50% in that situation.

## Pauses and tail latency

Averages hide GC pauses; percentiles expose them.

> [!example] A pause in the p99
> Assume requests otherwise take a fixed 5 ms, arrivals are uniform, a 150 ms pause starts every 5 s, and ignore in-flight requests and post-pause queueing. Then 3% arrive during the pause and wait 0–150 ms extra. In this simplified model p99 is 105 ms: the upper 1% corresponds to waits above 100 ms. Real queueing can add delay.

A fan-out that waits for all 100 backends sees the slowest response. If each independently has a 1% chance of a slow response, at least one is slow with probability 1 − 0.99^100, about 63.4%. Correlation, hedging and partial-result policies change this. This is why low-latency collectors matter so much for microservices.

## Choosing and tuning

- **Measure first.** Turn on GC logs (`-Xlog:gc*` in Java, `GODEBUG=gctrace=1` in Go) and find out whether pauses or CPU are the problem.
- **Reduce allocation.** The cheapest GC work is the work you don't create: reuse buffers, avoid boxing, use `sync.Pool` in Go for hot temporary objects.
- **Give it headroom.** Insufficient headroom is one cause of GC pressure; logs may instead reveal root scanning, allocation churn or scheduling problems.
- **Pick the collector by goal.** Batch jobs: Parallel GC for throughput. General services: G1. Large heaps with strict latency SLOs: ZGC or Shenandoah.
- **Don't over-tune.** Modern collectors are adaptive; dozens of flags copied from an old blog post often make things worse.

## Key takeaways
- Low-pause collectors do most of their work concurrently with the application, trading throughput and memory for latency.
- Creating a black-to-white edge breaks the strong tri-colour invariant. Losing all remaining tracing paths as well can hide a live object; insertion and deletion barriers prevent that lost-object scenario by different invariants.
- G1 splits the heap into regions, marks concurrently, and evacuates the regions with the most garbage to meet a soft pause goal.
- ZGC relocates objects concurrently using coloured pointers and self-healing load barriers, targeting very short pauses without guaranteeing a particular application latency.
- Go uses a concurrent, non-moving, non-generational mark-sweep collector tuned by `GOGC` and `GOMEMLIMIT`.
- GC pauses affect both averages and tail latency, but high percentiles expose their tail effect more clearly, and fan-out multiplies their impact.

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
