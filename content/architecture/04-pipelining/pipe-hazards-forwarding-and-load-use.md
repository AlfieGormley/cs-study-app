---
id: pipe-hazards-forwarding-and-load-use
sourceLesson: pipe-hazards
title: Forward values and handle load-use stalls
level: intermediate
minutes: 3
summary: Choose the newest available result, exclude the zero register and explain the remaining one-cycle load-use gap.
---

This unit uses the scalar five-stage pipeline with one-cycle cache-hit stages and operand bypasses into EX. A dependent instruction needs its input at the start of EX; an ALU result appears at the end of EX, while loaded data appears at the end of MEM.

> [!warning] Exclude the zero register
> RISC-V x0 always reads zero and discards writes. A forwarding comparison must reject destination x0: otherwise an attempted write could be incorrectly supplied to a later reader. For example, `add x0, x1, x2` must not affect the x0 operand of `add x3, x0, x4`.

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

## Key takeaways
- EX/MEM and MEM/WB bypasses can supply a result before register write-back.
- A newer producer wins, but an unavailable load result must stall rather than forward its address.
- A next-instruction EX consumer of a load needs one stall in this teaching model.

## Further reading
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
