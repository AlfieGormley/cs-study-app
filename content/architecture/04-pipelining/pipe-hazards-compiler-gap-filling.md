---
id: pipe-hazards-compiler-gap-filling
sourceLesson: pipe-hazards
title: Schedule independent work around a load
level: intermediate
minutes: 3
summary: Reorder a straight-line sequence without changing its values or observable memory behaviour.
---

Continue with a five-stage, single-issue, cache-hit teaching pipeline. ALU-to-ALU forwarding needs no stall; a load immediately followed by an EX consumer needs one. Scheduling fills that gap with useful independent work rather than changing the hardware. The two listings below compute the same two independent expressions only under their stated memory assumptions.

### Option 3: let the compiler schedule around it

Since the load-use stall is predictable, the compiler can reorder independent instructions to fill the gap. For ordinary valid, nonvolatile memory accesses with independent values and no aliasing or observable-order constraints, take `a = b + c; d = e + f`. The listings below are schematic (symbolic addresses rather than literal RISC-V load/store syntax; `!` marks a load-use stall and is not an instruction):

```
# naive order        # scheduled
lw  x1, b            lw  x1, b
lw  x2, c            lw  x2, c
add x3, x1, x2  !    lw  x4, e
sw  x3, a            add x3, x1, x2
lw  x4, e            lw  x5, f
lw  x5, f            sw  x3, a
add x6, x4, x5  !    add x6, x4, x5
sw  x6, d            sw  x6, d
```

The naive order has two load-use stalls (marked `!`). In the scheduled order every load has an independent instruction between it and its first dependent operation, so there are none. Counting cycles for the 8 instructions from first fetch to last write-back:

```formula
N_cyc = k + (n − 1) + s_tot
N_naive = 5 + (8 − 1) + 2 = 14
N_sched = 5 + (8 − 1) + 0 = 12
where
N_cyc: the total clock cycles from the first fetch to the last write-back
k: the number of pipeline stages, 5
n: the number of instructions, 8 in each listing
s_tot: the total stall cycles (bubbles) in the run: 2 for the naive order, 0 for the scheduled one
N_naive, N_sched: the cycle counts for the naive and the scheduled order
In words: each stall adds one cycle to the ideal fill-plus-one-per-instruction count, so removing both stalls saves 2 of 14 cycles.
```

Compilers do this routinely (**instruction scheduling**), and it matters most on simple in-order cores when the target implements the assumed instruction timing.

## Key takeaways
- Move only independent operations across the load-use gap.
- Memory faults, aliasing, volatile accesses and observable order can forbid a reorder.
- Count one additional cycle for each remaining bubble in this finite-run model.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
