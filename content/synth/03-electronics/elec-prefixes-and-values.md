---
id: elec-prefixes-and-values
sourceLesson: elec-ohms-law
title: "Reading electronic units and prefixes"
level: basic
minutes: 1
summary: "Prefix case matters: milli and mega differ by a billion."
---

Prefix case matters: milli and mega differ by a billion.

## Units and prefixes
Electronics spans huge ranges, so SI prefixes are everywhere. A prefix mistake can change a part by orders of magnitude.

| Prefix | Symbol | Factor |
|---|---|---|
| mega | M | 10⁶ |
| kilo | k | 10³ |
| milli | m | 10⁻³ |
| micro | µ (or u) | 10⁻⁶ |
| nano | n | 10⁻⁹ |
| pico | p | 10⁻¹² |

Tips:

- Note the case: **m** (milli) and **M** (mega) differ by 10⁹.
- Schematics often put the prefix where the decimal point would be (the RKM code, part of IEC 60062): `4k7` means 4.7 kΩ, `2R2` means 2.2 Ω, and `100n` means 100 nF.
- Match the value and unit when comparing a schematic with a parts list. `100n`, 100 nF and 0.1 µF describe the same capacitance; 100 µF is a thousand times larger.

Matching capacitance alone does not establish an interchangeable part. Also check its voltage rating (allowed voltage), dielectric (insulating material) and tolerance (allowed value variation), as specified for the circuit.

## Key takeaways

- Prefix case matters: milli and mega differ by a billion.
- Check prefixes before fitting a part; a familiar-looking number may represent a very different value.

## Further reading

- [BIPM: SI prefixes](https://www.bipm.org/en/measurement-units/si-prefixes)
- [Vishay: resistor colour code](https://www.vishay.com/docs/49411/resistor_color_code_calculator.pdf)
