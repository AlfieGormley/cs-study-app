---
id: tcp-reno-large-path-recovery
sourceLesson: tcp-congestion
title: Reno recovery on a large-delay path
level: advanced
minutes: 3
summary: Why one-segment-per-round-trip growth cannot refill the huge windows of fast, long-distance paths.
---

## Why Reno fails on fast, long paths

Additive increase is one segment per RTT, no matter how big the window. After a halving, the time to climb back is therefore proportional to both the window size and the round trip:

```formula reference
T_rec = (W / 2) × RTT
where
T_rec: the time to grow from half the window back to the full window at one segment per round trip, in seconds (s)
W: the full congestion window before the loss, in segments
RTT: round-trip time, in seconds (s)
s: seconds
In words: Reno regains one segment per round trip, so winning back half a window takes half a window's worth of round trips; a path that needs a huge window takes a very long time to recover.
```

Consider a model counting 1,500 payload bytes per segment, ignoring headers, at 10 Gbit/s and 100 ms RTT. Filling that path takes about 83,333 segments in flight. After one loss halves the window, getting back takes about 41,667 round trips of 100 ms: **over an hour**, during which a single further loss starts the climb again. RFC 3649 puts the same problem the other way round: to *sustain* that average rate, Reno could tolerate at most one congestion event every 5,000,000,000 packets, roughly one every 1⅔ hours ([RFC 3649](https://www.rfc-editor.org/rfc/rfc3649)). This illustrates Reno's scaling limitation under the stated assumptions, not an absolute impossibility for every high-speed path or workload.

So on a **long fat pipe**, loss-driven Reno spends most of its time far below capacity, even when losses are rare by everyday standards. That is the motivation for CUBIC (next lesson), which regrows its window by elapsed time rather than one segment per round trip.

## Key takeaways

- Large bandwidth-delay products need large in-flight windows.
- One-segment-per-RTT Reno growth can take over an hour to undo one halving in the stated 10 Gbit/s model, so occasional losses keep it far below capacity.
- This comparison is a scaling illustration rather than a universal performance prediction.

## Further reading

- [RFC 5681: TCP Congestion Control](https://www.rfc-editor.org/rfc/rfc5681)
- [RFC 9438: CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438)
