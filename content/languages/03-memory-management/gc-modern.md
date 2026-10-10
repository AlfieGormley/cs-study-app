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
- **Memory footprint**: how much extra memory the heap needs beyond the live data.

GC throughput is usually quoted as a percentage of time:

```formula
T = t_app / (t_app + t_gc)
T = 95 s / (95 s + 5 s) = 0.95
where
T: throughput: the fraction of CPU time spent running the application, from 0 to 1 (often written as a percentage)
t_app: CPU time spent running application code, in seconds (s)
t_gc: CPU time spent on garbage collection work, including barriers and concurrent GC threads, in seconds
s: seconds
In words: if 5 of every 100 CPU-seconds go to the collector, throughput is 95%.
```

Note that a collector can have high throughput and still a bad latency: 5% of CPU spent in one 5-second pause every 100 seconds is 95% throughput, but any request that arrives during that pause waits up to 5 seconds.

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

**Snapshot-at-the-beginning** (SATB), used by G1 and Shenandoah, treats everything reachable when marking began as live. It's conservative: objects that die during marking survive until the next cycle (**floating garbage**). Go uses a **hybrid write barrier** that combines both, introduced in Go 1.8, which let it drop a stop-the-world stack rescan and cut typical pauses well below a millisecond.

## G1: regions and a pause-time goal

G1 ("Garbage-First") has been HotSpot's default collector since JDK 9. Instead of a few large contiguous generations, it divides the heap into many equal **heap regions** (ergonomically often 1–32 MB; JDK 25 also permits explicitly configured larger sizes). Regions have roles such as eden, survivor, old or free, with special handling for humongous allocations.

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

You give G1 a **pause-time goal** (`-XX:MaxGCPauseMillis`, default 200 ms) and it sizes the young generation and the number of old regions per mixed collection to try to meet it. It's a soft goal, not a guarantee. Objects of half a region or more are **humongous objects** and get their own contiguous regions, which can cause trouble if you allocate many of them.

## ZGC: concurrent compaction

Concurrent marking alone isn't enough: someone still has to **move** objects to defragment, and moving objects while threads use them is the hard part. G1 does its moving in pauses. **ZGC** does it concurrently.

Its key mechanisms:

- **Coloured pointers.** ZGC stores a few metadata bits inside each 64-bit object reference, recording which GC phase the pointer is "good" for.
- **Load barriers.** Every time the application loads a reference from the heap, a short check tests those bits. If the pointer is stale (say its object has been relocated), a slow path fixes it, finding or completing the move, and writes the corrected pointer back. The next load of that field takes the fast path: the barrier is a **self-healing barrier**.

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
5. Concurrent sweeping, done bit by bit as memory is reallocated.

The 25% background share in step 2 translates into whole CPUs like this:

```formula
P_bg = 0.25 × GOMAXPROCS
P_bg = 0.25 × 8 = 2
where
P_bg: the number of CPUs' worth of time the background mark workers aim to use during marking
0.25: the Go runtime's background-marking utilisation target, 25%
GOMAXPROCS: the Go setting for how many OS threads may run Go code at once; by default the number of logical CPUs the program may use, and since Go 1.25 on Linux no more than a container's CPU limit (8 in this example)
In words: on an 8-core machine, background marking aims to use about 2 cores, leaving about 6 for the application, before any mark assists.
```

Mark assists come on top of this when the application allocates faster than the background workers can mark.

Go targets short pauses, but no per-workload pause bound is guaranteed; measure pause distributions and assist time.

### GOGC and GOMEMLIMIT

You tune Go's GC mostly with `GOGC` (default 100). Ignoring roots for a moment, `GOGC` sets a **heap-size goal** based on growth since the last live-heap measurement. The GC pacer starts collection before reaching that goal so concurrent marking has time to finish:

```formula
H_goal = L + L × GOGC / 100
H_goal = 400 MB + 400 MB × 100 / 100
H_goal = 800 MB
where
H_goal: the heap-size goal: how big the heap may grow before this GC cycle should finish, in megabytes (MB)
L: the live heap measured at the end of the previous GC cycle, in MB
GOGC: the Go tuning setting, a percentage; default 100, meaning "let the heap grow by 100% of the live heap"
100: converts the GOGC percentage into a fraction (100% = 1)
MB: megabyte, 1,000,000 bytes
In words: the heap may grow by GOGC percent of the live data before the next collection should be done.
```

With the same 400 MB live heap, `GOGC=50` gives 400 MB + 200 MB = 600 MB, and `GOGC=200` gives 400 MB + 800 MB = 1,200 MB.

Since Go 1.18 the roots count too:

```formula
H_goal = L + (L + R) × GOGC / 100
H_goal = 400 MB + 420 MB × 100 / 100
H_goal = 820 MB
where
H_goal: the heap-size goal, in megabytes (MB)
L: the live heap from the previous cycle, in MB
R: the GC roots the collector must scan: goroutine stacks and global variables, in MB (20 MB here, an illustrative figure)
GOGC: the Go tuning percentage, default 100
100: converts the percentage into a fraction
MB: megabyte, 1,000,000 bytes
In words: the allowance for new allocation is GOGC percent of the live heap plus the roots, so a program with large stacks or globals gets a slightly bigger goal.
```

The 400 MB examples above neglect roots. In the guide’s steady model (constant live heap and allocation rate), changing GOGC adjusts the allocation allowance and the dominant GC frequency/cost. Roots, memory limits, changing liveness and fixed costs can alter the simple inverse relationship.

`GOMEMLIMIT` (Go 1.19) adds a **soft memory limit**: as Go-runtime-managed memory approaches it, the GC runs more often regardless of `GOGC`. In containers, leave measured headroom below the container limit for memory outside the runtime; a fixed percentage cannot suit every application, and this soft limit cannot guarantee avoidance of an OOM kill. Setting `GOGC=off` disables automatic growth-triggered collection but leaves memory-limit-driven collection enabled; explicit `runtime.GC()` can still request a collection. Beware: if live data really approaches the limit, the GC runs almost continuously (a **death spiral**), so Go caps GC CPU at about 50% in that situation.

## Pauses and tail latency

Averages hide GC pauses; percentiles expose them.

> [!example] A pause in the p99
> Assume requests otherwise take a fixed 5 ms, arrivals are uniform, a 150 ms pause starts every 5 s, and ignore requests already in progress and post-pause queueing. Then 3% arrive during the pause and wait 0–150 ms extra. In this simplified model p99 is 105 ms: the upper 1% corresponds to waits above 100 ms. Real queueing can add delay.

The p99 (99th percentile) is the latency that 99% of requests beat. Here is how the 105 ms comes out:

```formula
f = t_p / t_c = 150 ms / 5000 ms = 0.03
w = t_p × (1 − 0.01 / f)
w = 150 ms × (1 − 0.01 / 0.03) = 100 ms
p99 = t_r + w = 5 ms + 100 ms = 105 ms
where
f: the fraction of requests that arrive during a pause
t_p: the pause length, 150 milliseconds (ms)
t_c: the time from one pause start to the next, 5 s = 5000 ms
0.01: the slowest 1% of all requests, the part above the 99th percentile
w: the extra wait at the p99 boundary; delayed requests wait anywhere from 0 to t_p, evenly spread, and the slowest 0.01 / f of them (one third here) wait more than w
p99: the 99th-percentile latency: 99% of requests finish faster than this
t_r: the normal request time without a pause, 5 ms
ms: milliseconds, thousandths of a second
In words: 3% of requests hit the pause; the slowest third of those, 1% of all requests, wait more than 100 ms, so p99 is 5 + 100 = 105 ms.
```

The model only works when the fraction hitting a pause is above 1% (otherwise the p99 never sees the pause at all, though p99.9 might). The median is still 5 ms, which is why averages and medians hide GC pauses.

A fan-out that waits for all 100 backends sees the slowest response. If each independently has a 1% chance of a slow response, the chance that at least one is slow is:

```formula
P = 1 − (1 − p)^n
P = 1 − 0.99^100 ≈ 1 − 0.366 = 0.634
where
P: the probability that at least one of the n backends responds slowly
p: the probability that any one backend is slow, 1% = 0.01
n: the number of backends the request waits for, 100 here
(1 − p)^n: the chance that all n are fast: (1 − p) multiplied by itself n times
≈: approximately equal to (rounded)
In words: with 100 backends each slow 1% of the time, about 63% of fan-out requests wait for at least one slow response.
```

So a 1-in-100 event on each backend becomes the common case for the whole request. Correlation, hedging and partial-result policies change this. This is why low-latency collectors matter so much for microservices.

## Choosing and tuning

- **Measure first.** Turn on GC logs (`-Xlog:gc*` in Java, `GODEBUG=gctrace=1` in Go) and find out whether pauses or CPU are the problem.
- **Reduce allocation.** The cheapest GC work is the work you don't create: reuse scratch memory, avoid autoboxing, use `sync.Pool` in Go for hot temporary objects.
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
