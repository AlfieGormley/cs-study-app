---
id: emb-mcu-firmware
title: Microcontrollers and firmware
level: basic
minutes: 12
summary: What a microcontroller is, how firmware differs from an application, the build-flash-run-debug cycle, bootloaders, DFU, SWD/JTAG probes, recovering a board, and the three broad hardware approaches for a synth.
---

A desktop program runs on top of an operating system that loads it, gives it memory, and cleans up when it crashes. A synth built on a microcontroller has none of that. Your code *is* the only thing running. It starts when power arrives, it must never exit, and if it crashes, the sound stops and nothing restarts it unless you planned for that.

This lesson builds the mental model you need before touching a board: what is on the chip, how your code gets there, and how to get a board back when you have broken it.

## What a microcontroller is

A **microcontroller (MCU)** is a whole small computer on one chip:

- **CPU core.** Audio-oriented boards commonly use an Arm Cortex-M7, a 32-bit core with a hardware floating-point unit.
- **Flash.** Non-volatile memory that holds your program and constant data. It survives power-off.
- **RAM.** Volatile working memory: stack, variables, audio buffers. Lost at power-off.
- **Peripherals.** Dedicated hardware blocks that do jobs without the CPU: GPIO pins, ADCs, DACs, timers, UART/I2C/SPI controllers, a serial audio interface (SAI or I2S), USB and DMA engines.

```diagram
+------------------- MCU ------------------+
|  CPU core  <--bus-->  Flash   RAM        |
|     |                                    |
|     +--bus-->  GPIO  ADC  Timers  DMA    |
|                UART  I2C  SPI  SAI/I2S   |
+------------------------------------------+
        |pins|            |pins|
     buttons, pots     codec, MIDI, display
```

The peripherals are the reason MCUs suit instruments. A serial audio peripheral plus DMA can move samples to a codec with no CPU involvement between blocks. A timer can trigger ADC reads at a steady rate. The CPU is left free for DSP.

### A concrete example: the Daisy Seed's memory

The Daisy Seed (Rev 7, datasheet v1.2.0, checked 2026-10-04) has an Arm Cortex-M7 running at 480 MHz; libDaisy builds for ST's STM32H750IB (its linker script is named after that part). Electro-Smith's bootloader guide shows the memory regions a build reports, including:

| Region | Size | Notes |
|---|---|---|
| Internal flash | 128 KB | On the MCU |
| SRAM | 512 KB | On the MCU |
| DTCM RAM | 128 KB | Fast, tightly coupled |
| SDRAM | 64 MB | External chip |
| QSPI application region | 7,936 KB | Within the 8 MB external flash |

Two lessons hide in that table. First, "8 MB of flash" on a product page may mean an *external* chip, which is slower than internal flash. Second, memory is not one big pool. Where code and buffers live affects speed, so the linker script (the file that tells the build where each section goes) matters on embedded targets.

## Firmware versus an application

**Firmware** is the program that runs directly on the hardware. The following comparison describes a simple bare-metal program; MCUs can also run an RTOS, and reset/recovery behaviour depends on firmware and watchdogs. Compared with a desktop application:

| Desktop app | MCU firmware |
|---|---|
| OS loads and runs it | Runs from reset |
| Exits when done | Never returns |
| Virtual memory, big heap | Fixed, small memory |
| Crash is caught by OS | Crash hangs the device |
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

The audio work happens in a callback driven by interrupts, which later lessons cover. The `loop forever` part is the **foreground** or **main loop**.

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

## Bootloaders and DFU

A **bootloader** is a small program that can receive new firmware and write it to flash. Recovery is most robust when the bootloader is protected from application writes. ROM and separate-chip loaders provide that separation; a flash-resident second-stage loader can be overwritten and may need restoring via the ROM loader.

- **ST system bootloader.** STM32 chips have a factory bootloader in read-only memory. On the Daisy Seed you enter it by holding BOOT and pressing RESET. It then appears on USB as a **DFU** (Device Firmware Upgrade, a standard USB class) device and a tool such as `dfu-util`, or Electro-Smith's web programmer, writes the firmware. Electro-Smith notes this route can only program the chip's internal 128 KB flash.
- **Daisy bootloader.** An optional second-stage bootloader from Electro-Smith that sits in internal flash and loads larger programs into SRAM or QSPI flash. After reset it waits a 2.5-second grace period for DFU or a valid binary on SD card or USB drive.
- **Teensy 4.x.** PJRC puts the bootloader on a separate chip on the board, so flashing your program cannot erase it. The Teensy Loader application flashes `.hex` files; normally the IDE triggers it automatically.

## Debug probes: SWD and JTAG

A **debug probe** connects your computer to the MCU's debug port. Arm cores expose **SWD** (Serial Wire Debug, two signals plus ground) and often **JTAG** (an older, wider standard). Through the probe a debugger such as GDB can:

- flash firmware without a bootloader;
- halt the CPU, set breakpoints, single-step;
- read variables, registers and memory while stopped;
- see where a crash (a *hard fault*) happened.

Electro-Smith's getting-started guide recommends the ST-Link V3 Mini for the Daisy Seed, with OpenOCD doing the flashing and GDB the debugging from VS Code.

On a stock Teensy 4.x, the main processor's JTAG port is used by PJRC's bootloader chip: PJRC's bootloader-chip page says the i.MX RT is configured to communicate using JTAG, and that locking secure mode disables JTAG access. PJRC does not document a header or supported workflow for attaching your own SWD/JTAG probe. Debugging there is usually serial printing from the main loop, plus measurement (cycle counter, GPIO toggles). Check PJRC's current pages before relying on this.

> [!warning] Breakpoints and audio
> Halting the CPU at a breakpoint stops the audio callback. The codec keeps clocking out whatever is in its buffer, which often means a loud repeating buzz. Turn the monitoring level down before stepping through audio code.

## Recovering a board

Sooner or later you will flash something that hangs before USB starts, so the IDE can no longer reach the board. This is normal, and it is why hardware bootloaders exist.

| Board | Recovery path |
|---|---|
| Daisy Seed | Hold BOOT, press RESET: ROM DFU |
| Daisy Seed | Debug probe over SWD |
| Teensy 4.x | Press Program button |
| Teensy 4.x | Hold Program 13–17 s: wipe |

PJRC states that holding the Program button between 13 and 17 seconds fully erases the flash and restores a simple LED-blink program. Its bootloader-chip page adds a catch: the known-good blink copy is written on the first ordinary press, so the long-press restore only works if the button has been pressed briefly at least once before. Neither path needs your broken firmware to cooperate, because the code doing the recovery is outside the region you can overwrite.

The diy-synth roadmap asks you to "build, flash, and recover a minimal board example from a clean checkout". Do the recovery deliberately, once, before you need it in a panic.

## Three ways to build a digital synth

The project's hardware framework lists three digital approaches. They differ in where the hard work lands.

**1. Audio-focused MCU board** (for example Daisy Seed). The MCU, codec, audio clocks and a library that starts the audio callback are all done for you. You write DSP and control code. You inherit the board's choices: its codec, its output level, its pinout.

**2. General MCU plus a separate codec** (for example a Teensy 4.x with PJRC's audio adaptor, or any MCU with a codec breakout). You choose and wire the codec, configure it, and get the clocks right. Teensy's audio library hides much of this; a bare MCU leaves all of it to you. More integration learning, more ways to get no sound at all.

**3. Small Linux computer** (for example Raspberry Pi with an audio HAT). A full OS, a filesystem, networking, and a large CPU. Audio runs through ALSA (Linux's audio layer) with OS buffering. You trade bare-metal determinism for convenience: the board takes time to boot, needs a clean shutdown to protect its SD card, and timing depends on the OS scheduler.

| | MCU board | MCU + codec | Linux SBC |
|---|---|---|---|
| Boot time | Instant | Instant | Seconds |
| Timing | Deterministic | Deterministic | OS-scheduled |
| Audio setup | Done | Your job | Drivers/HAT |
| Debugging | Probe or prints | Varies | Full Linux tools |

None of these is "best". Lesson 8 gives a method for comparing them against the project's criteria.

## Key takeaways
- An MCU combines CPU, flash, RAM and peripherals on one chip; the peripherals (DMA, SAI/I2S, ADC, timers) do much of an instrument's I/O work.
- Firmware runs from reset, never exits, and has no OS to catch crashes.
- The cycle is edit, cross-compile, link, flash, run, debug. Flash via a USB bootloader (DFU, Teensy Loader) or a debug probe (SWD/JTAG).
- A bootloader in protected memory (ST's ROM bootloader, Teensy's separate chip) is what makes a "bricked" board recoverable. Practise recovery early.
- Product pages blur internal and external memory; read the datasheet and the build's memory report.

## Further reading
- [Daisy Seed hardware page and datasheet — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy C++ development environment (DFU, ST-Link) — Electro-Smith](https://docs.daisy.audio/tutorials/cpp-dev-env/)
- [Getting started: Daisy bootloader — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/doc/md/_a7_Getting-Started-Daisy-Bootloader.md)
- [Teensy 4.1 (programming, bootloader, recovery) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bootloader chip for Teensy 4.x — PJRC](https://www.pjrc.com/store/ic_mkl02_t4.html)
- [Microcontroller — Wikipedia](https://en.wikipedia.org/wiki/Microcontroller)
- [JTAG — Wikipedia](https://en.wikipedia.org/wiki/JTAG)
