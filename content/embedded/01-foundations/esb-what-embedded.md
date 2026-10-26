---
id: esb-what-embedded
title: What embedded software does
level: basic
minutes: 3
summary: Identify the inputs, decisions, outputs and constraints of a small firmware system.
---

A room sensor reads a measurement, decides whether a threshold has been crossed and changes an indicator. The program has the familiar ingredients of any software system: data, conditions, functions and state. What changes is its relationship with the physical device.

**Embedded software** runs as part of a device's particular purpose. **Firmware** is the software stored for that device to execute, often in memory that retains its contents without power. The term does not mean that the software can never be updated. The vendor's supported update process determines how a particular device changes its firmware.

This course concentrates on small **microcontrollers**, or MCUs. You can learn their software structure and test decision logic on a computer before choosing a development board.

## Start with behaviour

For an illustrative sensor indicator, write the behaviour before writing code:

| Part | Example requirement |
|---|---|
| Input | A new measurement and whether it is valid |
| Decision | Compare a valid measurement with a limit |
| Output | Update the indicator |
| Fault | Show a distinct indication when data is invalid |

The threshold and the fault indication are choices for this example, not universal sensor rules. A first useful test is a sequence of inputs: below the threshold, above it, then invalid. The expected outputs are normal, alert, then fault. That sequence can be tested without connecting an actual sensor.

> [!analogy] Real-world analogy: a receptionist following a procedure
> A receptionist receives information, checks a rule and gives an appropriate response. If the information is missing, the procedure can specify a different response.
>
> **How it maps:** Incoming information represents sensor input, the rule represents firmware logic and the response represents an output. An explicit missing-information rule represents fault handling.
>
> **Where it stops:** A microcontroller cannot use human judgement to fill in an omitted rule. Firmware must define its inputs, timing and failure behaviour precisely.

## What changes from desktop development

A **bare-metal** application runs without an operating system managing its application execution. Its startup support and libraries still do real work. A real-time operating system is still an operating system; an application running under one is not bare metal. Other embedded devices use an operating system, so embedded does not automatically mean bare metal.

Hardware places constraints on available memory, supported signals and the time allowed for a response. A **real-time** requirement concerns meeting a timing requirement, not simply running as fast as possible. A program that eventually gives the right answer can still fail if that answer arrives too late for its intended job.

For this course's small project, success means the logic is correct, operations return control promptly, and invalid input has a defined outcome. Later modules add device interfaces and timing methods to that foundation.

## Key takeaways
- Describe observable inputs, decisions, outputs and fault behaviour before choosing implementation details.
- Firmware can be updateable; embedded systems can run with or without an operating system.
- Correct timing can be part of correct behaviour.

## Further reading
- [Firmware definitions — NIST](https://csrc.nist.gov/glossary/term/firmware)
- [Bare metal excludes an OS or RTOS — Altera](https://www.altera.com/developers/embedded-software/bare-metal)
- [Pico microcontroller boards — Raspberry Pi](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/microcontrollers/pico-series/about_pico.adoc)
- [RP2040 datasheet: system description](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
