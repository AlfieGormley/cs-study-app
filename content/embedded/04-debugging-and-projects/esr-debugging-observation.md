---
id: esr-debugging-observation
title: Choose evidence before changing firmware
level: basic
minutes: 4
summary: Choose an observation that can answer the actual debugging question.
---

An indicator did not change when expected. Before rewriting the driver, turn the symptom into a question: did the input arrive, did the state change, or did the output operation reach the device? Each question needs different evidence.

## Choose an observation

| Question | Useful observation |
|---|---|
| Did this branch execute? | A bounded log or breakpoint |
| Who changed this variable? | A watchpoint, when supported |
| Which bytes did the driver report? | A bounded receive trace and errors |
| Did the expected signal appear? | A suitable instrument and device timing specification |

A **breakpoint** stops execution at a chosen location. A **watchpoint** can stop when a watched expression changes. Support depends on the target and debugger; hardware watchpoints have target-specific limits, and software watchpoints can add substantial overhead. Optimisation can also make a source variable unavailable or harder to interpret at a particular stopping point.

GDB is one debugger with these facilities. A host debugger can inspect the portable project in this module; build with suitable debug information when inspecting source variables. Inspecting a microcontroller instead requires a supported probe, connection and target configuration; there is no universal debug command or pinout.

> [!analogy] Real-world analogy: investigating a missed delivery
> A delivery record can show when a parcel was handed over; watching a doorway can show who actually moved it. Different records answer different questions.
>
> **How it maps:** Logs record selected events, a breakpoint checks execution at a point, and a watchpoint helps identify a data change. Choose the evidence that can distinguish competing explanations.
>
> **Where it stops:** A debugger can stop the processor and logging consumes execution time and storage. These observations can change the timing of the fault being investigated.

## Use one hypothesis at a time

For the hypothetical missing indicator, inspect the decoded input first. If it is correct, inspect the resulting application state. If that is also correct, check the driver result and the actual output configuration. This separates a parsing defect from a state-rule defect or an incorrectly configured output.

Add a short trace containing the state, event, driver failure result and timestamp you actually need. Bound its buffer and output rate; do not print without limit inside an ISR. A fault that disappears after adding logging needs investigation: the change may affect timing or memory use without correcting the defect.

Halting a processor changes its relationship with external devices and deadlines. A watchdog may continue running or pause under a configured debug option; check that device's behaviour. Use non-halting observations when you need timing evidence, and record how the observation affects the system.

## Key takeaways
- Start with a question that an observation can answer.
- Debugger and logging overhead can change timing and behaviour.
- Separate decoded input, application state and physical output evidence.

## Further reading
- [GDB breakpoints and watchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Breakpoints.html)
- [GDB watchpoint support and limits](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Watchpoints.html)
- [GDB: optimisation and source-variable visibility](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Optimized-Code.html)
- [Zephyr: logging overhead and bounded output](https://docs.zephyrproject.org/latest/services/logging/index.html)
- [Pico SDK watchdog debug-pause option](https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2_common/hardware_watchdog/include/hardware/watchdog.h)
