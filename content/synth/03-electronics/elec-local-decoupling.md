---
id: elec-local-decoupling
sourceLesson: elec-logic-levels
title: "Local decoupling and bulk supply storage"
level: intermediate
minutes: 2
summary: "A local capacitor shortens the path for switching current pulses."
---

A local capacitor shortens the path for switching current pulses.

## Decoupling capacitors
Digital chips draw current in very short pulses each time their transistors switch. The supply wiring has resistance and inductance, so it can't deliver those pulses instantly. The local supply voltage dips and rings, and that noise spreads to everything sharing the supply, including audio.

A **decoupling capacitor** (bypass capacitor) next to the chip's supply pin acts as a local reservoir, supplying the pulses so the long supply path doesn't have to. For TI SN74HC00, datasheet SCLS181H recommends 0.1 µF at the supply terminal, allows combining it with 1 µF to address different noise frequencies, and places bypass capacitors close to the supply terminal.

Practical rules:

- **Use each device’s specified local capacitors.** For SN74HC00, the documented 100 nF capacitor goes close to its supply pin, with short connections to the pin and to ground. Distance adds inductance and defeats the purpose.
- **Bulk capacitance** (an electrolytic, say 10–100 µF) where power enters a board, for slower load changes. Values are typical, not prescriptive; follow the datasheets.
- **Follow the datasheet** where it gives specific values. Audio codecs and regulators often do.

The noise and grounding units explain why this matters even more for audio.

> [!analogy] Real-world analogy: A nearby water bottle
> A nearby bottle can meet a brief need without waiting for a distant tap.
>
> **How it maps:** A local capacitor supplies a chip’s brief current demand through a short path, while the supply replenishes it.
>
> **Where it stops:** Capacitance, resistance and inductance determine the electrical response. A larger distant capacitor cannot automatically replace the required local layout.

## Key takeaways

- A local capacitor shortens the path for switching current pulses.
- Use the exact chip and regulator’s specified values and layout.

## Further reading

- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
- [Analog Devices MT-101: decoupling techniques](https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf)
