---
id: aud-microphones-phantom
title: Understand phantom-power connections
level: intermediate
minutes: 3
summary: P48 uses matched feed resistors to apply common-mode DC to the signal conductors.
sourceLesson: aud-microphones
---

## Phantom power (P48)

Condenser microphones are powered through the same balanced cable that carries their signal. **IEC 61938** defines **P48**:

- **+48 V** fed through two matched **6.81 kΩ** resistors, one to each signal conductor (pins 2 and 3 of an XLR), with the shield (XLR pin 1) as the return.
- Closely matched feed resistors help preserve the impedance balance of the line.
- The standard allows up to **10 mA** per microphone. Lower-voltage P12 and P24 variants also exist.

The equal DC on the signal wires is common-mode, so it does not appear across an ideal floating dynamic coil. A preamp still needs suitable DC blocking, voltage ratings and transient protection: common-mode rejection alone does not make an arbitrary balanced input safe at 48 V.

The microphone draws its current through both feed resistors at once, so they act like a single resistor of half the value (about 3.4 kΩ). Current through a resistance drops voltage across it, so **the more current a microphone draws, the less of the 48 V reaches it**:

| Microphone current | Approximate voltage at the mic |
|---|---|
| 0.8 mA (the U 87 Ai, per Neumann) | about 45 V |
| 5 mA | about 31 V |
| 10 mA (the standard's maximum) | about 14 V |

```formula reference
V_mic = V_s − I R_feed
where
V_mic: the DC voltage left at the microphone, in volts (V)
V_s: the phantom supply voltage, 48 V for P48
I: the current the microphone draws, in amperes (A); P48 allows up to 10 mA (0.010 A)
R_feed: the combined resistance of the two 6.81 kΩ feed resistors in parallel, about 3405 ohms (Ω)
Ω: ohm, the unit of resistance
V: volt
A: ampere (amp), the unit of current
In words: The voltage at the microphone is the supply voltage minus the drop across the paralleled feed resistors, so a microphone that draws more current sees less than 48 volts.
```

So the feed resistors limit what the microphone can draw: a low-current mic sees nearly the full 48 V, while a hungry one sees much less. A supply or interface that can't deliver enough current makes some microphones distort earlier or lose headroom, so check the microphone's stated current against the interface's phantom specification.

> [!warning] Phantom power and your synth
> As module 5 said, keep phantom **off** on any channel your synth or other line-level gear is plugged into. Phantom is for microphones and DI boxes designed for it.

## Key takeaways
- P48 uses matched feed resistors to apply common-mode DC to the signal conductors.
- Feed resistance makes the microphone’s connector voltage depend on current draw.
- Use compatible inputs and correct cables; turn phantom off for equipment that does not require it.

## Further reading
- [Phantom supply and XLR contact diagrams — Schoeps CMC/MK manual, October 2015](https://schoeps.de/fileadmin/user_upload/user_upload/Downloads/Bedienungsanleitungen/SCHOEPS_Manual_CMC_MK_E_2015-10-03_1444311033__1_.pdf)
- [Microphone technology — DPA](https://www.dpamicrophones.com/mic-university/technology/microphone-technology-the-essentials/)
- [U 87 Ai technical data — Neumann](https://www.neumann.com/en-en/products/microphones/u-87-ai/)
- [Phantom power — Schoeps](https://schoeps.de/en/knowledge/knowledge-base/technical-basics/phantom-power-p48p12.html)
- [Three-to-one rule — DPA](https://www.dpamicrophones.com/dict/3-1-rule/)
- [Ribbon microphone phantom precautions — Royer](https://royerlabs.com/faqs/)
