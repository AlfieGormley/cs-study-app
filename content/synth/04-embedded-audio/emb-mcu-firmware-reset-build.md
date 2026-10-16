---
id: emb-mcu-firmware-reset-build
sourceLesson: emb-mcu-firmware
title: "Firmware from reset to flashing"
level: basic
minutes: 2
summary: "A bare-metal program normally keeps foreground work in an endless main loop."
---

## Firmware versus an application

**Firmware** is software closely tied to a device and its hardware. The following comparison describes a simple bare-metal program; MCUs can also run an RTOS, and reset/recovery behaviour depends on firmware and watchdogs. Compared with a desktop application:

| Desktop app | MCU firmware |
|---|---|
| OS loads and runs it | Runs from reset |
| Exits when done | Normally keeps running |
| Virtual memory, big heap | Fixed, small memory |
| OS can terminate a failed app | Fault handler or watchdog determines recovery |
| printf to a terminal | No screen by default |

A typical firmware shape, in language-neutral pseudocode:

```
on reset:
  configure clocks, memory, pins
  configure peripherals (codec, ADC)
  start audio (DMA + callback)
  loop forever:
    read controls, update params
    handle MIDI, blink status LED
```

The audio work happens in a callback driven by interrupts, which later lessons cover. The endless main loop is the **foreground** or **main loop**.
## The build, flash, run, debug cycle

```flow
Edit source on your computer
Cross-compile for the MCU's CPU
Link into an image (.bin, .hex or .elf)
Flash the image into the board's memory
Reset: the MCU runs the new firmware
Observe, measure or debug, then repeat
```

**Cross-compiling** means the compiler runs on your laptop but produces machine code for a different CPU. For Arm Cortex-M boards that is usually a GNU Arm toolchain. The output is a raw binary (`.bin`), an Intel HEX file (`.hex`), or an ELF file (`.elf`) that also carries debug symbols.

**Flashing** writes the image into non-volatile memory. There are two broad ways to do it: through a **bootloader** over USB, or through a **debug probe**.

## Key takeaways
- A bare-metal program normally keeps foreground work in an endless main loop.
- Cross-compilation targets the board; linking decides placement before flashing.

## Further reading
- [Daisy Seed hardware page and datasheet — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy C++ development environment (DFU, ST-Link) — Electro-Smith](https://docs.daisy.audio/tutorials/cpp-dev-env/)
- [Getting started: Daisy bootloader — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/doc/md/_a7_Getting-Started-Daisy-Bootloader.md)
- [Teensy 4.1 (programming, bootloader, recovery) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bootloader chip for Teensy 4.x — PJRC](https://www.pjrc.com/store/ic_mkl02_t4.html)
- [Microcontroller — Wikipedia](https://en.wikipedia.org/wiki/Microcontroller)
- [JTAG — Wikipedia](https://en.wikipedia.org/wiki/JTAG)
