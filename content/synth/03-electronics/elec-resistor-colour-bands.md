---
id: elec-resistor-colour-bands
sourceLesson: elec-components
title: "Reading resistor colour bands"
level: intermediate
minutes: 2
summary: "Read digits, multiplier and tolerance separately."
---

A synth build uses a small set of passive parts over and over. Each one has a **value** (what it does) and **ratings** (what it survives). Ignoring ratings or component polarity can damage parts even when the nominal value is correct.

## Reading the value
Through-hole resistors use colour bands defined by IEC 60062. Read from the end where the bands bunch together. The gold or silver tolerance band is usually at the other end, often slightly separated.

| Colour | Digit | Multiplier |
|---|---|---|
| Black | 0 | ×1 |
| Brown | 1 | ×10 |
| Red | 2 | ×100 |
| Orange | 3 | ×1k |
| Yellow | 4 | ×10k |
| Green | 5 | ×100k |
| Blue | 6 | ×1M |
| Violet | 7 | ×10M |
| Grey | 8 | ×100M |
| White | 9 | ×1G |
| Gold | | ×0.1 |
| Silver | | ×0.01 |

- **Four-band resistor code:** digit, digit, multiplier, tolerance. Yellow-violet-red-gold = 4, 7, ×100 = 4.7 kΩ ±5%.
- **Five-band resistor code** (precision): digit, digit, digit, multiplier, tolerance. Brown-black-black-red-brown = 1, 0, 0, ×100 = 10 kΩ ±1%.
- **Tolerance band:** brown ±1%, red ±2%, gold ±5%, silver ±10%.

The digit bands form a whole number, and the multiplier band scales it. For four bands, read the first two as a number, apply the multiplier from the chart, then check tolerance. Keep the chart nearby rather than memorising every colour.

A five-band resistor uses three significant digits. Brown-black-black-red-brown has three digits followed by the red multiplier and brown tolerance. For five bands, read three significant digits before the multiplier and tolerance. Counting the bands first prevents mistaking a multiplier for a digit.

Colours are easy to misread under poor light. Brown, red and orange look alike, and so do violet and grey. **Measure with a multimeter before fitting** (out of circuit) whenever you're unsure.

## Key takeaways

- Read digits, multiplier and tolerance separately.
- Confirm uncertain colours by measuring the unpowered resistor out of circuit.

## Further reading

- [Vishay: resistor colour code](https://www.vishay.com/docs/49411/resistor_color_code_calculator.pdf)
