---
id: elec-ground-reference
sourceLesson: elec-ohms-law
title: "Ground references and return-wire voltage"
level: basic
minutes: 2
summary: "Circuit ground is a chosen reference, distinct from protective earth."
---

Circuit ground is a chosen reference, distinct from protective earth.

## Ground is a reference
**Circuit ground** (GND, 0 V) is the point you choose to measure every other voltage against. In a battery- or USB-powered synth it's usually the supply's negative terminal. It doesn't have to connect to the earth in the soil.

> [!analogy] Real-world analogy: Heights measured from sea level
> A hill's height is usually quoted above sea level, but you could measure it from the valley floor instead. The hill does not change; only the number you quote does.
>
> **How it maps:** Circuit ground is the chosen zero, like sea level. "This pin is at 3.3 V" is a difference between the pin and that reference. Two boards can only compare voltages meaningfully when they share a reference.
>
> **Where it stops:** A height datum is a fixed, agreed reference that nothing flows through. Real ground conductors carry current and can sit at slightly different voltages from point to point. Protective earth is also a separate safety connection, not just a choice of zero.

Three meanings of "ground" get mixed up:

- **Signal or circuit ground:** the 0 V reference and current return path inside your circuit. This is what "GND" on a microcontroller board means.
- **Chassis ground:** the conductive case or chassis reference; whether it connects to circuit 0 V depends on the equipment design.
- **Protective earth:** the mains safety earth in a wall socket. It belongs to mains equipment and is not something to modify. The later noise and grounding units return to this.

Two practical rules follow:

1. **Direct, non-isolated single-ended signals need a common voltage reference.** For ordinary GPIO/UART links, connect the boards' GND pins. Isolated links such as DIN MIDI deliberately avoid a direct ground connection. A voltage only means something relative to a reference both sides agree on.
2. **"0 V" isn't the same everywhere.** Ground wires have small resistances. When current flows through them, two "ground" points can differ by a few millivolts. For audio that's enough to hear (the noise and grounding units).

## Key takeaways

- Circuit ground is a chosen reference, distinct from protective earth.
- Real return conductors develop voltage when current flows.

## Further reading

- [Analog Devices MT-031: converter grounding](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf)
- [RaneNote 110: system interconnection](https://www.ranecommercial.com/legacy/note110.html)
