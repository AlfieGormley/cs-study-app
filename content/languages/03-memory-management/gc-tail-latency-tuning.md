---
id: gc-tail-latency-tuning
title: "Pause percentiles, fan-out and tuning"
level: advanced
minutes: 5
sourceLesson: gc-modern
summary: "Under uniform arrivals and the stated no-queueing assumptions, only requests arriving during a pause receive its residual waiting time"
---

A low average does not describe how the slowest requests feel. Explicit pause and fan-out models make their assumptions visible, while measurements tell you whether the model resembles your service.

## Pauses and tail latency

Averages hide GC pauses; percentiles expose them.

> [!example] A pause in the p99
> Assume requests otherwise take a fixed 5 ms, arrivals are uniform, a 150 ms pause starts every 5 s, and ignore requests already in progress and post-pause queueing. Then 3% arrive during the pause and wait 0–150 ms extra. In this simplified model p99 is 105 ms: the upper 1% corresponds to waits above 100 ms. Real queueing can add delay.

The p99 (99th percentile) is a latency boundary at or below which 99% of requests fall; ties and finite-sample conventions matter. Here is how the 105 ms comes out:

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

The model only works when the fraction hitting a pause is above 1% (otherwise the p99 never sees the pause at all, though p99.9 might). The median is still 5 ms, so a median or average alone can obscure the tail effect even though a pause can change the mean.

A fan-out that waits for all 100 backends sees the slowest response. If each independently has a 1% chance of a slow response, the chance that at least one is slow is:

```formula
P = 1 − (1 − p)^n
P = 1 − 0.99^100 ≈ 1 − 0.366 = 0.634
where
P: the probability that at least one of the n backends responds slowly
p: the probability that any one backend is slow, 1% = 0.01
n: the number of backends the request waits for, 100 here
(1 − p)^n: the chance that all n are fast: n copies of (1 − p) multiplied together
≈: approximately equal to (rounded)
In words: with 100 backends each slow 1% of the time, about 63% of fan-out requests wait for at least one slow response.
```

So a 1-in-100 event on each backend becomes the common case for the whole request. Correlation, hedging and partial-result policies change this. This is why low-latency collectors matter so much for microservices.

## Choosing and tuning

- **Measure first.** Turn on GC logs (`-Xlog:gc*` in Java, `GODEBUG=gctrace=1` in Go) and find out whether pauses or CPU are the problem.
- **Reduce allocation.** The cheapest GC work is the work you don't create: reuse scratch memory, avoid autoboxing, use `sync.Pool` in Go for hot temporary objects.
- **Give it headroom.** Insufficient headroom is one cause of GC pressure; logs may instead reveal root scanning, allocation churn or scheduling problems.
- **Test collector candidates by goal.** Parallel GC is a throughput candidate for batch work; G1 is a general-service baseline; ZGC or Shenandoah are latency candidates for large heaps. Measure the full application before choosing.
- **Don't over-tune.** Modern collectors are adaptive; dozens of flags copied from an old blog post often make things worse.

## Key takeaways
- Under uniform arrivals and the stated no-queueing assumptions, only requests arriving during a pause receive its residual waiting time.
- Independent slow-backend probabilities compound in all-results fan-out; correlation and early-result policies change the model.
- Choose and tune collectors from measured pause, CPU, allocation and memory data rather than assuming a universal best collector.

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
