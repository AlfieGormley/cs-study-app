---
id: pipe-out-of-order-window-and-hardware-cost
sourceLesson: pipe-out-of-order
title: Size the window and account for complexity
level: advanced
minutes: 4
summary: Estimate allocation capacity during a blocked retirement interval and recognise the limits of wider execution.
---

In the preceding recovery unit, the reorder buffer retired oldest first. If its oldest instruction waits, younger completed instructions still occupy entries. This unit sizes a hypothetical allocation window and considers other bottlenecks. The numbers are teaching assumptions, not measured commercial ROB sizes.

## How big is the window?

> [!note] Product data omitted
> Exact commercial decode widths and ROB sizes are omitted because sufficiently reliable, consistently defined primary-source figures were not established here. Instruction counts, µop counts and ROB entries are not interchangeable.

While a load at the head of the reorder buffer waits for memory, nothing behind it can retire, but the CPU front end keeps allocating new entries. How many entries would it take to keep allocating for the whole wait? Convert the miss time to cycles, then multiply by the allocation rate. For a hypothetical 80 ns miss at 4 GHz:

```formula
L = t_miss f
L = 80 ns × 4 GHz = 320
E = Lw
E = 320 × 4 = 1280
where
L: the miss latency counted in clock cycles
t_miss: the miss latency in time, 80 nanoseconds (ns) here
f: the clock frequency, 4 gigahertz (GHz) here
ns: nanoseconds, 10^-9 seconds
GHz: gigahertz, 10^9 cycles per second, so 80 ns × 4 GHz = 80 × 10^-9 × 4 × 10^9 = 320
E: the number of reorder-buffer entries needed to keep allocating until the load returns
w: the allocation width: new entries allocated per cycle, 4 here
In words: an 80 ns miss lasts 320 cycles at 4 GHz, and allocating four entries every one of those cycles needs about 1,280 free entries.
```

So maintaining allocation at four entries per cycle while retirement is blocked would require space for roughly 1,280 entries. This estimates how many entries would be occupied, assuming sufficient independent work and no earlier resource limit. It does not prove all real misses stall for a fixed duration. A larger window may discover independent memory accesses whose latencies overlap (**memory-level parallelism**); bandwidth and other queues still limit progress.

## Why not let the compiler do it?

**VLIW** (very long instruction word) designs expose operation grouping to the compiler, shifting much scheduling work from hardware to software. Variable memory latency makes static scheduling harder. Intel Itanium used **EPIC**, an explicitly parallel design with bundles, instruction groups, predication and speculation; it should not be reduced to a simple VLIW machine with no means to tolerate uncertain execution. A single-cause explanation of its commercial outcome is omitted because this lesson has not established evidence for one.

## The costs

- **Area and power.** Rename tables, schedulers that compare every result tag with every waiting operand each cycle (wakeup and select), and large multi-ported register files are expensive. Scheduler logic scales badly with width.
- **Diminishing returns.** Dependence chains, branch recovery, fetch limits and memory behaviour can leave issue capacity unused; achievable IPC is workload- and core-dependent.
- **Mispredictions cost more.** More speculative capacity can allow more wrong-path work, but does not by itself fix the recovery latency or amount discarded.

These costs are part of why performance per core stopped growing fast enough, helping motivate the multicore and power-budget units that follow.

## Key takeaways
- Convert latency to cycles before multiplying by an entry-allocation rate.
- Free entries alone do not guarantee independent work, memory bandwidth or available queue space.
- Static and dynamic scheduling trade hardware complexity against information available at run time.

## Further reading
- [BOOM implementation: pipeline](https://docs.boom-core.org/en/latest/sections/intro-overview/boom-pipeline.html)
- [BOOM implementation: reorder buffer](https://docs.boom-core.org/en/latest/sections/reorder-buffer.html)
- [BOOM implementation: rename stage](https://docs.boom-core.org/en/latest/sections/rename-stage.html)
- [BOOM implementation: load/store unit](https://docs.boom-core.org/en/latest/sections/load-store-unit.html)

- [Fisher: original VLIW paper](https://people.eecs.berkeley.edu/~kubitron/courses/cs252-F00/handouts/papers/p263-fisher.pdf)
- [Intel Itanium architecture manual: predication and speculation](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/itanium-architecture-software-developer-rev-2-3-vol-1-manual.pdf)
