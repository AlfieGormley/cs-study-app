---
id: logic-cdc-metastability
title: Metastability and clock-domain crossings
level: intermediate
minutes: 3
sourceLesson: logic-sequential
summary: Synchroniser stages give metastability time to resolve.
---

## Metastability

What if D changes inside the setup/hold window? This is unavoidable when a signal comes from outside the clock domain: a button, a network chip with its own clock, another core running at a different frequency.

The flip-flop's internal loop can then be caught balanced between 0 and 1, like a ball on the top of a hill. This **metastable** state resolves to a valid 0 or 1 eventually, but the time it takes is unbounded in principle; the probability of still being unresolved falls off exponentially with the time you wait.

A common mitigation for a single-bit level is a two-flip-flop synchroniser, with both stages clocked by the destination clock:

```
async ---> [FF_a] ---> [FF_b] ---> logic
              ^           ^
              +--- CLK ---+
```

FF_a may go metastable. Resolution time is roughly a cycle minus stage, routing and setup overhead; placement matters. The failure rate depends on device parameters, clock frequency and asynchronous transition rate, so stage count must be justified against the required MTBF.

> [!note] Evidence gap
> A generic years-long MTBF is omitted because the required device and timing parameters were unavailable. A two-stage chain reduces risk but does not prove an acceptable failure rate.

A short pulse can be missed entirely; use pulse stretching or an appropriate handshake/toggle protocol when every event must be transferred. A push-button also requires debouncing separately. High-speed or high-reliability designs sometimes use three stages. Multi-bit values need more care (handshakes or asynchronous FIFOs with Gray-coded pointers), because separately synchronised bits can resolve on different cycles.

## Match the transfer method to the information

Imagine a slow destination clock and a brief source pulse that rises and falls between two destination edges. Even perfect, instantaneous flip-flops would miss it: neither sampling edge saw a one. Extra synchroniser stages address the probability of unresolved metastability, not this missing observation.

For an isolated event, one option is to stretch the pulse long enough for the specified destination sampling assumptions. Another is to toggle a source bit once per event and detect a change after synchronisation. A toggle scheme still needs a bound on event spacing: two toggles before the receiver observes either can cancel. A request/acknowledge handshake can instead keep an event pending until the receiver confirms it.

For a multi-bit word, synchronising every bit independently does not make the word coherent. Different bits can be observed in different cycles. A bundled-data handshake can keep the word stable during transfer; an asynchronous FIFO can queue words while transferring appropriately constrained pointers. These are design patterns with timing and protocol requirements, not interchangeable fixes for every crossing.

## Key takeaways
- Synchroniser stages give metastability time to resolve.
- Single-bit levels, pulses and coherent multi-bit data need different transfer schemes.

## Further reading
- [MIT — Synchronisation and arbitration](https://computationstructures.org/notes/arbitration/notes.html)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/sequential_logic/notes.html)
- [Flip-flop (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Flip-flop_(electronics))
- [Latch (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Latch_(electronics))
- [Metastability (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Metastability_(electronics))
- [Static timing analysis — Wikipedia](https://en.wikipedia.org/wiki/Static_timing_analysis)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Clock domain crossing — Wikipedia](https://en.wikipedia.org/wiki/Clock_domain_crossing)
