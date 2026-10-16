---
id: emb-mcu-firmware-probe-debugging
sourceLesson: emb-mcu-firmware
title: "Debugging a board with a probe"
level: basic
minutes: 2
summary: "A debug probe adds breakpoints, stepping and memory inspection to flashing."
---

## Debug probes: SWD and JTAG

A **debug probe** connects your computer to the MCU's debug port. Arm cores expose **SWD** (Serial Wire Debug, two signals plus ground) and often **JTAG** (an older, wider standard). Through the probe a debugger such as GDB can:

- flash firmware without a bootloader;
- halt the CPU, set breakpoints, single-step;
- read variables, registers and memory while stopped;
- see where a crash (a *hard fault*) happened.

Electro-Smith's getting-started guide recommends the ST-Link V3 Mini for the Daisy Seed, with OpenOCD doing the flashing and GDB the debugging from VS Code.

On a stock Teensy 4.x, the main processor's JTAG port is used by PJRC's bootloader chip: PJRC's bootloader-chip page says the i.MX RT is configured to communicate using JTAG, and that locking secure mode disables JTAG access. PJRC does not document a header or supported workflow for attaching your own SWD/JTAG probe. Debugging there is usually serial printing from the main loop, plus measurement (cycle counter, GPIO toggles). Check PJRC's current pages before relying on this.

> [!warning] Breakpoints and audio
> Halting the CPU at a breakpoint stops the audio callback. Depending on debug freeze settings, serial clocks and DMA may keep running and replay stale samples. That can produce a repeating signal, silence or another fault-dependent result. Turn the monitoring level down before stepping through audio code.

## Key takeaways
- A debug probe adds breakpoints, stepping and memory inspection to flashing.
- Lower monitoring levels before halting audio: stopped computation can leave stale samples.

## Further reading
- [Daisy Seed hardware page and datasheet — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy C++ development environment (DFU, ST-Link) — Electro-Smith](https://docs.daisy.audio/tutorials/cpp-dev-env/)
- [Getting started: Daisy bootloader — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/doc/md/_a7_Getting-Started-Daisy-Bootloader.md)
- [Teensy 4.1 (programming, bootloader, recovery) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bootloader chip for Teensy 4.x — PJRC](https://www.pjrc.com/store/ic_mkl02_t4.html)
- [Microcontroller — Wikipedia](https://en.wikipedia.org/wiki/Microcontroller)
- [JTAG — Wikipedia](https://en.wikipedia.org/wiki/JTAG)
