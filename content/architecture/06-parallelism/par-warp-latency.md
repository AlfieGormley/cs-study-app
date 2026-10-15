---
id: par-warp-latency
title: Hiding latency and estimating data in flight
level: intermediate
minutes: 3
sourceLesson: par-gpu
summary: Ready resident warps can issue while other warps wait.
---

## Hiding latency with many warps

Long-latency memory operations need not stall every resident warp. The SM retains execution state for several warps and can issue work from a ready warp while another waits. This avoids an operating-system context switch; it does not make scheduling physically free or guarantee that every cycle has an issuable instruction. Resident-warp limits and issue resources depend on the target.

```
cycle:  1  2  3  4  5  6  7  8
warp 0  ld .  .  .  .  .  .  add
warp 1  .  ld .  .  .  .  .  .
warp 2  .  .  mul mul ld .  .  .
warp 3  .  .  .  .  .  mul mul .
```

How many memory requests must be outstanding to keep the memory system busy? **Little's law**, a result from queueing theory that relates well-defined finite averages in a suitable steady state, answers it: the average amount in the system equals the rate it flows through times the average time each piece spends inside.

```formula
D = R × t_res
D = 10^12 B/s × 400 × 10^-9 s
D = 4 × 10^5 B = 400 KB
where
D: the average number of bytes in flight: requested but not yet delivered, in bytes (B)
R: the byte throughput, in bytes per second (B/s); 1 TB/s = 10^12 B/s in the example
t_res: the average residence time: how long each request is outstanding, in seconds (s); 400 ns = 400 × 10^-9 s
B: byte, 8 bits
s: second
KB: kilobyte, 1,000 bytes
In words: to stream 1 TB/s when each request takes 400 ns to come back, about 400 KB of requests must be in flight at any moment.
```

The law needs a steady state and a consistent definition of bytes and time. More resident warps can expose additional independent requests, but do not guarantee them.

## Key takeaways
- Ready resident warps can issue while other warps wait.
- Little’s law requires steady state and consistent definitions of throughput and residence time.

## Further reading
- [Little’s original queueing-law paper](https://fisherp.scripts.mit.edu/wordpress/wp-content/uploads/2015/11/ContentServer.pdf)
- [CUDA 13.0.3 programming guide](https://docs.nvidia.com/cuda/archive/13.0.3/cuda-c-programming-guide/index.html)
- [CUDA best practices: memory and occupancy](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)
- [NVIDIA warp-level synchronisation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/)
