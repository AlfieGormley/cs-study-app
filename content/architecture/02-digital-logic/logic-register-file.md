---
id: logic-register-file
title: A register file from muxes and decoders
level: advanced
minutes: 3
sourceLesson: logic-datapath-memory
summary: A teaching register file combines write decoding with read multiplexers.
---

The previous lessons built the parts: gates, adders, muxes, decoders, flip-flops and state machines. This lesson puts them together. A processor is a **datapath** (the registers, ALU, memories and muxes that data flows through) plus a **control unit** (the logic that decides, for each instruction, which way every mux points and which storage gets written).

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

- In this teaching register file, reading is combinational: the register number drives the select lines of a 32-to-1 mux (5 select bits, since five bits can name 2 × 2 × 2 × 2 × 2 = 32 registers). The value appears as soon as the mux settles.
- **Writing** happens at the clock edge: the decoder turns `rd` into a one-hot signal, ANDed with the `RegWrite` control signal, which enables the load input of exactly one register (the "mux in front of D" trick from sequential-logic lessons).
- x0 always reads as zero and discards writes. The implementation can return a constant rather than allocate an ordinary storage cell; merely disabling writes to an uninitialised cell would not guarantee zero.

Wide out-of-order designs need substantial operand-access bandwidth. A single multiported array adds circuitry and wiring as ports increase. BOOM illustrates separate integer and floating-point files with ports matched to its execution units; providing fewer ports can require arbitration and re-issue. Register access is one resource that can constrain issue width, rather than every processor requiring one particular port count.

## Key takeaways
- A teaching register file combines write decoding with read multiplexers.
- RISC-V register semantics are architectural; the port structure is an implementation choice.

## Further reading
- [BOOM — register files and bypass networks](https://docs.boom-core.org/en/latest/sections/reg-file-bypass-network.html)
- [RISC-V — RV64I base integer ISA](https://docs.riscv.org/reference/isa/unpriv/rv64.html)
- [Register file — Wikipedia](https://en.wikipedia.org/wiki/Register_file)
- [Datapath — Wikipedia](https://en.wikipedia.org/wiki/Datapath)
- [Static random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory refresh — Wikipedia](https://en.wikipedia.org/wiki/Memory_refresh)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
- [Verilog — Wikipedia](https://en.wikipedia.org/wiki/Verilog)
- [Logic synthesis — Wikipedia](https://en.wikipedia.org/wiki/Logic_synthesis)
