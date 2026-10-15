---
id: gc-go-heap-goals
title: "Go heap goals and soft memory limits"
level: advanced
minutes: 4
sourceLesson: gc-modern
summary: "GOGC controls an allocation allowance based on live heap plus roots; examples that omit roots are simplified sizing models"
---

The standard Go runtime's pacer aims to finish marking by a heap goal. This goal is distinct from the earlier point where concurrent marking starts, and from a hard operating-system or container memory limit.

## GOGC and GOMEMLIMIT



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

With the same 400 MB live heap and the same simplified assumptions, `GOGC=50` gives a 600 MB goal, and `GOGC=200` gives a 1,200 MB goal.

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

`GOMEMLIMIT` (Go 1.19) adds a **soft memory limit**: as Go-runtime-managed memory approaches it, the GC runs more often regardless of `GOGC`. In containers, leave measured headroom below the container limit for memory outside the runtime; a fixed percentage cannot suit every application, and this soft limit cannot guarantee avoidance of an OOM kill. Setting `GOGC=off` disables automatic growth-triggered collection but leaves memory-limit-driven collection enabled; explicit `runtime.GC()` can still request a collection. Beware: if live data really approaches the limit, the GC runs almost continuously (a **death spiral**), so the runtime applies a soft GC CPU limiter targeted at about 50% over its accounting window; it can then exceed the memory limit to keep making application progress.

## Key takeaways
- GOGC controls an allocation allowance based on live heap plus roots; examples that omit roots are simplified sizing models.
- GOMEMLIMIT is a soft limit for Go-runtime-managed memory, with exclusions and possible overshoot.
- When live data approaches a limit, repeated collection can cost CPU without freeing much; measure external memory and leave suitable headroom.

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
