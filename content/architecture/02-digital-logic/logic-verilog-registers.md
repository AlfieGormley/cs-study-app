---
id: logic-verilog-registers
title: Describe combinational and clocked hardware
level: advanced
minutes: 3
sourceLesson: logic-datapath-memory
summary: Concurrent HDL blocks describe hardware that operates in parallel.
---

## Describing hardware: Verilog

Large digital designs are commonly described using RTL, alongside generated blocks and custom-designed circuit macros. Engineers write **register-transfer level (RTL)** descriptions in a hardware description language (HDL), mainly **Verilog**/**SystemVerilog** or **VHDL**, and a **synthesis** tool turns them into a netlist of gates and flip-flops from a cell library (or LUTs on an FPGA).

The crucial mental shift: Verilog looks like a programming language, but it describes **hardware that all exists and runs at once**, not one CPU executing the whole file sequentially. Procedural statements within a block still follow simulation scheduling and statement order.

### Combinational logic

The full adder from adder lessons:

```verilog
module full_adder(
  input  a, b, cin,
  output s, cout
);
  // The sum keeps odd parity of three bits.
  assign s    = a ^ b ^ cin;
  // Generate or propagate the carry.
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
  // Reset wins over load at the same edge.
  always @(posedge clk)
    if (rst)       q <= 4'b0000;
    else if (load) q <= d;
endmodule
```

- `always @(posedge clk)` means "at each rising edge", so `q` becomes four D flip-flops.
- When neither condition holds, `q` keeps its value. Synthesis implements that with the mux in front of each D input, exactly as in sequential-logic lessons.
- `4'b0000` is a literal: 4 bits wide, binary.

## Key takeaways
- Concurrent HDL blocks describe hardware that operates in parallel.
- Continuous assignments model combinational functions; clocked non-blocking updates model registers.

## Further reading
- [Icarus Verilog — simulation semantics and examples](https://steveicarus.github.io/iverilog/usage/simulation.html)
- [Cummings — Nonblocking assignments in Verilog synthesis](https://ftp.sigmet.vaisala.com/files/custom/vaisala/ProgrammingDocs/Verilog/CummingsSNUG2000SJ_NBA.pdf)
- [Yosys — procedural synthesis](https://yosyshq.readthedocs.io/projects/yosys/en/latest/using_yosys/synthesis/proc.html)
- [RISC-V — RV64I base integer ISA](https://docs.riscv.org/reference/isa/unpriv/rv64.html)
- [Register file — Wikipedia](https://en.wikipedia.org/wiki/Register_file)
- [Datapath — Wikipedia](https://en.wikipedia.org/wiki/Datapath)
- [Static random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory refresh — Wikipedia](https://en.wikipedia.org/wiki/Memory_refresh)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
- [Verilog — Wikipedia](https://en.wikipedia.org/wiki/Verilog)
- [Logic synthesis — Wikipedia](https://en.wikipedia.org/wiki/Logic_synthesis)
