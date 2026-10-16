---
id: emb-mcu-firmware-chip-memory
sourceLesson: emb-mcu-firmware
title: "What is on a microcontroller?"
level: basic
minutes: 3
summary: "Separate persistent program storage from volatile working memory."
---

A desktop program runs on top of an operating system that loads it, gives it memory, and cleans up when it crashes. A bare-metal microcontroller synth has no general-purpose OS managing the application. Firmware starts through the reset/start-up path and normally keeps running. Interrupt handlers, library code and optional RTOS tasks also execute; watchdogs or fault handlers may recover a crash if configured.

This lesson builds the mental model you need before touching a board: what is on the chip, how your code gets there, and how to get a board back when you have broken it.

## What a microcontroller is

A **microcontroller (MCU)** is a whole small computer on one chip:

- **CPU core.** Audio-oriented boards commonly use an Arm Cortex-M7, a 32-bit core; the STM32H750 and i.MX RT1062 implementations used here include a hardware floating-point unit.
- **Flash.** Non-volatile memory that holds your program and constant data. It survives power-off.
- **RAM.** Volatile working memory: stack, variables, sample buffers. Lost at power-off.
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

The peripherals are the reason MCUs suit instruments. A serial audio peripheral plus DMA can move samples to a codec without the CPU copying each sample; competition for memory-bus bandwidth shared by CPU and DMA, cache coherency and buffer placement still need platform-specific handling. A timer can trigger ADC reads at a steady rate. The CPU is left free for DSP.

### A concrete example: the Daisy Seed's memory

The Daisy Seed (Rev 7, datasheet v1.2.0, checked 2026-10-16) has an Arm Cortex-M7 running at 480 MHz; libDaisy builds for ST's STM32H750IB (its linker script is named after that part). Electro-Smith's bootloader guide shows the memory regions a build reports, including:

| Region | Size | Notes |
|---|---|---|
| Internal flash | 128 KB | On the MCU |
| SRAM | 512 KB | On the MCU |
| DTCM RAM | 128 KB | Fast, tightly coupled memory |
| SDRAM | 64 MB | External chip |
| QSPI application region | 7,936 KB | Within the 8 MB external flash |

Two lessons hide in that table. First, "8 MB of flash" on a product page may mean an *external* chip, which is slower than internal flash. Second, memory is not one big pool. The fetched bootloader guide reserves the top 32 kB of its 512 kB SRAM execution region, leaving up to roughly 480 kB for a SRAM-hosted image. This is an execution-region limit, not the total data-memory capacity. Where code and buffers live affects speed, so the linker script (the file that tells the build where each section goes) matters on embedded targets.

## Key takeaways
- Separate persistent program storage from volatile working memory.
- Read the linker memory regions rather than treating all RAM or flash as one pool.

## Further reading
- [Daisy Seed hardware page and datasheet — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy C++ development environment (DFU, ST-Link) — Electro-Smith](https://docs.daisy.audio/tutorials/cpp-dev-env/)
- [Getting started: Daisy bootloader — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/doc/md/_a7_Getting-Started-Daisy-Bootloader.md)
- [Teensy 4.1 (programming, bootloader, recovery) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bootloader chip for Teensy 4.x — PJRC](https://www.pjrc.com/store/ic_mkl02_t4.html)
- [Microcontroller — Wikipedia](https://en.wikipedia.org/wiki/Microcontroller)
- [JTAG — Wikipedia](https://en.wikipedia.org/wiki/JTAG)
