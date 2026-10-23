---
id: esb-loop-state
title: Keep a main loop responsive with explicit state
level: basic
minutes: 4
summary: Trace bounded main-loop work and distinguish a button state from a new button event.
---

A **main loop**, sometimes called a superloop, repeatedly performs the application's foreground work. In a **cooperative** design, each operation returns control so the loop can visit its other jobs. One operation that waits indefinitely can prevent all later foreground jobs from running.

An explicit **state machine** records the current mode and defines how an input changes it. It replaces vague instructions such as "handle the button somehow" with a rule that can be traced and tested.

## Separate an event from a level

For this teaching example, a button toggles an indicator between OFF and ON. The input is an already accepted press event, not the raw electrical signal and not a button-held level. The later debounce lesson explains how to derive such events from real input.

This is illustrative pseudocode, not C or an SDK API. Each input check and output update is assumed to return promptly. The assignments initialise or change the remembered state.

```text
state <- OFF
repeat:
  event <- take_one_press_event()
  if event is PRESS:
    if state is OFF:
      state <- ON
    else:
      state <- OFF
  apply_indicator(state)
  service_other_work()
```

One loop pass consumes at most one event. With an initial state of OFF, the sequence below gives a deterministic trace:

| Pass | Accepted event | State after pass |
|---|---|---|
| 1 | none | OFF |
| 2 | PRESS | ON |
| 3 | none, button still held | ON |
| 4 | PRESS after another press | OFF |

Using the held-button level as the event would toggle again on every pass while the button stayed down. A fast loop would then produce behaviour unrelated to the number of deliberate presses.

> [!analogy] Real-world analogy: one person checking several service desks
> A person visits several desks in order, handles a small piece of work at each and returns for the next round. Waiting forever at one desk prevents visits to the others.
>
> **How it maps:** The person represents foreground execution, desks represent loop jobs and each short visit represents work that returns control. The remembered indicator mode represents the application's explicit state.
>
> **Where it stops:** Real MCU interrupts can run between foreground instructions, and another core may run simultaneously. A loop structure alone proves neither a response-time limit nor safe access to shared data.

## Test decisions separately from hardware

The event-to-state rule can be tested on a computer with a list of input events. That checks the defined transitions; it does not validate the physical button, signal levels or output wiring.

To reason about responsiveness, list the maximum work each foreground job can do before returning. Avoid an unbounded wait for input inside a loop job. Later timing and debugging lessons add elapsed-time scheduling, bounded communication and observation methods. They also explain why merely adding interrupts or more scheduling machinery does not establish a timing guarantee.

## Key takeaways
- Cooperative jobs must return control for the loop to service other foreground work.
- Remember explicit state and consume an accepted event once.
- A trace can test decision logic without claiming to validate hardware or deadlines.

## Further reading
- [Cooperative superloop model — Quantum Leaps](https://www.state-machine.com/qpc/srs-qp_qv.html)
- [Official blink application and its main loop — Raspberry Pi](https://raw.githubusercontent.com/raspberrypi/pico-examples/master/blink/blink.c)
- [Cortex-M interrupt model — Arm CMSIS](https://arm-software.github.io/CMSIS_6/latest/Core/group__NVIC__gr.html)
