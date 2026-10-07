---
id: pipe-hazards
title: Hazards and forwarding
level: intermediate
minutes: 13
summary: The structural, data and control hazards that stop a pipeline completing one instruction per cycle, and how forwarding, stalls, scheduling and early branch resolution deal with them.
---

This lesson uses a single-issue, in-order five-stage teaching pipeline with one-cycle stages, cache hits, register writes before reads in the same cycle, and the stated bypass paths. Numerical stalls below belong to this model, not every real CPU.

The last lesson's pipeline diagram assumed every instruction could start the cycle after the previous one. Real programs break that assumption constantly. The very next instruction often needs the result the current one is still computing.

A situation that prevents the next instruction from starting in its slot is a **hazard**. There are three kinds, and the hardware has a different trick for each. Whatever is left over shows up as extra CPI.

## Structural hazards

A **structural hazard** happens when two instructions need the same piece of hardware in the same cycle.

The classic example is memory. In cycle 4, instruction i1 is in MEM reading data while i4 is in IF fetching an instruction. With one single-ported memory, one of them must wait.

Possible fixes include stalling, adding ports or separating resources. Many CPUs use **separate L1 instruction and data caches** (a "modified Harvard" design), and register files often have multiple access ports. The textbook 5-stage pipeline is designed so that structural hazards do not arise; in wider, real processors they appear as contention for ports and functional units.

## Data hazards

Consider:

```
add x1, x2, x3   # x1 = x2 + x3
sub x4, x1, x5   # needs the new x1
```

`sub` reads its registers in ID, in cycle 3. But `add` only writes x1 in WB, in cycle 5. If nothing intervenes, `sub` reads the *old* x1. This is a **read-after-write (RAW)** hazard, also called a true dependence.

```
cycle  1   2   3   4   5
add    IF  ID  EX  MEM WB
sub        IF  ID  ...

add writes x1 in cycle 5 (WB)
sub reads x1 in cycle 3 (ID): too early
```

### Option 1: stall

The simplest fix is for the hardware to detect the dependence in ID and hold `sub` there, inserting **bubbles** (do-nothing slots, effectively `nop`s) into EX until `add` has written x1.

A common trick helps: the register file is written in the first half of a cycle and read in the second half. So `sub` can read x1 in the same cycle that `add` writes it back (cycle 5). That still means `sub` waits in ID for cycles 3 and 4: **two stall cycles** for every back-to-back dependency. Since dependent instructions are extremely common, this would be ruinous for CPI.

### Option 2: forwarding

The key observation: the value `sub` needs exists at the end of `add`'s EX stage, in cycle 3. It just hasn't reached the register file yet. **Forwarding** (also called **bypassing**) adds wires and multiplexers that route results from the pipeline registers straight back to the ALU inputs.

```
         +-------------------+
         |  forward EX/MEM   |
         v                   |
ID/EX -> ALU -> EX/MEM -> MEM/WB
         ^                     |
         |  forward MEM/WB     |
         +---------------------+
```

There are two main paths:

- **EX/MEM to EX**: the result of the instruction directly ahead (one instruction back).
- **MEM/WB to EX**: the result of the instruction two ahead.

A **forwarding unit** compares the source register numbers of the instruction entering EX with the destination register numbers in EX/MEM and MEM/WB. If they match (and the earlier instruction really writes a register, and the register isn't x0), it selects the forwarded value instead of the stale one from ID/EX. If both match, the most recent producer takes priority, but its value must actually be available: a load in EX/MEM does not yet provide its loaded data. Stalling must prevent accidentally forwarding that load’s address or an older superseded value.

With forwarding, `add` followed by `sub` runs with **zero stalls**.

### The load-use hazard

Forwarding cannot fix everything. A load's data only arrives at the end of MEM:

```
lw  x1, 0(x2)    IF ID EX MEM WB
add x3, x1, x4      IF ID -- EX  MEM WB
                          ^ bubble
```

`add` needs x1 at the start of its EX. If `add` ran in cycle 4, it would need a value that `lw` only produces at the end of cycle 4. Time cannot run backwards, so the hardware must stall for **one cycle**, then forward from MEM/WB. This is the **load-use hazard**, and a **hazard detection unit** in ID spots it: "the instruction in EX is a load, and its destination is one of my sources".

### Option 3: let the compiler schedule around it

Since the load-use stall is predictable, the compiler can reorder independent instructions to fill the gap. For ordinary valid, nonvolatile memory accesses with independent values and no aliasing or observable-order constraints, take `a = b + c; d = e + f`. The listings below are schematic (symbolic addresses rather than literal RISC-V load/store syntax):

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

The naive order has two load-use stalls (marked `!`). In the scheduled order every load has an independent instruction between it and its first dependent operation, so there are none: 12 cycles instead of 14. Compilers do this routinely (**instruction scheduling**), and it matters most on simple in-order cores such as small ARM microcontrollers.

### Counting stalls in code

This function counts stall cycles for a straight-line program on the 5-stage pipeline. It records the earliest logical issue slot compatible with each dependency. With forwarding this is not the cycle when the register file itself contains the new value. Program entries are `(op, dst, srcs)` with integer register IDs 0–31, `dst=None` for no register result, and register 0 hard-wired to zero. All forwarded sources, including store data, are required by EX in this simplified model; it does not model a separate late store-data bypass, branches, cache misses or multicycle units:

```python
def stalls(prog, forwarding=True):
    rdy = {}     # reg -> ready slot
    cycle = 0    # logical issue slot
    total = 0
    for op, dst, srcs in prog:
        need = [rdy.get(r, 0)
                for r in srcs if r != 0]
        start = max(need + [cycle])
        total += start - cycle
        cycle = start
        if dst:
            if not forwarding:
                lat = 3      # wait for WB
            elif op == "lw":
                lat = 2      # load-use
            else:
                lat = 1      # EX -> EX
            rdy[dst] = cycle + lat
        cycle += 1
    return total
```

On the naive sequence above it returns 2 with forwarding and 8 without; on the scheduled one, 0 and 4. For this sequence and model, forwarding removes more stalls than scheduling alone; combining them removes all modelled stalls.

### WAR and WAW

There are two other orderings of register access:

- **Write after read (WAR)**: a later instruction writes a register an earlier one still needs to read.
- **Write after write (WAW)**: two instructions write the same register, and the final value must come from the later one.

These are **name dependences**: they exist only because two instructions happen to reuse a register name, not because data flows between them. In the in-order 5-stage pipeline they cannot cause trouble, since every instruction reads in ID and writes in WB in program order. They become real problems in out-of-order processors, where **register renaming** removes them (lesson 5).

## Control hazards

After fetching a branch in cycle 1, what should IF fetch in cycle 2? The branch hasn't even been decoded, let alone compared its registers. This is a **control hazard**.

Suppose the branch outcome is known at the end of EX (cycle 3). Options:

1. **Stall** until the branch resolves: 2 lost cycles on every branch.
2. **Predict not taken**: keep fetching sequentially. If the branch isn't taken, no cost. If it is, **flush** the two wrongly fetched instructions (turn them into bubbles) and fetch from the target: a 2-cycle penalty.
3. **Resolve earlier**: add a comparator and target adder in ID so the branch is decided in cycle 2. The penalty falls to 1 cycle, but now the branch may need forwarding into ID and can stall on an instruction ahead of it.
4. **Branch delay slot**: classic MIPS normal delay slots execute on both paths; some branch-likely forms have annulment rules. The compiler fills the slot with useful work when it can (or a `nop`). It provides one architecturally executed slot; that does not necessarily hide the entire branch penalty of a particular implementation, but became a burden when pipelines got deeper and wider. RISC-V and ARM64 do not have delay slots.

Real processors use **dynamic branch prediction**, the subject of the next lesson.

## Putting numbers on it

For a long run in this scalar model, ignoring fill/drain and avoiding double-counting overlapping penalties, hazards add stall cycles to ideal CPI 1:

```
CPI = 1 + stall cycles per instruction
```

> [!example] A worked CPI
> 25% of instructions are loads, and 40% of those are immediately followed by a dependent instruction (1-cycle stall each). 15% are branches; with predict-not-taken, 60% of them are taken, costing 2 cycles.
> Assume these penalties are additive, and the stated dependencies need operands in EX. Load stalls: 0.25 × 0.4 × 1 = 0.10.
> Branch stalls: 0.15 × 0.6 × 2 = 0.18.
> CPI = 1 + 0.10 + 0.18 = **1.28**.

Notice branches cost more than loads here. That is why branch prediction gets an entire lesson, and why it matters even more in deeper pipelines, where recovery penalties may be larger. Exact real-core cycle counts require a specified core and measurement.

> [!warning] Don't forget x0
> In RISC-V and MIPS, register 0 is hard-wired to zero. Forwarding logic must ignore writes to it; otherwise `add x0, x1, x2` followed by `add x3, x0, x4` would wrongly forward a non-zero value. Textbook forwarding conditions include an explicit "destination ≠ 0" check for this reason.

## Key takeaways
- Structural hazards can be handled by stalling or providing more resources, such as separate instruction and data caches.
- RAW data hazards are handled by forwarding results from pipeline registers straight to the ALU, which removes most stalls.
- An immediate EX-stage load consumer costs one stall in this model; compilers schedule independent instructions into that slot.
- WAR and WAW are name dependences; they don't matter in an in-order 5-stage pipeline but do in out-of-order cores.
- Control hazards cost cycles proportional to how late the branch resolves; predicting, resolving early, and (historically) delay slots reduce them.
- CPI = 1 + stalls per instruction, computed as frequency × probability × penalty for each hazard type.

## Further reading
- [Hazard (computer architecture) — Wikipedia](https://en.wikipedia.org/wiki/Hazard_(computer_architecture))
- [Operand forwarding — Wikipedia](https://en.wikipedia.org/wiki/Operand_forwarding)
- [Classic RISC pipeline — Wikipedia](https://en.wikipedia.org/wiki/Classic_RISC_pipeline)
- [Delay slot — Wikipedia](https://en.wikipedia.org/wiki/Delay_slot)
- [MIPS architecture manual: delay slots and branch likely, section 5.3.2](https://hades.mech.northwestern.edu/images/a/af/MIPS32_Architecture_Volume_I-A_Introduction.pdf)
