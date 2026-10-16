---
id: emb-mcu-firmware-digital-approaches
sourceLesson: emb-mcu-firmware
title: "Three digital synth approaches"
level: basic
minutes: 2
summary: "Compare complete systems: integrated audio MCU, MCU plus converter, or Linux computer."
---

## Three ways to build a digital synth

The project's hardware framework lists three digital approaches. They differ in where the hard work lands.

**1. Audio-focused MCU board** (for example Daisy Seed). The MCU, codec, audio clocks and a library that starts the audio callback are all done for you. You write DSP and control code. You inherit the board's choices: its codec, its output level, its pinout.

**2. General MCU plus a separate codec** (for example a Teensy 4.x with PJRC's audio adaptor, or any MCU with a codec breakout). You choose and wire the codec, configure it, and get the clocks right. Teensy's audio library hides much of this; a bare MCU leaves all of it to you. More integration learning, more ways to get no sound at all.

**3. Small Linux computer** (for example Raspberry Pi with an audio HAT). A full OS, a filesystem, networking, and a large CPU. Audio runs through ALSA (Linux's audio layer) with OS buffering. A general-purpose Linux system provides convenience but adds scheduling and buffering to the deadline analysis. It takes time to boot and should shut down cleanly when using writable storage. Bare-metal code also needs bounded work, correct priorities and measurements; it does not acquire determinism merely by omitting an OS.

| | MCU board | MCU + codec | Linux SBC |
|---|---|---|---|
| Boot time | Measure firmware | Measure firmware | Measure OS setup |
| Timing | Interrupt/deadline design | Interrupt/deadline design | OS-scheduled |
| Audio setup | Done | Your job | Drivers/HAT |
| Debugging | Probe or prints | Varies | Full Linux tools |

None of these is "best". The platform-comparison units give a method for comparing them against the project's criteria.

## Key takeaways
- Compare complete systems: integrated audio MCU, MCU plus converter, or Linux computer.
- Boot behavior, deadlines and power-off robustness need checking for the actual system.

## Further reading
- [Daisy Seed hardware page and datasheet — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy C++ development environment (DFU, ST-Link) — Electro-Smith](https://docs.daisy.audio/tutorials/cpp-dev-env/)
- [Getting started: Daisy bootloader — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/doc/md/_a7_Getting-Started-Daisy-Bootloader.md)
- [Teensy 4.1 (programming, bootloader, recovery) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bootloader chip for Teensy 4.x — PJRC](https://www.pjrc.com/store/ic_mkl02_t4.html)
- [Microcontroller — Wikipedia](https://en.wikipedia.org/wiki/Microcontroller)
- [JTAG — Wikipedia](https://en.wikipedia.org/wiki/JTAG)
