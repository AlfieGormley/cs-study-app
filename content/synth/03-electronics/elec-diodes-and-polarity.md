---
id: elec-diodes-and-polarity
sourceLesson: elec-components
title: "Diode direction, drops and protection"
level: intermediate
minutes: 2
summary: "A diode’s current and temperature affect its forward drop."
---

A diode’s current and temperature affect its forward drop.

## Diodes
A forward-biased diode conducts conventional current from **anode** to **cathode** (towards the bar in its schematic symbol; an LED’s outward arrows represent emitted light). Reverse-biased, it normally carries a small leakage current until breakdown; respect the exact reverse-voltage rating. The cathode is marked with a band.

| Type | Forward drop (approx.) | Common use |
|---|---|---|
| Silicon (e.g. 1N4148) | ~0.6–0.75 V at a few mA | Low-current signal switching, diode clamping |
| Silicon rectifier (e.g. 1N400x) | ~0.7 V small current, up to ~1 V at 1 A | Reverse-polarity protection |
| Schottky | ~0.2–0.4 V small current, ~0.45–0.6 V at 1 A | Low-drop protection |

The forward drops are approximate, and they rise with current and fall with temperature. Datasheets give limits at stated test conditions and show typical curves. Checked 29 October 2026: Vishay 1N4148 revision 1.6 (7 November 2024) gives 1 V maximum at 10 mA; Vishay 1N5817 revision 1 July 2020 gives 0.45 V maximum at 1 A, while Vishay 1N4001–1N4007 revision 29 April 2020 gives 1.1 V maximum at 1 A. These are exact documented examples, not a universal diode drop.

Uses in a synth:

- **Reverse-polarity protection:** a series diode in the supply line blocks current if the supply is connected backwards, at the cost of its forward drop.
- **Diode clamping:** diodes to the supply rails catch input overvoltage (the logic and datasheet units).
- **Flyback:** a correctly oriented diode across a DC relay or motor coil lets its current recirculate after switch-off, limiting the voltage spike while stored magnetic energy is dissipated. Check the drive circuit and release-time requirements.

When checking orientation, use the exact part’s markings: an LED’s longer lead is usually its anode, and an axial diode’s band marks the cathode. Ordinary ceramic capacitors are non-polarised; tantalum capacitors are polarised and must not be reversed. Lead length alone is unreliable after leads have been trimmed.

## Key takeaways

- A diode’s current and temperature affect its forward drop.
- Check component polarity and reverse ratings; a diode does not eliminate all fault paths.

## Further reading

- [Vishay 1N4148, revision 1.6](https://www.vishay.com/docs/81857/1n4148.pdf)
- [Vishay 1N4001–1N4007, revision 29 April 2020](https://www.vishay.com/docs/88503/1n4001.pdf)
- [Vishay 1N5817–1N5819, revision 1 July 2020](https://www.vishay.com/docs/88525/1n5817.pdf)
