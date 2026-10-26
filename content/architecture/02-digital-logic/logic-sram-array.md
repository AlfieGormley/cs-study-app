---
id: logic-sram-array
title: Memory arrays and the 6T SRAM cell
level: advanced
minutes: 3
sourceLesson: logic-datapath-memory
summary: Word lines select rows and bit lines connect cells to sensing circuits.
---

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

SRAM and DRAM both use row/column organisation, but their cells, sensing, write circuits, timing and peripheral structures differ.

## SRAM: the bistable loop, made addressable

A static RAM cell is the two-inverter loop from sequential-logic lessons plus two **access transistors** that connect it to a pair of complementary bit lines:

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

- **Hold**: the word line is low, the access transistors are off, and the loop keeps its value as long as the chip has power. No refresh is needed: that is what *static* means.
- **Read**: precharge both complementary bit lines high, then raise the word line. The side storing 0 slowly pulls its bit line down. The sense amplifier detects the small difference between the two bit lines and resolves it quickly, long before the bit line has swung fully.
- **Write**: drive the two bit lines hard to the new value and its complement, then raise the word line. The drivers overpower the small inverters and flip the loop.

Transistor sizing is delicate: the cell must be strong enough not to flip during a read, yet weak enough to be overwritten during a write. SRAM integrates with logic processes and provides low-latency storage; actual cache latency depends on size, organization, technology and clock rate, so it is used for **registers, caches, TLBs and buffers**. Its drawback is size: six transistors per bit. Caches often make up a large fraction of a modern CPU die's area.

## Key takeaways
- Word lines select rows and bit lines connect cells to sensing circuits.
- The illustrated 6T SRAM cell holds a bit without periodic refresh while powered.

## Further reading
- [CMU — Memory and processor bus](https://course.ece.cmu.edu/~ece348/lectures/08_bus_memory_handouts.pdf)
- [RISC-V — RV64I base integer ISA](https://docs.riscv.org/reference/isa/unpriv/rv64.html)
- [Register file — Wikipedia](https://en.wikipedia.org/wiki/Register_file)
- [Datapath — Wikipedia](https://en.wikipedia.org/wiki/Datapath)
- [Static random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory refresh — Wikipedia](https://en.wikipedia.org/wiki/Memory_refresh)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
- [Verilog — Wikipedia](https://en.wikipedia.org/wiki/Verilog)
- [Logic synthesis — Wikipedia](https://en.wikipedia.org/wiki/Logic_synthesis)
