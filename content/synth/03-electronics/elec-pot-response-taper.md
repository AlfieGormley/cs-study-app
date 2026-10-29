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

- **Linear taper:** halfway round, the wiper is at half the total resistance. With negligible loading and a steady supply, output voltage is approximately proportional to angle over the usable track.
- **Logarithmic or "audio" taper:** the resistance changes slowly at first, then quickly. Audio tapers are often specified by the share of resistance at mid-rotation: a 10% taper puts the wiper at about 10% of the total there, and 15% versions also exist (Bourns PDB181-GTR offers both). Loudness perception is roughly logarithmic, so an audio taper makes an analogue volume control feel more even than a linear one.

| Rotation | Linear | 10% log (approx.) |
|---|---|---|
| 0% | 0% | 0% |
| 50% | 50% | 10% |
| 100% | 100% | 100% |

Two practical warnings:

- **Markings aren't standardised.** For example, Bourns PDB181-GTR uses its A-series audio curves and B0 linear curve. Other manufacturers and legacy parts use different letter schemes. Read the datasheet.
- **Audio tapers follow specified curves.** They need not be exact mathematical logarithms; use the manufacturer’s curve for the actual part.

> [!tip] For digital synths, usually choose linear
> When a pot feeds an ADC, you can choose the response curve in software, within the available resolution. An ideal linear pot with negligible loading spreads ADC resolution roughly evenly across usable rotation, and code can map it to a logarithmic volume or exponential frequency response. A log pot is mostly useful when it directly controls an analogue audio level.

## Key takeaways

- Taper describes resistance versus rotation.
- Verify the manufacturer’s marking scheme rather than assuming a letter code.

## Further reading

- [Bourns PDB181-GTR: circuit and taper charts](https://www.bourns.com/docs/product-datasheets/PDB181-GTR.pdf)
