---
id: pipe-out-of-order
title: Superscalar, out-of-order and Tomasulo
level: advanced
minutes: 16
summary: How modern cores finish several instructions per cycle by issuing them out of order, using register renaming, reservation stations, Tomasulo's algorithm and a reorder buffer, and what still limits them.
---

A scalar pipeline, however well forwarded and predicted, peaks at one instruction per cycle. In this instruction-level model, sustaining CPI below 1 requires starting more than one instruction per cycle on average. That is **superscalar** execution.

In-order superscalar execution can improve throughput, but a blocked instruction can prevent younger independent work from issuing. **Out-of-order** execution finds ready work further ahead while preserving the architectural rules. The 200-cycle load used below is hypothetical, not a universal DRAM latency. In-order retirement does not imply sequentially consistent interthread memory ordering. This lesson shows how.

## Instruction-level parallelism

**Instruction-level parallelism** (ILP) is the number of instructions in a stretch of code that could, in principle, run at the same time.

```
a = b + c      # independent
d = e + f      # independent
g = a * d      # needs both
```

The first two can run together; the third must wait. ILP is limited by **true (RAW) dependences**, by branches (you can't run what you haven't fetched), and by memory latency.

## In-order superscalar

A simple in-order superscalar design can issue two instructions per cycle when pairing rules, operands and execution resources allow. Multiple issue does not itself require out-of-order scheduling.

The weakness of in-order issue: when one instruction stalls, everything behind it stalls too, even independent work.

```
lw   x1, 0(x2)    # assume a long cache miss
add  x3, x1, x4   # must wait: depends on x1
mul  x5, x6, x7   # independent, but stuck
sub  x8, x9, x10  # independent, but stuck
```

An out-of-order core runs `mul` and `sub` while the load is outstanding.

## The out-of-order pipeline

A common out-of-order (OoO) teaching design has three parts. Real designs differ in µop grouping, scheduler organisation and retirement bookkeeping:

```
IN ORDER: fetch, decode, rename,
          allocate ROB entry
              |
              v
OUT OF ORDER: scheduler waits for
              operands, issues to
              ALUs / load-store unit
              |
              v
IN ORDER: reorder buffer retires
          (commits) oldest first
```

1. **Front end, in order**: fetch (guided by the branch predictor), decode into µops, **rename** registers, and allocate tracking space in the **reorder buffer** (ROB) and in a scheduler.
2. **Execution, out of order**: each µop waits in the scheduler until its source operands are ready and a suitable unit is free, then **issues**. Results are broadcast to waiting µops.
3. **Retirement, in order**: the ROB commits results to the architectural state strictly in program order, so exceptions and mispredictions can be handled precisely.

## Register renaming

Out-of-order execution exposes the **name dependences** from lesson 3:

```
i1: mul x1, x2, x3
i2: add x4, x1, x5   # RAW on x1 (real)
i3: add x1, x6, x7   # WAW i1, WAR i2
i4: add x8, x1, x2   # RAW on i3's x1
```

i3 and i4 have nothing to do with i1 and i2; they just reuse the name x1. But if i3 ran before i1 finished, it could have its x1 overwritten by the slow `mul` (WAW), or i2 could read i3's x1 instead of i1's (WAR).

**Renaming** assigns distinct storage to simultaneously live register versions. A physical-register implementation maintains more result storage than the architectural register set. Exact counts depend on the core and ISA extensions; they are omitted without a specified implementation. A **register alias table** (RAT) maps each architectural register to the physical register holding its newest value.

This teaching renamer handles a finite straight-line sequence of ordinary register-producing operations. It has no retirement, branches, zero-register semantics or free-list reclamation; names x0… are generic, not a complete RISC-V implementation.

```python
def rename(prog, n_arch=32, n_phys=128):
    if not 0 < n_arch <= n_phys:
        raise ValueError("bad counts")
    rat = {f"x{i}": f"p{i}"
           for i in range(n_arch)}
    free = [f"p{i}"
            for i in range(n_arch, n_phys)]
    for op, dst, srcs in prog:
        s = [rat[r] for r in srcs]
        if dst not in rat:
            raise ValueError("bad dst")
        if not free:
            raise ValueError("no registers")
        rat[dst] = free.pop(0)
        print(f"{rat[dst]} = {op}"
              f"({', '.join(s)})")

rename([
    ("mul", "x1", ["x2", "x3"]),
    ("add", "x4", ["x1", "x5"]),
    ("add", "x1", ["x6", "x7"]),
    ("add", "x8", ["x1", "x2"]),
])
```

Output:

```
p32 = mul(p2, p3)
p33 = add(p32, p5)
p34 = add(p6, p7)
p35 = add(p34, p2)
```

The two x1s are now p32 and p34. Only true register dependences remain in this arithmetic trace (p32 → p33, p34 → p35), so i3 and i4 can execute while the `mul` is still running. Sources are renamed *before* the destination, so `add x1, x1, x2` correctly reads the old x1.

In a simple design without shared physical mappings or other retained references, the free list is refilled at retirement: when an instruction that overwrites x1 commits, the physical register that held the *previous* x1 can no longer be needed and is freed.

## Tomasulo's algorithm

Robert Tomasulo devised the original scheme for the floating-point unit of the IBM System/360 Model 91 (1967). Its tag-based scheduling and renaming ideas are foundational; modern implementations need not use the original structure.

Three structures:

- **Reservation stations** (RS) sit in front of each functional unit. Each holds one waiting instruction and, for each operand, either its **value** (V) or the **tag** (Q) of the reservation station that will produce it.
- A **register status table** records, for each register, which RS tag will write it next (blank if the register file value is current).
- A **common data bus** (CDB) broadcasts every result as a (tag, value) pair to all reservation stations and the register file at once.

Each instruction goes through:

1. **Issue**: take the next instruction in order, if a matching RS is free. For each source, copy the value from the register file if it is current, or else copy the producing tag. Then set the destination register's status to this RS's tag.
2. **Execute**: when both operands are values, start executing. Independent instructions overtake stalled ones here.
3. **Write result**: broadcast (tag, value) on the CDB. Every RS waiting on that tag grabs the value. The register file is updated only if its status still names this tag.

Tags distinguish producer versions, providing renaming without requiring the separate physical register file used in the preceding example. A reservation station is not literally a physical register.

### A worked snapshot

```
1: L.D   F6, 0(R2)
2: MUL.D F0, F6, F4
3: ADD.D F6, F8, F2
4: SUB.D F2, F6, F4
```

Assume enough reservation stations, ready initial registers and sufficiently long operation latencies for all four to issue before any result broadcasts. This is a schematic floating-point instruction trace, not literal IBM instruction syntax:

| RS | Op | Operand j | Operand k |
|---|---|---|---|
| Load1 | L.D | addr R2+0 | |
| Mult1 | MUL | Q = Load1 | V = F4 |
| Add1 | ADD | V = F8 | V = F2 |
| Add2 | SUB | Q = Add1 | V = F4 |

Register status: F0 ← Mult1, F2 ← Add2, F6 ← Add1.

What happens next:

- **Add1 can start immediately.** It copied F8 and F2 at issue, so it waits for neither the load nor the multiply.
- When **Load1** broadcasts, Mult1 captures the value. But F6's status says Add1, not Load1, so the **register file is not updated**. The load's F6 is now an orphan that only Mult1 needed. That is the WAW hazard with instruction 3, resolved.
- When **Add1** broadcasts, Add2 (the SUB) captures it, and F6 in the register file is updated.
- SUB overwrites F2, which ADD read. That WAR is harmless: ADD copied F2's value into its RS at issue.
- **Mult1** can finish last despite issuing second; exact completion order depends on latencies and resource availability.

### What the original lacked

The Model 91 wrote results to registers as soon as they were computed, out of order, so a fault in an earlier, slower instruction left a state where later instructions had already taken effect. It could produce **imprecise** floating-point exceptions. The original tag-and-broadcast algorithm described here lacks the modern speculative branch-recovery machinery.

## The reorder buffer

A **reorder buffer**, discussed by Smith and Pleszkun in their work on precise interrupts, is one solution. In this teaching model it is a circular queue with one entry per in-flight instruction, in program order. Real entry granularity can differ. Checkpointing and other bookkeeping are also needed for speculative recovery.

- Instructions execute out of order and write results into their ROB entry (or a physical register), not the architectural state.
- The head of the ROB **retires** (commits) only when it has completed. Retirement is in order, up to the supported retirement width per cycle.
- If the head instruction faulted, the core discards it and every younger entry, and the exception appears exactly at that instruction: **precise exceptions**.
- If a branch turns out mispredicted, every entry after it is **squashed**. The rename table is restored to its state at the branch, and fetch restarts on the right path.

This is what makes **speculative execution** safe, architecturally: wrong-path instructions execute, but never commit. But "never commits" is not the same as "leaves no trace": some microarchitectural effects, such as cache state, may persist; recovery of predictor history is implementation-dependent, which is what the Spectre and Meltdown vulnerabilities revealed.

### Memory ordering

Loads and stores need extra care, because whether two of them conflict depends on addresses that aren't known until they execute.

- Ordinary cacheable stores retain speculative data in a store queue or buffer until it is safe to commit. Squashing a store must not make its data architecturally visible; related address translation or ownership requests can still affect microarchitectural state.
- A load may forward bytes from the youngest matching older store when address, data and coverage requirements permit. Partial overlaps or unavailable data can require stalling or replay.
- A core may let a load pass older stores with unknown addresses (**memory disambiguation**). If required ordering was violated, recovery re-executes affected work; a full squash from the load is one implementation, not a universal mechanism.

## How big is the window?

> [!note] Product data omitted
> Exact commercial decode widths and ROB sizes are omitted because sufficiently reliable, consistently defined primary-source figures were not established here. Instruction counts, µop counts and ROB entries are not interchangeable.

For a hypothetical 80 ns miss at 4 GHz, latency is 320 cycles. Maintaining allocation at four entries per cycle while retirement is blocked would require space for roughly 1,280 entries. This is an occupancy estimate, assuming sufficient independent work and no earlier resource limit. It does not prove all real misses stall for a fixed duration. A larger window may discover independent memory accesses whose latencies overlap (**memory-level parallelism**); bandwidth and other queues still limit progress.

## Why not let the compiler do it?

**VLIW** (very long instruction word) designs expose operation grouping to the compiler, shifting much scheduling work from hardware to software. Variable memory latency makes static scheduling harder. Intel Itanium used **EPIC**, an explicitly parallel design with bundles, instruction groups, predication and speculation; it should not be reduced to a simple VLIW machine with no means to tolerate uncertain execution. A single-cause explanation of its commercial outcome is omitted because this lesson has not established evidence for one.

## The costs

- **Area and power.** Rename tables, schedulers that compare every result tag with every waiting operand each cycle (wakeup and select), and large multi-ported register files are expensive. Scheduler logic scales badly with width.
- **Diminishing returns.** Dependence chains, branch recovery, fetch limits and memory behaviour can leave issue capacity unused; achievable IPC is workload- and core-dependent.
- **Mispredictions cost more.** More speculative capacity can allow more wrong-path work, but does not by itself fix the recovery latency or amount discarded.

These costs are part of why performance per core stopped growing fast enough, leading to multicore (the final lesson of this module).

## Key takeaways
- Superscalar cores issue several instructions per cycle; out-of-order cores pick ready instructions whose execution resources and ordering constraints permit issue rather than stalling behind a blocked one.
- Register renaming maps architectural to physical registers, removing register-name WAR and WAW dependences. True register data dependences, control constraints and memory ordering still matter.
- Tomasulo's algorithm uses reservation stations holding values or producer tags, and a common data bus that broadcasts results; tags are renaming.
- The reorder buffer retires in order, supporting precise exceptions and architectural recovery with additional bookkeeping; it does not erase every speculative side effect.
- Window size matters for hiding memory latency and enabling memory-level parallelism; VLIW's static scheduling struggles with unpredictable cache misses.

## Further reading
- [Tomasulo's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Tomasulo%27s_algorithm)
- [Out-of-order execution — Wikipedia](https://en.wikipedia.org/wiki/Out-of-order_execution)
- [Register renaming — Wikipedia](https://en.wikipedia.org/wiki/Register_renaming)
- [Re-order buffer — Wikipedia](https://en.wikipedia.org/wiki/Re-order_buffer)
- [Superscalar processor — Wikipedia](https://en.wikipedia.org/wiki/Superscalar_processor)
- [The microarchitecture of Intel, AMD and VIA CPUs, by Agner Fog (PDF)](https://www.agner.org/optimize/microarchitecture.pdf)

- [Smith and Pleszkun: Implementing Precise Interrupts in Pipelined Processors](https://american.cs.ucdavis.edu/academic/readings/papers/smithpleszkun.pdf)
- [University of Edinburgh HASE Tomasulo model](https://www.icsa.inf.ed.ac.uk/research/groups/hase/models/tomasulo/tomasulo.html)
- [Intel: hardware behaviour related to speculative execution](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/hardware-behavior-related-to-speculative-execution.html)
