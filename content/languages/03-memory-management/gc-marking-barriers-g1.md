---
id: gc-marking-barriers-g1
title: "Marking barriers and G1 regions"
level: advanced
minutes: 4
sourceLesson: gc-modern
summary: "Creating a black-to-white edge and destroying every remaining tracing path can hide a live object without a suitable barrier"
---

Concurrent marking must preserve a route to every object that remains live while application threads change references. The lost-object example motivates barriers; G1 combines such a barrier with region-level pause planning.

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

**Snapshot-at-the-beginning** (SATB), used by G1 and Shenandoah, treats everything reachable when marking began as live. It's conservative: objects that die during marking can remain as floating garbage until a later eligible collection (**floating garbage**). Go uses a **hybrid write barrier** that combines both, introduced in Go 1.8, which removed a stop-the-world stack rescan. The Go team reported substantially shorter pauses for its evaluated workloads; no fixed pause bound follows for an arbitrary program.

## G1: regions and a pause-time goal

G1 ("Garbage-First") became HotSpot's default for server-class configurations in JDK 9 and remains the default on most current configurations; Serial GC is still selected on some configurations. Instead of a few large contiguous generations, it divides the heap into many equal **heap regions** (ergonomically often 1–32 MB; JDK 25 also permits explicitly configured larger sizes). Regions have roles such as eden, survivor, old or free, with special handling for humongous allocations.

```
 +---+---+---+---+---+---+---+---+
 | E | O | S | O | E | F | O | H |
 +---+---+---+---+---+---+---+---+
 E eden  S survivor  O old
 F free  H humongous (big object)
```

- **Young collections** are stop-the-world but parallel. They evacuate (copy) live objects out of eden and survivor regions.
- **Concurrent marking** runs alongside the application once the heap reaches an occupancy threshold, using SATB barriers, and works out how much live data each old region holds.
- **Mixed collections** then evacuate the young regions plus selected old regions predicted to reclaim space efficiently: hence "garbage first". Garbage amount and predicted collection cost both influence selection. Fewer live bytes to copy means more space freed per millisecond of pause.

You give G1 a **pause-time goal** (`-XX:MaxGCPauseMillis`, default 200 ms) and it sizes the young generation and the number of old regions per mixed collection to try to meet it. It's a soft goal, not a guarantee. Objects of half a region or more are **humongous objects** and get their own contiguous regions, which can cause trouble if you allocate many of them.

## Key takeaways
- Creating a black-to-white edge and destroying every remaining tracing path can hide a live object without a suitable barrier.
- Insertion and deletion barriers protect different marking invariants; SATB can retain floating garbage.
- G1 marks concurrently and evacuates selected regions in pauses; its configured pause goal is a planning target, not a bound.

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
