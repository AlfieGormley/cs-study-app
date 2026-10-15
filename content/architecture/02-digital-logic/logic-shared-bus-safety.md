---
id: logic-shared-bus-safety
title: Tri-state buses, noise and physical limits
level: basic
minutes: 3
sourceLesson: logic-gates-cmos
summary: Only one enabled driver may drive a shared tri-state wire.
---

## Beyond 0 and 1

- **Tri-state buffers** have a third output state, high-impedance (`Z`), which is effectively disconnected. Several tri-state outputs can share one wire, provided at most one drives at a time; when none drives, a pull resistor, keeper or protocol rule may be needed to define the idle level. If two drive opposite values, you get a short circuit and an undefined level.
- **Restoring logic**: the gates in this model restore valid input voltage ranges to valid output ranges within specified noise margins and loading. Excess noise or an input in the undefined region can still cause failure; regeneration is a benefit of digital abstraction, not an unlimited noise guarantee.

## Pitfalls

- **Counting gates instead of transistors or delay.** Equivalent two-level AND-OR and NAND-NAND designs can have the same number of logic boxes but different transistor counts and delays. Compare actual cells, fan-in, loading and wiring.
- **Leaving inputs floating.** An unconnected CMOS input drifts to an undefined voltage and can turn both transistors partly on, wasting current and producing random outputs. Tie unused inputs to VDD or ground.
- **Ignoring fan-out.** One signal driving hundreds of inputs (a clock, a reset, an enable) is slow unless it is buffered into a tree.

## Trace the possible bus states

Suppose two devices share a data wire. Each device has a separate output enable; disabling its output produces high impedance rather than a stored zero.

| Driver A | Driver B | Shared wire |
|---|---|---|
| high impedance | drives low | low |
| drives high | high impedance | high |
| high impedance | high impedance | needs idle-level design |
| drives high | drives low | contention |

The third row is easy to overlook. Disconnecting both drivers does not actively select a valid level. A pull resistor or keeper can define an idle level, but its strength must be compatible with the enabled drivers and the required rise time. A weak keeper also does not replace proper arbitration between opposite push-pull drivers.

When switching ownership, the control design must account for the old driver's disable delay and the new driver's enable delay. A logical promise that the enables never overlap is insufficient if physical delays still allow both outputs to conduct simultaneously. Check the selected devices' timing specifications rather than assuming the Boolean control table proves electrical safety.

## Key takeaways
- Only one enabled driver may drive a shared tri-state wire.
- Noise margins, input levels and output loading constrain real gates.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/cmos/notes.html)
- [Logic gate — Wikipedia](https://en.wikipedia.org/wiki/Logic_gate)
- [CMOS — Wikipedia](https://en.wikipedia.org/wiki/CMOS)
- [NAND logic — Wikipedia](https://en.wikipedia.org/wiki/NAND_logic)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
- [Processor power dissipation — Wikipedia](https://en.wikipedia.org/wiki/Processor_power_dissipation)
- [Nand2Tetris: build a computer from NAND gates](https://www.nand2tetris.org/)
