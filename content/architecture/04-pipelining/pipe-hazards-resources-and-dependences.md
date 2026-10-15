---
id: pipe-hazards-resources-and-dependences
sourceLesson: pipe-hazards
title: Resource conflicts and register dependences
level: intermediate
minutes: 4
summary: Recognise structural hazards and distinguish true register data flow from register-name reuse.
---

Use IF, ID, EX, MEM and WB from the preceding pipeline units. Keep the model assumptions below: the exact stall counts follow from the stated stage timing, not from the RISC-V instruction set itself.

This lesson uses a single-issue, in-order five-stage teaching pipeline with one-cycle stages, cache hits, register writes before reads in the same cycle, and the stated bypass paths. Numerical stalls below belong to this model, not every real CPU.

The earlier overlap unit's pipeline diagram assumed every instruction could start the cycle after the previous one. Real programs break that assumption constantly. The very next instruction often needs the result the current one is still computing.

A situation that prevents the next instruction from starting in its slot is a **hazard**. There are three kinds, and the hardware has a different trick for each. Whatever is left over shows up as extra CPI.

## Structural hazards

A **structural hazard** happens when two instructions need the same piece of hardware in the same cycle.

The classic example is memory. In cycle 4, instruction i1 is in MEM reading data while i4 is in IF fetching an instruction. With one single-ported memory, one of them must wait.

Possible fixes include stalling, adding ports or separating resources. Many CPUs use **separate L1 instruction and data caches** (a "modified Harvard" design), and register files often have multiple read and write ports. The ideal five-stage design assumes sufficient independent resources to avoid these structural hazards; in wider, real processors they appear as contention for ports and functional units.

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

### WAR and WAW

There are two other orderings of register access:

- **Write after read (WAR)**: a later instruction writes a register an earlier one still needs to read.
- **Write after write (WAW)**: two instructions write the same register, and the final value must come from the later one.

These are **name dependences**: they exist only because two instructions happen to reuse a register name, not because data flows between them. In the in-order 5-stage pipeline they cannot cause trouble, since every instruction reads in ID and writes in WB in program order. They become real problems in out-of-order processors, where **register renaming** removes them (the later register-renaming unit).

## Key takeaways
- A shared single memory port can conflict between instruction fetch and data access.
- RAW carries a produced value; WAR and WAW arise from reuse of register names.
- The stated register timing permits same-cycle write then read, leaving two stalls without bypasses.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
- [BOOM implementation: rename stage](https://docs.boom-core.org/en/latest/sections/rename-stage.html)
