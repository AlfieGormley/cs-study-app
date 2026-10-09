---
id: pipe-five-stage
title: The 5-stage pipeline
level: basic
minutes: 11
summary: How splitting instruction execution into five overlapping stages lets a CPU finish one instruction per cycle, what each stage does, and why the speedup is less than five.
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

Follow a load, `lw x1, 8(x2)` (RISC-V: load the word at address x2 + 8 into x1):

1. **IF**: read the instruction from the instruction cache at the address in the program counter (PC); compute PC + 4.
2. **ID**: decode the opcode; read register x2; sign-extend the immediate 8.
3. **EX**: the ALU adds x2 + 8 to form the address.
4. **MEM**: read the data cache at that address.
5. **WB**: write the loaded value into x1.

Other instructions use a subset. An `add x3, x4, x5` does its addition in EX and has nothing to do in MEM. A store `sw` writes memory in MEM and has nothing to write back. A branch compares registers and decides the next PC.

## Without a pipeline

A simple **single-cycle** processor does all five steps in one long clock cycle. The cycle must be long enough for the slowest instruction. Using these hypothetical combinational stage delays, with single-cycle boundary overhead ignored:

```
IF   ID   EX   MEM  WB
200  100  200  200  100  (ps)
```

A load uses all five steps, so the single cycle must cover their sum:

```formula
T_1 = t_IF + t_ID + t_EX + t_MEM + t_WB
T_1 = 200 + 100 + 200 + 200 + 100 = 800 ps
f_1 = 1 / T_1 = 1 / 800 ps = 1.25 GHz
where
T_1: the clock period of the single-cycle design, in picoseconds (ps)
t_IF, t_ID, t_EX, t_MEM, t_WB: the logic delay of each step (fetch, decode, execute, memory, write back), in picoseconds
f_1: the resulting clock frequency, in gigahertz (GHz)
ps: picoseconds; 1 ps = 10^-12 seconds, so 1,000 ps = 1 nanosecond
GHz: gigahertz, 10^9 cycles per second
In words: a single-cycle CPU's clock tick must be as long as all five steps of its slowest instruction put together.
```

So the clock period is 800 ps (1.25 GHz), and each instruction takes one cycle. Most of the hardware sits idle most of the time: while the ALU is working, the fetch unit has nothing to do.

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
    total = k + n - 1 if n else 0
    for i in range(n):
        row = ["    "] * total
        for s, name in enumerate(STAGES):
            row[i + s] = f"{name:<4}"
        print(f"i{i + 1:<3}" + "".join(row))
    print("cycles:", total)

diagram(4)   # ... cycles: 8
```

### Pipeline registers

Between each pair of stages sits a **pipeline register** (named IF/ID, ID/EX, EX/MEM and MEM/WB). At every clock edge, each stage's output is latched into the next register. This holds everything the instruction still needs: its operand values, destination register number and control signals (is it a load? does it write a register?). Without these registers, the next instruction would overwrite the values the previous one is still using.

### The clock period

The clock now only needs to cover the slowest **stage**, not the whole instruction. In reality a pipeline register adds its own delay, setup time and clock skew, which must be budgeted:

```formula
T_clk = t_max + t_reg
t_max = max(t_IF, t_ID, t_EX, t_MEM, t_WB)
where
T_clk: the pipelined clock period, in picoseconds (ps)
t_IF, t_ID, t_EX, t_MEM, t_WB: the logic delay of each of the five stages, in picoseconds
max: the largest of the values listed
t_max: the delay of the slowest stage
t_reg: the per-cycle overhead of a pipeline register (its own delay, setup time and clock skew), in picoseconds
ps: picoseconds, 10^-12 seconds
In words: every stage gets the same clock tick, so the tick must fit the slowest stage plus the register overhead.
```

Here the slowest stages are IF, EX and MEM at 200 ps. With no overhead the period is 200 ps. Assuming 20 ps of combined per-cycle boundary overhead gives 200 + 20 = 220 ps; this is a teaching assumption, not a measured device value.

## How much faster?

Take a run of instructions on an initially empty, single-issue pipeline with no stalls. The first instruction needs one cycle per stage to come out, and each later one comes out 1 cycle after the one before:

```formula
N_cyc = k + (n − 1)
where
N_cyc: the total clock cycles from the first fetch to the last write-back
k: the number of pipeline stages; 5 here
n: the number of instructions in the run, at least 1
In words: filling the pipeline costs one cycle per stage, then every further instruction adds just one more cycle.
```

For 1,000 instructions, compare the single-cycle design with the pipelined one:

```formula
T_single = n × T_1 = 1000 × 800 ps = 800 ns
T_pipe = (k + n − 1) × T_clk
T_pipe = 1004 × 200 ps = 200.8 ns
S = T_single / T_pipe = 800 / 200.8 ≈ 3.98
where
T_single: the total time on the single-cycle design
T_pipe: the total time on the pipelined design
n: the number of instructions, 1,000
k: the number of pipeline stages, 5
T_1: the single-cycle clock period, 800 ps
T_clk: the pipelined clock period, 200 ps (no register overhead)
S: the speedup: how many times faster the pipeline is
ps: picoseconds, 10^-12 seconds
ns: nanoseconds, 10^-9 seconds; 1 ns = 1,000 ps
≈: approximately equal to (rounded)
In words: the pipeline runs the 1,000 instructions about 3.98 times faster than the single-cycle design.
```

The ideal speedup of a k-stage pipeline is k, here 5: that happens when the k stages are perfectly balanced, so each stage is exactly one k-th of the single-cycle period, and there is no register overhead. We got about 4 for two reasons:

1. **Unbalanced stages.** ID and WB need only 100 ps but get a full 200 ps slot. The pipeline runs at the pace of its slowest stage.
2. **Fill and drain.** The first k − 1 cycles have empty stages. With 1,000 instructions this barely matters (4 cycles); with 5 it would matter a lot.

For a long run, n is so large that the fill cycles vanish and the speedup settles at the ratio of the two clock periods:

```formula
S_max = T_1 / T_clk
S_max = 800 ps / 200 ps = 4
S_max = 800 ps / 220 ps ≈ 3.6
where
S_max: the long-run speedup as the number of instructions grows very large
T_1: the single-cycle clock period, 800 ps
T_clk: the pipelined clock period: 200 ps without register overhead, 220 ps with 20 ps of overhead
ps: picoseconds, 10^-12 seconds
≈: approximately equal to (rounded)
In words: in the long run the pipeline wins by the ratio of the old clock tick to the new one, so register overhead eats directly into the gain.
```

> [!warning] Throughput and latency differ
> With a 200 ps cycle, a single load now takes five cycles of 200 ps, 1,000 ps in all, to pass through, compared with 800 ps unpipelined. In this comparison, pipelining raises throughput while increasing instruction latency. Balanced stages with no register overhead could preserve latency; real overhead and imbalance often increase it. Enough independent work allows the improved throughput to outweigh fill/drain overhead; billions of instructions are not required.

## Why RISC was designed for this

Regular encodings and load/store operations, as in the base RISC teaching model here, simplify pipeline design:

- **Fixed-length base instructions** (32 bits in the model; compressed forms such as RISC-V C differ) let IF fetch one per cycle and let ID start decoding before it knows what the instruction is.
- **Regular register fields**, where the formats keep their positions fixed, allow register selection alongside opcode decoding.
- **Load/store data operations**: ordinary arithmetic in this model uses registers; separate loads and stores transfer data. Instruction fetch and specialised atomic operations are outside that simplification.
- **Naturally aligned scalar accesses** avoid line splits when their power-of-two size does not exceed the line size and divides it. Real ISAs can also allow unaligned accesses, with additional handling.

x86, with variable-length instructions from 1 to 15 bytes and memory operands on arithmetic, is much harder to pipeline. Many Intel and AMD implementations translate x86 instructions into simple, RISC-like **micro-operations** (µops), and pipeline those.

## Real pipelines

The five-stage design is a teaching model. Real implementations divide work differently, and “pipeline depth” may refer to different instruction paths or recovery events. A cross-product table of stage counts is omitted because comparable primary documentation was not established for every entry.

Splitting a critical stage can shorten the clock period, while adding register overhead and potentially delaying particular result or branch-resolution paths. Not every hazard penalty necessarily increases: that depends on where stages are added and which bypass paths exist.

## Where it goes wrong

The ideal "one instruction per cycle" assumes every instruction can enter the pipeline the cycle after the previous one. Three things break that:

- **Structural hazards**: two instructions need the same hardware in the same cycle.
- **Data hazards**: an instruction needs a result the previous one hasn't produced yet.
- **Control hazards**: after a branch, the CPU doesn't know which instruction to fetch next.

The next lesson covers each one and the tricks, chiefly **forwarding**, that keep the pipeline flowing.

## Key takeaways
- The ideal single-issue model overlaps instructions and completes one per cycle in steady state, with no hazards or resource conflicts.
- Pipelining targets throughput; in the worked design each instruction takes longer to pass through.
- The clock is set by the slowest stage plus pipeline register overhead, so unbalanced stages limit the speedup.
- In the ideal model, a run takes one cycle per stage to fill the pipeline, then one cycle for each further instruction. Long-run speedup approaches the number of stages only with balanced stages and negligible overhead.
- Regular encodings and load/store organization simplify this pipeline model; many x86 implementations pipeline decoded micro-ops.

## Further reading
- [Classic RISC pipeline — Wikipedia](https://en.wikipedia.org/wiki/Classic_RISC_pipeline)
- [Instruction pipelining — Wikipedia](https://en.wikipedia.org/wiki/Instruction_pipelining)
- [Micro-operation — Wikipedia](https://en.wikipedia.org/wiki/Micro-operation)
- [Instruction cycle — Wikipedia](https://en.wikipedia.org/wiki/Instruction_cycle)
