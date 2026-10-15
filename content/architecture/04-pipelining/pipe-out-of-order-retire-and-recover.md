---
id: pipe-out-of-order-retire-and-recover
sourceLesson: pipe-out-of-order
title: Retire precisely and recover memory ordering
level: advanced
minutes: 3
summary: Explain reorder-buffer commitment, branch squashing, store visibility and speculative loads.
---

The earlier out-of-order units used ready-instruction scheduling and register versions. This unit adds recovery: completed speculative results are not yet an irrevocable architectural update. The circular reorder-buffer and squash behaviour below is a teaching organisation; real cores choose their entry granularity and recovery details.

## The reorder buffer

A **reorder buffer**, discussed by Smith and Pleszkun in their work on precise interrupts, is one solution. In this teaching model it is a circular queue with one entry per in-flight instruction, in program order. Real entry granularity can differ. Checkpointing and other bookkeeping are also needed for speculative recovery.

- Instructions execute out of order and write results into their ROB entry (or a physical register), not the architectural state.
- The head of the ROB **retires** (commits) only when it has completed. Retirement is in order, up to the supported retirement width per cycle.
- If the head instruction faulted, the core discards it and every younger entry, and the exception appears exactly at that instruction: **precise exceptions**.
- If a branch turns out mispredicted, the core performs a **pipeline flush**, discarding every younger entry. The rename table is restored to the state it had at the branch, and fetch restarts on the right path.

This is what makes **speculative execution** safe, architecturally: wrong-path instructions execute, but never commit. But "never commits" is not the same as "leaves no trace": some microarchitectural effects, such as cache state, may persist, and recovery of predictor history is implementation-dependent. The Spectre and Meltdown vulnerabilities exploited exactly such leftover traces.

### Memory ordering

Loads and stores need extra care, because whether two of them conflict depends on addresses that aren't known until they execute.

- Ordinary cacheable stores retain speculative data in a store queue or buffer until it is safe to commit. Squashing a store must not make its data architecturally visible; related address translation or ownership requests can still affect microarchitectural state.
- A load may forward bytes from the youngest matching older store when address, data and coverage requirements permit. Partial overlaps or unavailable data can require stalling or replay.
- A core may let a load pass older stores with unknown addresses (**memory disambiguation**). If required ordering was violated, recovery re-executes affected work; a pipeline squash starting from the load is one implementation, not a universal mechanism.

## Key takeaways
- In-order retirement supports precise architectural exceptions while execution remains out of order.
- Wrong-path results must not commit, although microarchitectural traces can remain.
- Loads passing unknown older stores require checking for conflicts and replaying affected work.

## Further reading
- [BOOM implementation: reorder buffer](https://docs.boom-core.org/en/latest/sections/reorder-buffer.html)
- [BOOM implementation: load/store unit](https://docs.boom-core.org/en/latest/sections/load-store-unit.html)
- [Smith and Pleszkun: precise interrupts (original paper)](https://american.cs.ucdavis.edu/academic/readings/papers/smithpleszkun.pdf)
- [Spectre: original research paper](https://spectreattack.com/spectre.pdf)
