---
id: esb-mcu-memory-peripherals
title: CPU, memory and peripherals
level: basic
minutes: 3
summary: Separate instruction execution, persistent storage, working memory and hardware interfaces.
---

A **microcontroller** combines one or more processor cores, memory and hardware interfaces in a chip. The exact mixture varies. The development board around it may add more memory, power circuitry, connectors and other components.

The **CPU**, or central processing unit, executes instructions. It uses **RAM**, random-access memory, for working data such as changing variables and temporary buffers. The SRAM commonly used by small MCUs is **volatile memory**: its contents are not retained when power is removed.

**Flash memory** is non-volatile storage that can hold firmware and persistent data. It may be inside the MCU or on a separate chip. As a concrete distinction, RP2040 has on-chip SRAM and accesses external flash through its flash interface. Do not assume that a board's advertised flash capacity describes memory inside its processor.

## Give each part a job

For the sensor indicator introduced earlier:

| Part | Job in the example |
|---|---|
| CPU | Execute the measurement decision |
| Firmware storage | Retain the program when power is removed |
| RAM | Hold the current measurement and state |
| Peripheral | Exchange signals with the sensor or indicator |

A **peripheral** is a dedicated hardware block such as a timer or a serial controller. Software configures it and observes or supplies data. The peripheral can perform its configured hardware work between CPU instructions; it does not decide the application's requirements for you.

> [!analogy] Real-world analogy: a workshop with instructions and a workbench
> A workshop keeps instructions in a cupboard, places the current job on a workbench and uses specialised tools for particular operations.
>
> **How it maps:** Stored instructions represent firmware storage; the workbench represents working RAM; the worker following instructions represents the CPU. Specialised tools represent peripherals.
>
> **Where it stops:** Actual memory has defined addresses and access rules. Some systems execute code from RAM, and a peripheral's registers are not ordinary storage just because software accesses them by address.

## Addresses describe different kinds of access

A **memory map** describes which addresses refer to memory and which refer to hardware. A **peripheral register** is a location used to control or observe a hardware function. For example, one register can select a pin's function while another reports an input value.

Access can cause **register side effects**: reading or writing a peripheral register is not automatically equivalent to reading or writing a RAM variable. Later lessons use the relevant device manual or SDK rather than guessing addresses.

Try a mental power cycle. The saved firmware can remain in flash, but the current working measurement is not a persistent record merely because it was stored in RAM. To retain a setting, the application needs an appropriate supported storage mechanism and a defined loading process.

## Key takeaways
- Distinguish firmware storage from the RAM used while the program runs.
- MCU and board memory are different descriptions; check the actual device.
- Peripherals and their registers have device-specific behaviour.

## Further reading
- [RP2040 datasheet: memory and peripheral descriptions](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [Pico board memory and storage — Raspberry Pi](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/microcontrollers/pico-series/about_pico.adoc)
