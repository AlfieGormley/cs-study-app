---
id: elec-pot-response-taper
sourceLesson: elec-dividers
title: "Linear and audio potentiometer tapers"
level: basic
minutes: 2
summary: "Taper describes resistance versus rotation."
---

Taper describes resistance versus rotation.

## Linear and logarithmic (audio) taper
The **potentiometer taper** (or law) is how resistance changes with rotation.

- **Linear taper:** halfway round, the wiper is at half the total resistance. Output voltage is proportional to angle.
- **Logarithmic or "audio" taper:** the resistance changes slowly at first, then quickly. A common specification is a 10% log taper, meaning the wiper is at 10% of the total at mid-rotation. Hearing is roughly logarithmic, so a log pot makes an analogue volume control feel even.

| Rotation | Linear | 10% log (approx.) |
|---|---|---|
| 0% | 0% | 0% |
| 50% | 50% | 10% |
| 100% | 100% | 100% |

Two practical warnings:

- **Markings aren't standardised.** For example, Bourns PDB181-GTR uses its A-series audio curves and B0 linear curve. Other manufacturers and legacy parts use different letter schemes. Read the datasheet.
- **Cheap log pots are approximations,** often two linear segments joined near the middle.

> [!tip] For digital synths, usually choose linear
> When a pot feeds an ADC, you can apply any curve you like in software. A linear pot gives even resolution across the whole rotation, and code can map it to a logarithmic volume or exponential frequency response. A log pot is mostly useful when it directly controls an analogue audio level.

## Key takeaways

- Taper describes resistance versus rotation.
- Verify the manufacturer’s marking scheme rather than assuming a letter code.

## Further reading

- [Bourns PDB181-GTR: circuit and taper charts](https://www.bourns.com/docs/product-datasheets/PDB181-GTR.pdf)
