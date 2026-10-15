---
id: cache-short-amat-cpi-overlap
title: Convert miss costs to processor stalls
level: intermediate
minutes: 4
sourceLesson: cache-arch-write-amat
summary: Add exposed miss stalls to a base CPI that already includes hits.
---

This unit builds on the earlier cache lessons and focuses on convert miss costs to processor stalls. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## From AMAT to CPI

AMAT tells you the cost of one access; what you usually care about is total run time. The "iron law" of processor performance splits run time into three factors:

```formula
T_CPU = N_instr CPI t_cycle
where
T_CPU: the CPU time the program takes, in seconds (s)
N_instr: the number of instructions executed
CPI: cycles per instruction: the average number of clock cycles each instruction takes
t_cycle: the clock period, the length of one cycle, in seconds; 0.25 ns at 4 GHz
In words: run time is how many instructions you execute, times how many cycles each takes on average, times how long a cycle is.
```

Memory stalls make each instruction take more cycles, so for a simple in-order core that blocks on misses they add directly to CPI:

```formula
CPI = CPI_base + r m t_penalty
where
CPI: cycles per instruction including memory stalls
CPI_base: cycles per instruction with a perfect cache, cache-hit cost already included
r: memory references per instruction: how many loads and stores an average instruction makes, e.g. 0.4
m: the miss rate of the cache those references use, a fraction from 0 to 1
t_penalty: the extra cycles each miss costs, in clock cycles
In words: each instruction makes r memory references, a fraction m of them miss, and each miss stalls the core for the penalty.
```

Assume base CPI already includes cache-hit execution cost and that miss penalties cannot overlap. With base CPI 1.0, 0.4 data references per instruction, L1d (level-1 data cache) miss rate 5%, and an L1 miss penalty of 52 cycles (the L2 AMAT above):

```formula
S = r m t_penalty
S = 0.4 × 0.05 × 52 = 1.04 cycles
CPI = CPI_base + S
CPI = 1.0 + 1.04 = 2.04 cycles
where
S: memory stall cycles per instruction
r: data references per instruction, 0.4
m: L1d miss rate, 0.05
t_penalty: L1 miss penalty, 52 cycles
CPI: cycles per instruction, with stalls
CPI_base: cycles per instruction with no misses, 1.0
cycles: clock cycles (per instruction here)
In words: each instruction loses 1.04 cycles to data misses, which roughly doubles CPI from 1.0 to 2.04.
```

About half of all cycles (1.04 of 2.04) are spent waiting for memory. Instruction fetches add a stall term of their own, using one reference per instruction and the L1i (level-1 instruction cache) miss rate, if the L1i misses. The model breaks down once misses overlap: see the first pitfall below.

## Trade-offs and pitfalls

- AMAT is a model for blocking caches. Out-of-order cores keep running independent instructions during a miss and can have many misses outstanding at once (**memory-level parallelism**). Ten overlapped 100-cycle misses do not cost 1,000 cycles. AMAT alone cannot reliably rank such designs or predict total stall time: dependency chains, overlap, bandwidth, and queueing can change the result.
- Average hides the tail. A loop with 99% hits can still be dominated by the 1% if those are DRAM misses.
- Evaluate hit time and miss rate together. In this model L1 lookup time is paid on every access; lower-level costs are weighted by how often accesses reach them. Which change matters most depends on the workload and trade-off.
- Write-allocate can double traffic for streaming writes; use streaming stores or library routines that do.

## Key takeaways
- Add exposed miss stalls to a base CPI that already includes hits.
- Out-of-order overlap, queueing and bandwidth limit what a blocking AMAT model predicts.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
