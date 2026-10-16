---
id: elec-schematic-nets-symbols
sourceLesson: elec-schematics-breadboards
title: "Reading schematic symbols and nets"
level: intermediate
minutes: 3
summary: "Follow nets, pin numbers, labels and junctions rather than page geometry."
---

A schematic says *what connects to what*. A breadboard is one physical way to make those connections. The skill is moving between the two without error, and checking your work before power goes on.

## Common symbols
Symbols vary between the US/ANSI style and the IEC style used in Europe. You'll meet both.

| Part | Symbol notes | Designator |
|---|---|---|
| Resistor | Zigzag (US) or rectangle (IEC) | R1, R2 |
| Capacitor | Two parallel plates | C1 |
| Polarised capacitor | One plate curved or marked + | C2 |
| Diode | Diode symbol with a cathode bar; not a current arrow | D1 |
| LED | Diode with outward arrows | D2, LED1 |
| Potentiometer | Resistor with an arrow (wiper) | RV1, VR1 |
| Switch / button | Broken line with a lever | SW1, S1 |
| IC | Box with numbered pins | U1, IC1 |
| Connector / jack | Varies; pins numbered | J1, P1 |
| Ground | Downward lines or a triangle | GND |
| Supply | Arrow, bar or label (+5V, 3V3) | VCC |

The **reference designator** (R1, C3, U2) links each symbol to the parts list and to the board's silkscreen. Use designators in your notes too: "R3 is wrong" is unambiguous.

## Reading a schematic
### Nets, not pictures

A schematic is a graph made of schematic nets. Each **net** is a set of pins joined together electrically. Wire lengths and positions mean nothing; only connections do.

- **Junction dots** mark wires that connect. Two wires crossing *without* a dot don't connect. Many drawing conventions avoid four-way junctions entirely, so a cross is never ambiguous.
- **Net labels:** two wires with the same label (for example `ADC0` or `+3V3`) are connected even if no line joins them.
- **Power and ground symbols** are net labels too. Matching symbols for the same named ground or supply identify that net within the schematic’s scope. Distinct AGND and DGND symbols or hierarchical labels need the design’s own connection rules.
- **Hidden power pins:** some schematics omit an IC's supply pins from the drawing. Check the datasheet pinout so you don't forget to power the chip.

### Conventions that help

- Signals usually flow **left to right**: inputs on the left, outputs on the right.
- Higher voltages at the **top**, ground at the **bottom**.
- Values sit beside designators: `R1 10k`, `C4 100n`.

> [!example] Reading a pot input
> `+3V3 → RV1 pin 3`, `RV1 pin 1 → GND`, `RV1 pin 2 → net ADC0`, `C5 100n from ADC0 to GND`, and elsewhere `ADC0 → U1 pin 14`. That's three nets: +3V3, GND and ADC0. ADC0 has three members: the pot’s wiper, one terminal of the capacitor and U1 pin 14.

## Key takeaways

- Follow nets, pin numbers, labels and junctions rather than page geometry.
- Reference designators identify actual parts.

## Further reading

- [SparkFun: reading schematics](https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all)
- [TI SN74HC00, SCLS181H](https://www.ti.com/lit/ds/symlink/sn74hc00.pdf)
