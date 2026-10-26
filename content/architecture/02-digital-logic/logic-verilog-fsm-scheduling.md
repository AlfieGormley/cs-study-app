---
id: logic-verilog-fsm-scheduling
title: Verilog FSMs, scheduling and synthesis
level: advanced
minutes: 4
sourceLesson: logic-datapath-memory
summary: Non-blocking assignments preserve old-value sampling in the race-free example.
---

### The FSM from sequential-logic lessons

The "two 1s in a row" Moore machine, written the standard way with one block for the state register and one for the next-state logic:

```verilog
module two_ones(
  input  clk, rst, x,
  output z
);
  localparam S0 = 2'b00, S1 = 2'b01,
             S2 = 2'b10;
  reg [1:0] state, next;

  // Capture state at each rising edge.
  always @(posedge clk)
    if (rst) state <= S0;
    else     state <= next;

  // Assign every branch: no storage here.
  always @(*)
    case (state)
      S0:      next = x ? S1 : S0;
      S1:      next = x ? S2 : S0;
      S2:      next = x ? S2 : S0;
      default: next = S0;
    endcase

  // Moore output uses only stored state.
  assign z = (state == S2);
endmodule
```

Compare it with the block diagram of an FSM: the first `always` block is the state register, the second is the next-state logic, and the `assign` is the Moore output logic. The `default` branch sends the unused code `11` back to S0, in the RTL simulation. This is not a general physical fault-recovery guarantee: synthesis may optimize unreachable encodings or re-encode the FSM. Use the tool's safe-state options and verify the synthesized implementation if illegal-state recovery is required. The synthesis tool derives the gate equations (and may re-encode the states, for example as one-hot).

### Blocking vs non-blocking assignment

Verilog has two assignment operators, and mixing them up is the most common beginner bug:

- `<=` (**non-blocking assignment**): a right-hand side is evaluated when its statement executes and the update is scheduled for the non-blocking-assignment region. In this race-free same-edge example, both right-hand sides read the old values. This models flip-flops, which all sample on the same edge. Use it in `always @(posedge clk)` blocks.
- `=` (**blocking**): updates immediately, so later lines see the new value. Use it in combinational `always @(*)` blocks.

```verilog
always @(posedge clk) begin
  a <= b;   // both read the old values:
  b <= a;   // a and b swap every cycle
end
```

With `=` instead, `a = b;` would happen first and `b = a;` would then copy the *new* `a`, so both end up holding the old `b`. In hardware terms you described a different circuit from the one you meant.

### Pitfalls

- **Accidental latches.** In intended combinational `always @(*)` logic, assign each output on every path. For independent input signals, `if (en) y = d;` with no `else` retains `y` when enable is low and normally infers a transparent latch. Synthesis may remove unreachable paths or unused storage, so inspect its reports. Supply an `else` or a suitable default to describe combinational behaviour.
- **Simulation-only code.** Simulation delays such as #5 do not specify physical gate delay in ordinary RTL synthesis. Some FPGA flows do synthesize supported initial blocks into power-up register or memory initialization; other constructs and ASIC flows differ. Check the target tool's supported subset.
- **Thinking in software.** A synthesizable fixed-bound loop may be unrolled, but data dependencies can make a combinational chain and optimizations can share or remove logic. A 1,000-iteration source loop does not guarantee exactly 1,000 physical copies. Explicit state/control is needed to spread work across clock cycles.

### From RTL to silicon

The flow after writing RTL is roughly:

1. **Simulate** with a testbench to check behaviour.
2. **Synthesise** into a gate-level netlist (lessons 2 and 3 done automatically, with multi-level optimisation).
3. **Place and route**: position every cell and draw every wire.
4. **Static timing analysis**: check setup and hold on every path (sequential-logic lessons), inserting buffers to fix hold violations.
5. For an FPGA, the result is a bitstream that configures LUTs and routing; for an ASIC, it is masks for fabrication.

## Key takeaways
- Non-blocking assignments preserve old-value sampling in the race-free example.
- Complete combinational assignments avoid unintended latches; synthesis and physical checks follow simulation.

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
