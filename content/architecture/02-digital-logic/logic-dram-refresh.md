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
- **Charge leaks.** Stored charge degrades, so the memory must periodically sense and restore its rows even when software makes no accesses. Refresh windows, commands and scheduling limits depend on the device, temperature and selected mode. Shortening the allowed refresh window while retaining the same command count requires more frequent refreshes.

Controllers must obey the selected part's timing and scheduling limits; affected banks cannot serve ordinary accesses during their refresh operation. A generic interval is not a controller specification.

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
