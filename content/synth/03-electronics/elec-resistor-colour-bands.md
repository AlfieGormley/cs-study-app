---
id: elec-resistor-colour-bands
sourceLesson: elec-components
title: "Reading resistor colour bands"
level: intermediate
minutes: 2
summary: "Read digits, multiplier and tolerance separately."
---

A synth build uses a small set of passive parts over and over. Each one has a **value** (what it does) and **ratings** (what it survives). Ignoring ratings or component polarity can damage parts even when the nominal value is correct.

### Reading the value
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

The digit bands form a whole number, and the multiplier band scales it:

```formula
R = (10 × d_1 + d_2) × m
R = (10 × 4 + 7) × 100 Ω = 4700 Ω
where
R: the resistor's nominal value, in ohms (Ω)
d_1: the first digit band's number (yellow = 4)
d_2: the second digit band's number (violet = 7)
m: the multiplier band’s resistance scale, in ohms (Ω); red means 100 Ω per digit count
Ω: ohms, the unit of resistance
In words: read the digit bands as a two-digit number, then multiply by the multiplier band. Yellow-violet-red gives 47 × 100 = 4700 Ω = 4.7 kΩ.
```

A five-band resistor uses three significant digits. Brown-black-black-red-brown has three digits followed by the red multiplier and brown tolerance:

```formula
R = (100d_1 + 10d_2 + d_3)m
R = (100 × 1 + 10 × 0 + 0) × 100 Ω
R = 10,000 Ω = 10 kΩ
where
R: nominal resistance, in ohms (Ω)
d_1: first significant digit, brown gives one
d_2: second significant digit, black gives zero
d_3: third significant digit, black gives zero
m: resistance scale from the multiplier band, in ohms; red gives 100 Ω per digit count
Ω: ohms, the unit of resistance
kΩ: kilohms, one thousand ohms
In words: read the first three bands as one hundred, then apply the red scale of one hundred ohms. The brown tolerance band permits 1% initial variation.
```

Colours are easy to misread under poor light. Brown, red and orange look alike, and so do violet and grey. **Measure with a multimeter before fitting** (out of circuit) whenever you're unsure.

## Key takeaways

- Read digits, multiplier and tolerance separately.
- Confirm uncertain colours by measuring the unpowered resistor out of circuit.

## Further reading

- [Vishay: resistor colour code](https://www.vishay.com/docs/49411/resistor_color_code_calculator.pdf)
