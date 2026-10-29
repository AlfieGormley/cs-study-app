---
id: midi-hardware-output-fault-rating
title: Check MIDI output fault ratings
level: intermediate
minutes: 2
sourceLesson: midi-hardware
summary: Normal loop current does not determine the worst resistor heating: check the specified electrical short case and driver limits.
---

## Why RA is rated 0.5 W

In normal operation only a few milliamps flow, and the resistors barely warm. The rating is set by a *fault*. If a damaged cable or a wiring mistake shorts pin 4 to ground, RA sits directly across the 3.3 V supply with nothing else to limit the current. A small resistor across a whole supply carries a large current and turns it into heat, and the heat grows with the *square* of the voltage across it:

```formula reference
P = V^2 / R
where
P: the power the resistor turns into heat, in watts (W)
V: the voltage across the resistor, in volts (V); during the short, the whole supply
R: the resistance, in ohms (Ω)
W: watt, the unit of power
Ω: ohm, the unit of resistance
In words: put the whole supply across a small resistor and it must dissipate the supply voltage squared divided by its resistance as heat.
```

CA-033 works the worst case: the supply 5% high (3.465 V) and RA 5% low (31.35 Ω). That gives about **111 mA and 0.38 W**, well above a 0.25 W part's rating and below the 0.5 W specified. Actual component temperature and derating still matter; parallel resistors with the same total resistance and combined rating are an accepted alternative.

The spec also assumes the buffer driving RC in 3.3 V designs is open-collector or open-drain, and warns not to exceed the driving buffer's short-circuit current rating. The normal loop current tells you nothing about either limit: always check the fault case.

> [!tip] Use the published circuit
> Copy CA-033's figures (or your board vendor's documented MIDI circuit) exactly, and note where each value came from. If you use a MIDI breakout or shield, check its schematic against CA-033 for the voltage your board runs at.

## Key takeaways
- Resistor and driver ratings are set by fault cases, not by the few milliamps of normal operation.
- A short from pin 4 to ground puts the whole supply across RA: about 111 mA and 0.38 W worst case, so RA must be rated 0.5 W.
- Also respect the driving buffer's short-circuit rating, and copy the published circuit for your supply voltage.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
