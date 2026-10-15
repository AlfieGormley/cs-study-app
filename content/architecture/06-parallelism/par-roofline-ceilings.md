---
id: par-roofline-ceilings
title: Arithmetic intensity and the roofline ridge
level: advanced
minutes: 3
sourceLesson: par-measuring
summary: Roofline compares consistently defined arithmetic and bandwidth ceilings.
---

## Level 3: the roofline model

Counters say what the hardware did. They do not say how far you are from what it *could* do. For that, Samuel Williams, Andrew Waterman and David Patterson proposed the **roofline model** (2009).

### Arithmetic intensity

The key property of a compute kernel is its **arithmetic intensity** (AI): floating-point operations performed per byte moved to or from main memory.

```formula
AI = F / D
where
AI: arithmetic intensity, in FLOPs per byte (FLOP/byte)
F: the number of floating-point operations (FLOPs) the compute kernel performs
D: the number of bytes the compute kernel moves to or from main memory (DRAM)
In words: intensity is how much arithmetic a compute kernel does for every byte it has to fetch or store.
```

A machine has two limits: its peak compute rate and its memory bandwidth. A compute kernel can go no faster than either allows. Bandwidth times intensity is the FLOP rate the memory system can feed:

```formula
P_att = min(P, AI × B)
where
P_att: attainable performance: the most FLOPs per second the compute kernel can reach on this machine, in GFLOP/s
P: the machine's peak compute rate, in GFLOP/s (10^9 FLOPs per second)
AI: the compute kernel's arithmetic intensity, in FLOP/byte
B: the machine's memory bandwidth, in GB/s (10^9 bytes per second)
min: the smaller of its two inputs
In words: a compute kernel is capped either by how fast the chip can do arithmetic or by how fast memory can deliver the bytes that arithmetic needs, whichever is lower.
```

Plotted on log–log axes, that is a sloped line (bandwidth-limited) meeting a flat line (compute-limited): a roof.

For example, on a machine with a 1,000 GFLOP/s peak and 100 GB/s of bandwidth:

| AI (FLOP/byte) | Bandwidth ceiling (GFLOP/s) | Combined roof (GFLOP/s) |
|---|---|---|
| 0.01 | 1 | 1 |
| 0.1 | 10 | 10 |
| 1 | 100 | 100 |
| 10 | 1,000 | 1,000 |
| 100 | 10,000 | 1,000 |

The corner is the **ridge point**: the intensity at which the two ceilings meet.

```formula
AI_r = P / B
AI_r = 1,000 GFLOP/s / (100 GB/s)
AI_r = 10 FLOP/byte
where
AI_r: the ridge-point intensity, in FLOP/byte
P: peak compute rate; 1,000 GFLOP/s here
B: memory bandwidth; 100 GB/s here
GFLOP/s: 10^9 floating-point operations per second
GB/s: gigabytes per second, 10^9 bytes per second
FLOP: one floating-point operation
byte: 8 bits
In words: this machine needs at least 10 FLOPs per byte fetched before memory stops being the limit.
```

To its left, bandwidth is the lower of these two ceilings; to its right, arithmetic throughput is lower. At the ridge they are equal. An actual compute kernel may run below both because of dependencies, latency, limited concurrency or other resource ceilings. Position alone does not prove its observed bottleneck.

## Key takeaways
- Roofline compares consistently defined arithmetic and bandwidth ceilings.
- Being below one roof does not prove the actual cause of a slow run.

## Further reading
- [The original Roofline paper](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
- [Python timeit measurement contract](https://docs.python.org/3/library/timeit.html)
- [Linux perf stat reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-stat.txt)
- [Linux perf record reference](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt)
- [Flame graphs from their creator](https://www.brendangregg.com/flamegraphs.html)
- [STREAM traffic conventions](https://www.cs.virginia.edu/stream/ref.html)
- [Python Linux perf integration](https://docs.python.org/3/howto/perf_profiling.html)
