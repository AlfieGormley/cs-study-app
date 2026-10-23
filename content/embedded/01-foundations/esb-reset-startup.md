---
id: esb-reset-startup
title: From reset to application startup
level: basic
minutes: 3
summary: Trace a documented reset path without assuming every MCU begins directly at main.
---

Resetting a device is not the same operation as flashing new firmware. A **reset** restarts execution through a defined hardware and software path. Programming flash changes stored contents. Either operation may be part of a development tool's sequence, but one does not automatically imply the other.

Your application's first visible action may be turning an indicator on. Before that action, the processor and its support code need a way to locate executable code and establish an environment in which that code can run.

## Trace one documented startup model

Arm's CMSIS Cortex-M startup template describes a **reset handler**, an initial **stack pointer**, and an **interrupt vector table** containing handler addresses. The reset handler typically calls system initialisation, then transfers control to a C runtime that performs its initialisation and calls the application's `main` function. Here `main` is the entry function used by that runtime; it is not the first instruction executed after reset.

This names a particular Cortex-M software model. The exact sequence comes from the chip, toolchain and project. Another processor or startup package can use a different arrangement.

C variables with **static storage duration** have storage for the whole program execution; program-wide variables are an example. C requires these variables to receive their initial values before C program startup. The described runtime completes this initialisation before calling `main`. This is a software initialisation rule, not a claim that reset hardware erases all physical RAM. C does not require every microcontroller project to use an entry function named `main`.

> [!analogy] Real-world analogy: opening a shop before serving customers
> A shop can need its entrance opened, workspace prepared and equipment checked before the first customer is served.
>
> **How it maps:** The opening procedure represents the reset and startup path; serving the first customer represents entering application code. A fault during preparation can prevent the application's first visible action.
>
> **Where it stops:** There is no universal startup checklist for every MCU. Hardware-defined entry rules and vendor startup code determine the real order, and a reset need not erase every memory region.

## Boot code and application code are distinct

A **bootloader** is code that loads or starts another program and may support a programming or recovery interface. Some devices begin in manufacturer **ROM**, read-only memory containing fixed boot code. Others enter an application image more directly. These arrangements are device-specific.

RP2040 is one concrete example: its boot ROM participates in startup and supports the documented USB boot interface. That example should not be expanded into a claim that every MCU has a USB bootloader.

When diagnosing a board that never reaches the application, ask which milestone failed. Did the programming tool report a successful transfer? Can the debug tools reach the target? Does execution reach application startup? Does hardware initialisation finish? These observations separate a startup failure from a failure in the later decision logic.

Treat retained settings deliberately. Some reset conditions can preserve physical RAM or special retention storage, while startup code may reinitialise application data. Check the specific device and runtime rather than using a reset as a general promise to erase all data.

## Key takeaways
- Reset, flash programming, startup and application entry are distinct operations.
- `main` is reached through supporting code in the described CMSIS startup model.
- Boot behaviour and retention depend on the target and its startup configuration.

## Further reading
- [Cortex-M startup file and reset handler — Arm CMSIS](https://arm-software.github.io/CMSIS_6/latest/Core/startup_c_pg.html)
- [System initialisation — Arm CMSIS](https://arm-software.github.io/CMSIS_6/latest/Core/group__system__init__gr.html)
- [C11 draft: execution environments, sections 5.1.2 and 5.1.2.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [RP2040 datasheet: boot sequence](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
