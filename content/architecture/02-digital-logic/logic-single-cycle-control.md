---
id: logic-single-cycle-control
title: Trace a single-cycle datapath
level: advanced
minutes: 4
sourceLesson: logic-datapath-memory
summary: Control signals choose data routes and writes for each supported instruction.
---

## A single-cycle datapath

This simplified single-cycle datapath supports the illustrated add/lw/sw subset with fixed 32-bit instructions and combinational instruction/data reads. It omits branches, traps, stalls, compressed instructions and many full-ISA details. Its five conceptual steps are:

```
 fetch    decode   execute memory  write
+------+  +-----+  +-----+ +-----+ back
|  PC  |->| reg |->| ALU |>|data |--+
|instr |  |file |  |     | | mem |  |
| mem  |  +-----+  +-----+ +-----+  |
+------+     ^     imm/reg  ALU or  |
             |     (ALUSrc) mem     |
             |              (MemToReg)
             +----------------------+
```

1. **Fetch**: the PC addresses the instruction memory; an adder computes PC + 4 for the next instruction.
2. **Decode**: the instruction's register fields drive the register file's read ports. An immediate (a constant in the instruction) is extracted and sign-extended.
3. **Execute**: the ALU computes. A mux controlled by **ALUSrc** chooses its second operand: register B or the immediate.
4. **Memory**: loads and stores use the ALU result as an address into data memory.
5. **Write back**: a mux controlled by **MemToReg** chooses what is written to `rd`: the ALU result or the loaded value.

### Control is just mux selects and write enables

The control unit is a combinational decoder from the opcode to a handful of control signals. For three instructions:

| Signal | add | lw | sw |
|---|---|---|---|
| RegWrite | 1 | 1 | 0 |
| ALUSrc | reg | imm | imm |
| MemWrite | 0 | 0 | 1 |
| MemToReg | ALU | mem | x |

- `add x5, x6, x7`: ALU adds two registers; result written to x5.
- `lw x5, 8(x6)`: ALU adds x6 + 8 to form an address; the loaded 32-bit word is sign-extended to 64 bits and written to x5 in RV64I.
- `sw x7, 8(x6)`: same address calculation, but the low 32 bits of register B (x7) go to the data memory's write-data input, and **nothing** is written to the register file.

The `x` for `sw` is a don't-care from K-map lessons: with register writing disabled, whatever MemToReg selects is thrown away, so the decoder logic may choose whichever value makes it smallest.

> [!warning] The control signals that must never be don't-cares
> Write enables (RegWrite, MemWrite) must be exactly right for every instruction. A spurious write corrupts state; a wrong mux select whose output is ignored is harmless.

### Why high-performance designs pipeline

In a single-cycle design, the clock period must accommodate the **slowest** supported instruction path under the timing assumptions. A load passes through instruction memory, register read, the ALU and data memory before register-file setup. Those delays occur along one dependent path: knowing the slowest individual block is insufficient. Real timing also includes launch, mux, wire and clock effects.

An `add` skips the data memory but still has to wait for the same long clock. Most of the hardware also sits idle most of the cycle: while the ALU computes, the instruction memory is doing nothing useful.

The fix is to put registers between the five steps so that up to five instructions can overlap in the ideal full five-stage pipeline. Stalls, flushes and hazards reduce occupancy and throughput. That is **pipelining**, the subject of module 4, and the five boxes above become its five stages.

## Key takeaways
- Control signals choose data routes and writes for each supported instruction.
- The longest illustrated instruction path sets the common cycle period.

## Further reading
- [RISC-V — RV64I base integer ISA](https://docs.riscv.org/reference/isa/unpriv/rv64.html)
- [Register file — Wikipedia](https://en.wikipedia.org/wiki/Register_file)
- [Datapath — Wikipedia](https://en.wikipedia.org/wiki/Datapath)
- [Static random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory refresh — Wikipedia](https://en.wikipedia.org/wiki/Memory_refresh)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
- [Verilog — Wikipedia](https://en.wikipedia.org/wiki/Verilog)
- [Logic synthesis — Wikipedia](https://en.wikipedia.org/wiki/Logic_synthesis)
