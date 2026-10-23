# Beginner embedded software course

Build a beginner learning path in `content/embedded/`. The learner understands basic variables, conditions,
loops and functions, but is new to C, electronics and firmware. Teach the C needed for each example.
Each short lesson should leave them able to explain or carry out one concrete task, with worked practice
questions and optional real-world analogies. The course ends with a small sensor-and-indicator firmware
design that can first be tested on a computer.

Follow `CONTENT_SPEC.md`, `docs/new-module.md`, `docs/verify-brief.md` and `docs/CONTENT_PROCESS.md`.
One author owns each module; a different agent independently verifies it before stamping.

## Course structure

| Order | Module directory and id | Lessons and objectives |
|---|---|---|
| 1 | `01-foundations`, `embedded-foundations` | Six lessons: `esb-what-embedded` distinguishes firmware from a desktop program; `esb-mcu-memory-peripherals` explains the CPU, flash, RAM and peripherals; `esb-datasheet-and-board` separates chip limits, board wiring and SDK configuration; `esb-build-flash-run` follows edit, compile, link, flash and observe; `esb-reset-startup` traces reset and startup into the application without assuming every chip boots alike; `esb-loop-state` traces a cooperative main loop and explicit state. |
| 2 | `02-c-and-io`, `embedded-c-io` | Eight lessons: `esc-c-values-types` introduces declarations, functions and fixed-width unsigned values; `esc-pointers-registers` explains pointers and memory-mapped I/O with clearly labelled hardware sketches; `esc-bits-masks` reads and changes bits safely; `esc-gpio-input-output` distinguishes input/output modes and pulls; `esc-buttons-debounce` handles a bouncing input without blocking the loop; `esc-memory-lifetimes` explains bounds, local/static storage and invalid pointers; `esc-adc-samples` interprets an ideal ADC code with real-device limits; `esc-pwm-output` explains period, duty cycle and an LED-only output example. |
| 3 | `03-timing-and-buses`, `embedded-timing-buses` | Six lessons: `est-polling-interrupts` compares polling and interrupt work; `est-timers-nonblocking` uses elapsed time and a wrapping unsigned counter; `est-isr-sharing` separates volatile access, atomicity, event loss and short critical sections; `est-uart-basics` interprets serial framing and buffering; `est-i2c-basics` traces a controller/peripheral transaction and failure; `est-spi-basics` traces clocked transfer and chip selection using a device's required mode. |
| 4 | `04-debugging-and-projects`, `embedded-debug-projects` | Six lessons: `esr-debugging-observation` chooses logs, breakpoints, watchpoints and signal observation; `esr-test-without-board` separates logic from device drivers and tests fake inputs on a computer; `esr-watchdog-reset` designs timeout, watchdog and reset-cause handling; `esr-rtos-when` compares a cooperative loop with tasks, ownership and blocking; `esr-sensor-state-machine` builds bounded sample, validate, indicate and fault states; `esr-project-workflow` gives a concrete test, flash, observe and recovery checklist for that small project. |

Keep these ids stable. Modules 1 to 3 must establish every prerequisite used by module 4. Lessons should
usually take 3–5 minutes, with 2–3 focused questions each, including applied single and multi-choice questions.
Difficulty reflects the learner: mainly basic, then intermediate applications; no artificial advanced trivia.
Write substantive explanations and examples rather than outlines. Include a concrete trace or worked example
in each lesson. Questions must be answerable from the visible lesson, with the analogy closed.

## Code and hardware assumptions

Use small C11 examples for firmware logic. Explain each unfamiliar construct before relying on it. State
when a snippet is complete, a function requiring a supplied harness, an SDK fragment, or illustrative
pseudocode. Portable examples must compile with warnings enabled and have deterministic inputs and outputs.
Run examples in the verifier's host harness; do not claim that host execution validates peripheral hardware.

Keep the course usable without purchasing a board. Explain the development process and an official vendor
example, rather than inventing generic flash commands. When concrete hardware behaviour is necessary,
label the exact device family; RP2040 documentation may provide an illustration, not a universal MCU rule.
Avoid volatile raw-address dereferences in runnable host examples. Use SDK or datasheet abstractions for
hardware, with hardware requirements explicit. A register may have read/write side effects: bitwise
read-modify-write is not automatically safe for every register.

`volatile` is not an atomic operation, memory barrier, critical section or thread-synchronisation primitive.
Never teach a shared flag read-and-clear as reliably counting interrupts. Critical-section examples must
state single-core and execution-context assumptions and preserve the previous interrupt state. Unsigned
elapsed-time examples must use an explicit width, unsigned arithmetic and a bounded observation interval.

Keep ideal converter and timing calculations separate from accuracy guarantees or worst-case timing claims.
Define every symbol and unit in a formula block, including inside question feedback. Avoid optional formulas
inside analogy callouts. Explain ADC quantisation assumptions and PWM's distinction from a true analogue
output. UART, I2C and SPI examples must use explicit assumed frame formats, address conventions and modes.

## Primary sources

Fetch the actual relevant pages or source passages; a homepage or search snippet is not a fact-check.
Prefer these publishers, using the precise section appropriate to each lesson:

- ISO C working draft N1570, `https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf`, for C11 semantics.
- GCC documentation, `https://gcc.gnu.org/onlinedocs/`, for the build toolchain and compiler-specific details.
- Raspberry Pi RP2040 datasheet, `https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf`, for named hardware examples.
- Raspberry Pi SDK documentation, `https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html`,
  and SDK API documentation, `https://www.raspberrypi.com/documentation/pico-sdk/`, for concrete firmware workflows and peripheral APIs.
- Arm CMSIS Core, `https://arm-software.github.io/CMSIS_6/latest/Core/`, for Cortex-M startup and interrupt interfaces.
- NXP UM10204 I2C specification, `https://www.nxp.com/docs/en/user-guide/UM10204.pdf`, for I2C signalling and transactions.
- Manufacturer device manuals and official SDK source for UART, SPI, ADC, PWM and watchdog examples.
- FreeRTOS documentation and kernel source, `https://www.freertos.org/` and
  `https://github.com/FreeRTOS/FreeRTOS-Kernel`, for RTOS tasks and constraints.
- SEI CERT C, `https://wiki.sei.cmu.edu/confluence/display/c`, for safe C practices and object lifetimes.

Verify every lesson and question link loads and supports the relevant claim. If a primary URL cannot be
retrieved, use a stable official alternative or remove the unsupported claim rather than inventing it.

## Familiar comparisons and technical terms

Use one focused `[!analogy]` disclosure where a familiar comparison improves a technical explanation.
Give a short descriptive title, a concrete situation, `**How it maps:**` and `**Where it stops:**`.
Keep all definitions, required mechanisms, safety instructions and assessment facts visible outside it.
Do not duplicate a story across unrelated lessons or force one into a simple procedure; record the reason
when a lesson needs no analogy.

Each module needs a glossary for every unfamiliar technical term and acronym, with precise aliases and
independently sourced definitions. Search existing terms first, reuse earlier entries within this subject,
and use `embedded-` prefixes for new glossary ids where needed. Module 1 owns general firmware, memory
and toolchain vocabulary; later modules own their new C, I/O, timing, communication and debugging terms.
Avoid aliases that capture ordinary English. Do not edit other subjects' verified glossaries.

## Scope and practical safety

This is an introductory software course. Keep electronics to signal direction, input limits, pull resistors,
an existing development board's onboard indicators and reading the correct manuals. Work only with
low-voltage development hardware. Never instruct direct connection of motors, relays, mains, high-current
loads or unknown voltage sources to MCU pins. Do not prescribe universal logic-voltage or pin-current limits.
Keep necessary precautions next to the relevant activity, visible while analogies are closed.

Do not duplicate the specialised synth/audio course, give a full C language course, or cover assembly,
linker-script authoring, DMA/cache coherence, production bootloaders, OTA, cryptographic provisioning,
low-power characterisation or safety-critical certification. Introduce the idea of an RTOS without claiming
that installing one proves a deadline. State these boundaries as course scope, not as missing beginner prerequisites.

## Required author and verifier reports

The author reports every lesson id, question count, analogy decision, formula count and glossary entry count,
the exact code checks performed, primary sources fetched, gaps and every uncertain claim. Save a machine-readable
author report in `/tmp/embedded-<module>-author.json`. Do not write verification or stamp as the author.

The independent verifier checks all lesson and question claims, calculations, code, analogies, terminology
and answer keys. Correct the module, write full `verification.json`, and stamp only after the real pass.
Preserve the scope and report corrections, gaps and confidence. Also add `analogyReview` using the format
in `docs/CONTENT_PROCESS.md`, covering every new lesson with a current review hash, a specific decision
and rationale, distinct author/verifier identities and fetched sources. Save the verifier report in
`/tmp/embedded-<module>-verified.json`. New content must not be added to the frozen legacy verification list.
