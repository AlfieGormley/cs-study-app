---
id: midi-hardware-output-fault-rating
title: Check MIDI output fault ratings
level: intermediate
minutes: 2
sourceLesson: midi-hardware
summary: Normal loop current does not determine the worst resistor heating: check the specified electrical short case and driver limits.
---

## Why RA is rated 0.5 W
Why is RA rated 0.5 W? If a cable fault shorts pin 4 to ground, RA sits directly across the supply. The spec's worst case is the supply 5% high (3.465 V) and the resistor 5% low (31.35 Ω). Ohm's law gives the current, and the power the resistor must turn into heat follows from the voltage across it:

```formula
I = V / R
I = 3.465 V / (31.35 Ω) ≈ 0.111 A
P = V^2 / R
P = (3.465 V)^2 / (31.35 Ω)
P ≈ 12.006 V^2 / (31.35 Ω)
P ≈ 0.383 W
where
I: the fault current through RA, in amperes (A)
V: the voltage across RA, which during the short is the whole supply, in volts (V); 3.465 V worst case
R: RA's resistance, in ohms (Ω); 33 Ω nominal, 31.35 Ω at −5% tolerance
P: the power dissipated in RA as heat, in watts (W)
A: ampere, the unit of current
Ω: ohm, the unit of resistance
W: watt, the unit of power
≈: approximately equal to (rounded)
In words: shorted straight across the supply, the small resistor carries about 111 mA and heats by about 0.38 W, which would overload a 0.25 W part.
```

So the result is about **111 mA and 0.38 W**, below the nominal 0.5 W rating; actual component temperature and derating requirements still matter. The spec also assumes the buffer driving RC in 3.3 V designs is open-collector or open-drain, and warns not to exceed the driving buffer's short-circuit current rating.

> [!tip] Use the published circuit
> Copy CA-033's figures (or your board vendor's documented MIDI circuit) exactly, and note where each value came from. If you use a MIDI breakout or shield, check its schematic against CA-033 for the voltage your board runs at.

## Key takeaways
- Normal loop current does not determine the worst resistor heating: check the specified electrical short case and driver limits.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
