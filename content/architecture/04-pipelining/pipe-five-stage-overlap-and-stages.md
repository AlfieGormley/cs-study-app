---
id: pipe-five-stage-overlap-and-stages
sourceLesson: pipe-five-stage
title: Overlap instructions through five stages
level: basic
minutes: 4
summary: Trace a load and see why overlapping instructions improves throughput.
---

Imagine doing laundry. Each load needs washing (30 minutes), drying (30) and folding (30). Doing four loads one after another takes 6 hours. But the moment the first load moves to the dryer, the washer is free. Start the second load then, and four loads finish in 3 hours.

No individual load got faster: each still takes 90 minutes. What improved is **throughput**, the rate at which loads come out the end. That is pipelining, and it is a fundamental technique in CPU design.

## Executing one instruction

A simplified processor can organize instructions into a common sequence of stages. The classic RISC design, from the MIPS processors of the 1980s and the Patterson and Hennessy textbooks, splits it into five stages:

| Stage | Name | Does |
|---|---|---|
| IF | Fetch | Read instruction at PC |
| ID | Decode | Decode, read registers |
| EX | Execute | ALU op or address |
| MEM | Memory | Load or store data |
| WB | Write back | Write result register |

Follow a load, `lw x1, 8(x2)` (RISC-V: load a 32-bit word using x2 plus an eight-byte offset; on RV64I, sign-extend it into x1):

1. **IF**: read the instruction from the instruction cache at the address in the program counter (PC); compute the sequential next PC by adding four bytes for the uncompressed base instruction used here.
2. **ID**: decode the opcode; read register x2; sign-extend the immediate 8.
3. **EX**: the ALU adds the eight-byte offset to x2 to form the byte address.
4. **MEM**: read the data cache at that address.
5. **WB**: write the loaded value into x1.

Other instructions use a subset. An `add x3, x4, x5` does its addition in EX and has nothing to do in MEM. A store `sw` writes memory in MEM and has nothing to write back. A branch compares registers and decides the next PC.

## With a pipeline

Pipelining puts the next instruction into IF as soon as the current one moves on to ID. Once the pipeline is full, all five stages are busy, each with a different instruction:

```
cycle  1   2   3   4   5   6   7   8
i1     IF  ID  EX  MEM WB
i2         IF  ID  EX  MEM WB
i3             IF  ID  EX  MEM WB
i4                 IF  ID  EX  MEM WB
```

Read it column by column. In cycle 5, i1 is writing back, i2 is in MEM, i3 in EX, i4 in ID, and (if there were one) i5 in IF. From cycle 5 on, **one instruction completes every cycle**: an ideal CPI of 1.

Here is a small Python function that draws the diagram:

```python
STAGES = ["IF", "ID", "EX", "MEM", "WB"]

def diagram(n):
    if type(n) is not int or n < 0:
        raise ValueError("bad count")
    k = len(STAGES)
    # First result fills all k stages.
    total = k + n - 1 if n else 0
    for i in range(n):
        row = ["    "] * total
        # Shift this instruction one column.
        for s, name in enumerate(STAGES):
            row[i + s] = f"{name:<4}"
        print(f"i{i + 1:<3}" + "".join(row))
    print("cycles:", total)

# Four overlapping rows; 8 cycles total.
diagram(4)   # ... cycles: 8
```

## Key takeaways
- IF, ID, EX, MEM and WB describe the five-stage teaching pipeline.
- Several instructions occupy different stages simultaneously.
- The ideal scalar pipeline completes one instruction per cycle after filling.

## Further reading
- [MIT Computation Structures: performance and pipelining](https://computationstructures.org/notes/performance/notes.html)
- [RISC-V unprivileged ISA specification](https://riscv.github.io/riscv-isa-manual/snapshot/spec/)
- [BOOM implementation: pipeline](https://docs.boom-core.org/en/latest/sections/intro-overview/boom-pipeline.html)
