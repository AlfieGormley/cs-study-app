---
id: logic-datapath-memory
title: Datapath, SRAM vs DRAM, and a first look at Verilog
level: advanced
minutes: 18
summary: How registers, an ALU and muxes combine into a processor datapath driven by control signals, how SRAM and DRAM cells store bits and why one is fast and the other dense, and how hardware is actually written today in Verilog.
---

The previous lessons built the parts: gates, adders, muxes, decoders, flip-flops and state machines. This lesson assembles them. A processor is a **datapath** (the registers, ALU, memories and muxes that data flows through) plus a **control unit** (the logic that decides, for each instruction, which way every mux points and which storage gets written).

Then we look at two important kinds of volatile working memory, **SRAM** and **DRAM**, and finish with how engineers actually describe all this: not by drawing gates, but by writing a **hardware description language** such as Verilog.

## The register file

A CPU's registers live in a **register file**: an array of registers with read and write ports. RISC-V's RV64I has 32 registers of 64 bits (with `x0` hard-wired to zero), and a typical instruction such as `add x5, x6, x7` reads two registers and writes one. A simple implementation therefore uses two read ports and one write port; this port organization is a microarchitectural choice, not an ISA requirement.

It is built entirely from the blocks you already know:

```
write port
  rd (5 bits) -> [5-to-32 decoder]
                    | one-hot, ANDed
                    | with RegWrite
                    v
  wdata -------> [32 registers]
                  |           |
read ports        v           v
  rs1 ------> [32:1 mux] [32:1 mux] <- rs2
                  |           |
                value A    value B
```

- In this teaching register file, reading is combinational: the register number drives the select lines of a 32-to-1 mux (5 select bits, since 2^5 = 32). The value appears as soon as the mux settles.
- **Writing** happens at the clock edge: the decoder turns `rd` into a one-hot signal, ANDed with the `RegWrite` control signal, which enables the load input of exactly one register (the "mux in front of D" trick from lesson 5).
- x0 always reads as zero and discards writes. The implementation can return a constant rather than allocate an ordinary storage cell; merely disabling writes to an uninitialised cell would not guarantee zero.

Real register files in wide out-of-order cores have many more ports (a dozen or more), and each extra port adds wires and transistors to every cell, so their area grows steeply with port count. This is one of the costs that limits how many instructions a core can issue per cycle.

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

The `x` for `sw` is a don't-care from lesson 3: with RegWrite = 0, whatever MemToReg selects is thrown away, so the decoder logic may choose whichever value makes it smallest.

> [!warning] The control signals that must never be don't-cares
> Write enables (RegWrite, MemWrite) must be exactly right for every instruction. A spurious write corrupts state; a wrong mux select whose output is ignored is harmless.

### Why high-performance designs pipeline

In a single-cycle design the clock period must fit the **slowest** instruction. A load goes through every block: instruction memory, register read, ALU, data memory, then setup time at the register file. An `add` skips the data memory but still has to wait for the same long clock. Most of the hardware also sits idle most of the cycle: while the ALU computes, the instruction memory is doing nothing useful.

The fix is to put registers between the five steps so that up to five instructions can overlap in the ideal full five-stage pipeline. Stalls, flushes and hazards reduce occupancy and throughput. That is **pipelining**, the subject of module 4, and the five boxes above become its five stages.

## How memory arrays are organised

Large dense memories generally use compact memory cells rather than ordinary flip-flops; smaller or specialised memories may still be synthesized from registers. Instead, compact cells are packed into a 2D array:

```
          +----------------------+
row addr  | WL0 ===[cells]====== |
-> [row   | WL1 ===[cells]====== |
   dec-   | ...                  |
   oder]  | WLn ===[cells]====== |
          +---|---|---|---|------+
              bit lines
          [   sense amplifiers   ]
col addr->[    column mux        ]-> data
```

- The **row decoder** turns the row address into one active **word line**, which connects every cell in that row to its **bit line**.
- Each bit line carries a tiny signal, so **sense amplifiers** at the bottom amplify it to a full 0 or 1.
- A **column mux** picks the bits you asked for out of the row.

Both use row/column organization, but their cells, sensing, write circuits, timing and peripheral structures differ.

## SRAM: the bistable loop, made addressable

A static RAM cell is the two-inverter loop from lesson 5 plus two **access transistors** that connect it to a pair of complementary bit lines:

```
 BL                            BL'
  |    WL --+------------+      |
  |         |gate        |gate  |
  +------[T1]---+    +--[T2]----+
                |    |
                Q    Q'
                |    |
          +-----+----+-----+
          | two cross-     |
          | coupled        |
          | inverters      |
          +----------------+
```

Two inverters (2 transistors each) plus two access transistors make the standard **6T cell**.

- **Hold**: WL = 0, the access transistors are off, and the loop keeps its value as long as the chip has power. No refresh is needed: that is what *static* means.
- **Read**: precharge BL and BL' high, then raise WL. The side storing 0 slowly pulls its bit line down. The sense amplifier detects the small difference between BL and BL' and resolves it quickly, long before the bit line has swung fully.
- **Write**: drive BL and BL' hard to the new value and its complement, then raise WL. The drivers overpower the small inverters and flip the loop.

Transistor sizing is delicate: the cell must be strong enough not to flip during a read, yet weak enough to be overwritten during a write. SRAM integrates with logic processes and provides low-latency storage; actual cache latency depends on size, organization, technology and clock rate, so it is used for **registers, caches, TLBs and buffers**. Its drawback is size: six transistors per bit. Caches often make up a large fraction of a modern CPU die's area.

## DRAM: one transistor and a capacitor

A dynamic RAM cell stores a bit as **charge on a tiny capacitor**, behind one access transistor:

```
 WL --------+
            | gate
 BL ------[ T ]------+
                     |
                   ===== C
                     |
                    plate
```

That is the **1T1C** cell, far smaller than 6T SRAM, which is why DRAM is the cheap, dense memory used for main memory.

The price is paid in behaviour:

- **Reads are destructive.** Raising WL connects the capacitor to a bit line with much larger capacitance. The charge spreads out ("charge sharing"), nudging the bit line voltage up or down by a small amount. The sense amplifier detects and amplifies this, and in doing so **writes the value back** into the cells of the row.
- **Rows, not words.** Activating a word line reads an entire row into the sense amplifiers, which act as a **row buffer**. Further reads from the same open row are much faster than opening a new one. This is why access patterns matter so much for DRAM performance (module 5).
- **Charge leaks.** A capacitor slowly loses its charge, so every cell must be read and rewritten periodically. Refresh windows and commands depend on the device, temperature and selected refresh mode. As an illustrative schedule, 8,192 refresh operations in a 64 ms window average 7.8125 microseconds apart. Controllers must obey the part's timing and scheduling limits; affected banks cannot serve ordinary accesses during their refresh operation.

> [!note] Evidence gap
> A blanket DDR4/DDR5 refresh-window rule is omitted because no complete part-specific temperature/mode table was verified for that claim. Use the selected device's datasheet; the arithmetic example is not a controller specification.
- **A different process.** Making capacitors that hold enough charge in a tiny area needs special manufacturing, so commodity main-memory DRAM is commonly on separate dies, adding interface and interconnect costs. Embedded DRAM and integrated/stacked arrangements also exist; off-chip placement is not part of the definition of DRAM.

| | SRAM | DRAM |
|---|---|---|
| Cell | 6 transistors | 1 transistor + capacitor |
| Retention | while powered | ms; needs refresh |
| Read | non-destructive | destructive, rewritten |
| Typical use | registers, caches | main memory |
| Latency | depends on array and interface; usually favoured for low latency | depends on device, row state and interface |
| Cost per bit | high | low |

> [!example] Rowhammer
> DRAM cells are now so small and close together that repeatedly activating one row can disturb the charge in neighbouring rows. In 2014, researchers showed that hammering a row hundreds of thousands of times between refreshes could flip bits next door, and later work turned this into privilege-escalation exploits. Targeted refresh and error-correcting schemes can reduce risk, but neither generic TRR nor unspecified ECC guarantees immunity; effectiveness depends on the exact memory/controller and threat model. It is a reminder that the abstraction "memory holds bits" rests on analogue physics.

## Describing hardware: Verilog

Large digital designs are commonly described using RTL, alongside generated blocks and custom-designed circuit macros. Engineers write **register-transfer level (RTL)** descriptions in a hardware description language (HDL), mainly **Verilog**/**SystemVerilog** or **VHDL**, and a **synthesis** tool turns them into a netlist of gates and flip-flops from a cell library (or LUTs on an FPGA).

The crucial mental shift: Verilog looks like a programming language, but it describes **hardware that all exists and runs at once**, not one CPU executing the whole file sequentially. Procedural statements within a block still follow simulation scheduling and statement order.

### Combinational logic

The full adder from lesson 4:

```verilog
module full_adder(
  input  a, b, cin,
  output s, cout
);
  assign s    = a ^ b ^ cin;
  assign cout = (a & b) | (cin & (a ^ b));
endmodule
```

An `assign` is a permanent connection: whenever an input changes, the output follows, just like a gate. The two `assign` lines are two pieces of hardware side by side; their order is irrelevant.

In real designs you would just write `assign {cout, s} = a + b + cin;` and let the synthesis tool choose an adder structure (ripple, prefix and so on) that meets the timing target.

### Sequential logic

A 4-bit register with synchronous reset and a load enable:

```verilog
module reg4(
  input            clk, rst, load,
  input      [3:0] d,
  output reg [3:0] q
);
  always @(posedge clk)
    if (rst)       q <= 4'b0000;
    else if (load) q <= d;
endmodule
```

- `always @(posedge clk)` means "at each rising edge", so `q` becomes four D flip-flops.
- When neither condition holds, `q` keeps its value. Synthesis implements that with the mux in front of each D input, exactly as in lesson 5.
- `4'b0000` is a literal: 4 bits wide, binary.

### The FSM from lesson 5

The "two 1s in a row" Moore machine, written the standard way with one block for the state register and one for the next-state logic:

```verilog
module two_ones(
  input  clk, rst, x,
  output z
);
  localparam S0 = 2'b00, S1 = 2'b01,
             S2 = 2'b10;
  reg [1:0] state, next;

  always @(posedge clk)
    if (rst) state <= S0;
    else     state <= next;

  always @(*)
    case (state)
      S0:      next = x ? S1 : S0;
      S1:      next = x ? S2 : S0;
      S2:      next = x ? S2 : S0;
      default: next = S0;
    endcase

  assign z = (state == S2);
endmodule
```

Compare it with the block diagram of an FSM: the first `always` block is the state register, the second is the next-state logic, and the `assign` is the Moore output logic. The `default` branch sends the unused code `11` back to S0, in the RTL simulation. This is not a general physical fault-recovery guarantee: synthesis may optimize unreachable encodings or re-encode the FSM. Use the tool's safe-state options and verify the synthesized implementation if illegal-state recovery is required. The synthesis tool derives the gate equations (and may re-encode the states, for example as one-hot).

### Blocking vs non-blocking assignment

Verilog has two assignment operators, and mixing them up is the most common beginner bug:

- `<=` (**non-blocking**): a right-hand side is evaluated when its statement executes and the update is scheduled for the non-blocking-assignment region. In this race-free same-edge example, both right-hand sides read the old values. This models flip-flops, which all sample on the same edge. Use it in `always @(posedge clk)` blocks.
- `=` (**blocking**): updates immediately, so later lines see the new value. Use it in combinational `always @(*)` blocks.

```verilog
always @(posedge clk) begin
  a <= b;   // both read the old values:
  b <= a;   // a and b swap every cycle
end
```

With `=` instead, `a = b;` would happen first and `b = a;` would then copy the *new* `a`, so both end up holding the old `b`. In hardware terms you described a different circuit from the one you meant.

### Pitfalls

- **Accidental latches.** In an `always @(*)` block, every output must be assigned on every path. If you write `if (en) y = d;` with no `else`, `y` must remember its old value when `en = 0`, and synthesis builds a transparent latch, with all the timing problems from lesson 5. Always add an `else` or a `default`.
- **Simulation-only code.** Simulation delays such as #5 do not specify physical gate delay in ordinary RTL synthesis. Some FPGA flows do synthesize supported initial blocks into power-up register or memory initialization; other constructs and ASIC flows differ. Check the target tool's supported subset.
- **Thinking in software.** A synthesizable fixed-bound loop may be unrolled, but data dependencies can make a combinational chain and optimizations can share or remove logic. A 1,000-iteration source loop does not guarantee exactly 1,000 physical copies. Explicit state/control is needed to spread work across clock cycles.

### From RTL to silicon

The flow after writing RTL is roughly:

1. **Simulate** with a testbench to check behaviour.
2. **Synthesise** into a gate-level netlist (lessons 2 and 3 done automatically, with multi-level optimisation).
3. **Place and route**: position every cell and draw every wire.
4. **Static timing analysis**: check setup and hold on every path (lesson 5), inserting buffers to fix hold violations.
5. For an FPGA, the result is a bitstream that configures LUTs and routing; for an ASIC, it is masks for fabrication.

## Key takeaways
- A datapath is registers, an ALU, memories and muxes; the control unit decodes each instruction into mux selects and write enables.
- The teaching register file uses a write decoder and read muxes, with combinational reads and clocked writes. Other implementations have different port and timing choices.
- In the illustrated single-cycle subset, the load path sets the clock bound; pipelining can improve throughput but adds hazards and stage overhead.
- The illustrated SRAM cell is 6T and the DRAM cell is 1T1C. SRAM holds while powered without periodic refresh; DRAM activation disturbs charge and restores it, and refresh follows device-specific requirements. Other cell variants and embedded DRAM exist.
- Verilog describes parallel hardware. Use `assign` and `always @(*)` with `=` for combinational logic, `always @(posedge clk)` with `<=` for flip-flops, and always assign every output on every path to avoid latches.

## Further reading
- [Register file — Wikipedia](https://en.wikipedia.org/wiki/Register_file)
- [Datapath — Wikipedia](https://en.wikipedia.org/wiki/Datapath)
- [Static random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory refresh — Wikipedia](https://en.wikipedia.org/wiki/Memory_refresh)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
- [Verilog — Wikipedia](https://en.wikipedia.org/wiki/Verilog)
- [Logic synthesis — Wikipedia](https://en.wikipedia.org/wiki/Logic_synthesis)
