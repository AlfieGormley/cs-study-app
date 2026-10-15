---
id: logic-dram-refresh
title: DRAM charge, row buffers and refresh
level: advanced
minutes: 4
sourceLesson: logic-datapath-memory
summary: DRAM activation senses and restores a row of capacitor-stored bits.
---

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
- **Rows, not words.** Activating a word line reads an entire row into the sense amplifiers, which act as a **DRAM row buffer**. Further reads from the same open row are much faster than opening a new one. This is why access patterns matter so much for DRAM performance (module 5).
- **Charge leaks.** A capacitor slowly loses its charge, so every cell must be read and rewritten periodically. Refresh windows and commands depend on the device, temperature and selected refresh mode. As an illustrative schedule, 8,192 refresh operations spread evenly over a 64 ms window are this far apart:

```formula
t_REFI = t_window / N_refresh
t_REFI = 64 ms / 8192
t_REFI = 64000 µs / 8192 = 7.8125 µs
where
t_REFI: the average interval between refresh commands (the name DDR datasheets use)
t_window: the time within which every row must be refreshed, here 64 milliseconds (ms)
N_refresh: the number of refresh commands in that window, here 8,192; each one refreshes a group of rows
ms: milliseconds, 10^-3 seconds
µs: microseconds, 10^-6 seconds; 1 ms = 1000 µs
In words: 8,192 evenly spaced refreshes in 64 ms means one about every 7.8 microseconds.
```

Controllers must obey the part's timing and scheduling limits; affected banks cannot serve ordinary accesses during their refresh operation.

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

## Key takeaways
- DRAM activation senses and restores a row of capacitor-stored bits.
- Refresh requirements and disturbance mitigations depend on the device and operating conditions.

## Further reading
- [CMU — Memory and processor bus](https://course.ece.cmu.edu/~ece348/lectures/08_bus_memory_handouts.pdf)
- [Original Rowhammer paper](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca14.pdf)
- [TRRespass — targeted refresh limitations](https://download.vusec.net/papers/trrespass_sp20.pdf)
- [ECCploit — error correction and Rowhammer](https://download.vusec.net/papers/eccploit_sp19.pdf)
- [RISC-V — RV64I base integer ISA](https://docs.riscv.org/reference/isa/unpriv/rv64.html)
- [Register file — Wikipedia](https://en.wikipedia.org/wiki/Register_file)
- [Datapath — Wikipedia](https://en.wikipedia.org/wiki/Datapath)
- [Static random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory refresh — Wikipedia](https://en.wikipedia.org/wiki/Memory_refresh)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
- [Verilog — Wikipedia](https://en.wikipedia.org/wiki/Verilog)
- [Logic synthesis — Wikipedia](https://en.wikipedia.org/wiki/Logic_synthesis)
