---
id: emb-mcu-firmware-boot-recovery
sourceLesson: emb-mcu-firmware
title: "Bootloaders and deliberate recovery"
level: basic
minutes: 3
summary: "A ROM or separate-chip loader provides recovery independent of application code."
---

## Bootloaders and DFU

A **bootloader** is a small program that can receive new firmware and write it to flash. Recovery is most robust when the bootloader is protected from application writes. ROM and separate-chip loaders provide that separation; a flash-resident second-stage loader can be overwritten and may need restoring via the ROM loader.

- **ST system bootloader.** STM32 chips have a factory bootloader in read-only memory. On the Daisy Seed you enter it by holding BOOT and pressing RESET. It then appears on USB as a **DFU** (Device Firmware Upgrade, a standard USB class) device and a tool such as `dfu-util`, or Electro-Smith's web programmer, writes the firmware. Electro-Smith notes this route can only program the chip's internal 128 KB flash.
- **Daisy bootloader.** An optional second-stage bootloader from Electro-Smith that sits in internal flash and loads larger programs into SRAM or QSPI flash. After reset it waits a 2.5-second bootloader waiting interval for DFU or a valid binary on SD card or USB drive.
- **Teensy 4.x.** PJRC puts the bootloader on a separate chip on the board, so flashing your program cannot erase it. The Teensy Loader application flashes `.hex` files; normally the IDE triggers it automatically.
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

## Key takeaways
- A ROM or separate-chip loader provides recovery independent of application code.
- Record and practise the exact recovery sequence for your board and security state.

## Further reading
- [Daisy Seed hardware page and datasheet — Electro-Smith](https://docs.daisy.audio/hardware/Seed/)
- [Daisy C++ development environment (DFU, ST-Link) — Electro-Smith](https://docs.daisy.audio/tutorials/cpp-dev-env/)
- [Getting started: Daisy bootloader — libDaisy](https://github.com/electro-smith/libDaisy/blob/master/doc/md/_a7_Getting-Started-Daisy-Bootloader.md)
- [Teensy 4.1 (programming, bootloader, recovery) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Bootloader chip for Teensy 4.x — PJRC](https://www.pjrc.com/store/ic_mkl02_t4.html)
- [Microcontroller — Wikipedia](https://en.wikipedia.org/wiki/Microcontroller)
- [JTAG — Wikipedia](https://en.wikipedia.org/wiki/JTAG)
