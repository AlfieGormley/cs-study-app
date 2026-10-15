---
id: gc-concurrent-tradeoffs
title: "Concurrent collection and marking colours"
level: advanced
minutes: 4
sourceLesson: gc-modern
summary: "Parallel describes several GC workers; concurrent describes overlap with application execution"
---

A stop-the-world collector can be simple, but pause duration depends on live data, roots, heap work and hardware. Large full collections can take seconds; heap size alone does not determine a pause. For a trading system, a game or a web service with a 100 ms latency budget, that is unacceptable.

Modern collectors attack the pause by doing most of their work **while the program keeps running**. This unit introduces the marking abstraction. The following units explain barriers and how G1, ZGC and Go implement concurrent collection.

## Three things you can't all maximise

Every collector balances:

- **Latency**: how long the program is paused (worst case and p99).
- **GC throughput**: what fraction of CPU time goes to the application rather than to GC.
- **Memory footprint**: how much extra memory the heap needs beyond the live data.

GC throughput is usually quoted as a percentage of time:

```formula
T = t_app / (t_app + t_gc)
T = 95 s / (95 s + 5 s) = 0.95
where
T: GC throughput: the fraction of CPU time spent running the application, from 0 to 1 (often written as a percentage)
t_app: CPU time spent running application code, in seconds (s)
t_gc: CPU time spent on garbage collection work, including barriers and concurrent GC threads, in seconds
s: seconds
In words: if 5 of every 100 CPU-seconds go to the collector, GC throughput is 95%.
```

Note that a collector can have high GC throughput and still a bad latency: 5% of CPU spent in one 5-second pause every 100 seconds is 95% GC throughput, but any request that arrives during that pause waits up to 5 seconds.

| Collector | Optimises for |
|---|---|
| Parallel (JVM) | GC throughput |
| G1 (common HotSpot default) | balance, pause goal |
| ZGC (JVM) | latency, big heaps |
| Go | latency, simplicity |

Concurrent collectors buy low latency with GC throughput (barriers cost the application CPU) and footprint (garbage piles up while the collector is still running).

> [!note] Terminology
> **Parallel collection** means several GC threads work at once. That work may be stop-the-world or concurrent; the JVM collector named Parallel GC is stop-the-world. **Concurrent collection** means GC threads run *at the same time as* the application. A collector can be both.

## The tri-colour abstraction

To mark concurrently, think of every object as one of three colours:

- **White object**: not yet seen. At the end of marking, white means garbage.
- **Grey object**: seen, but its fields haven't been scanned yet.
- **Black object**: seen, and all its fields scanned.

Marking starts with the roots grey, then repeatedly picks a grey object, greys its white children and turns it black. When no grey objects remain, every white object is unreachable.

```
 [B]black -> [G]grey -> [W]white
 done         to scan    unseen
```

## Key takeaways
- Parallel describes several GC workers; concurrent describes overlap with application execution.
- GC throughput, pause latency and memory footprint are different measurements and must be assessed separately.
- White, grey and black describe unvisited, pending-scan and completed-scan states in the basic marking abstraction.

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
