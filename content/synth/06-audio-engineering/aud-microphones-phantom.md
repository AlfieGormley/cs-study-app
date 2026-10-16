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

The mic draws its current through both feed resistors at once. Two equal resistors side by side (in parallel) act like one of half the value, and the voltage lost across them follows Ohm's law:

```formula
R_feed = 6810 Ω / 2 = 3405 Ω
V_mic = V_s − I R_feed
V_mic = 48 V − 0.010 A × 3405 Ω
V_mic = 48 V − 34.05 V ≈ 14.0 V
where
R_feed: the combined resistance of the two 6.81 kΩ feed resistors in parallel, in ohms (Ω)
V_mic: the DC voltage left at the microphone, in volts (V)
V_s: the phantom supply voltage, 48 V for P48
I: the current the microphone draws, in amperes (A); here 10 mA = 0.010 A, the maximum the standard allows
Ω: ohm, the unit of resistance
V: volt
A: ampere (amp), the unit of current
≈: approximately equal to (the result is rounded)
In words: the more current the mic draws, the more voltage is dropped in the feed resistors, so a hungry mic sees much less than 48 V.
```

The same calculation for three currents, in Python:

```python
# Each matched leg carries half the current.
R_feed = 6810 / 2     # two in parallel
for i_ma in (0.8, 5, 10):
    v = 48 - i_ma / 1000 * R_feed
    print(f"{i_ma:>4} mA: "
          f"{v:5.1f} V at mic")
```

```
 0.8 mA:  45.3 V at mic
   5 mA:  31.0 V at mic
  10 mA:  14.0 V at mic
```

The feed resistors limit what the mic can draw: a low-current mic like the U 87 Ai (0.8 mA per Neumann) sees nearly the full 48 V; a hungry one sees much less. A supply that can't deliver enough current makes some mics distort earlier.

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
