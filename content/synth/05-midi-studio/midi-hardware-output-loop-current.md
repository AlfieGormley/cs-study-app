---
id: midi-hardware-output-loop-current
title: Check the 3.3 V output current
level: intermediate
minutes: 3
sourceLesson: midi-hardware
summary: Use the resistor values for the specified transmitter voltage and account for receiver and driver drops.
---

## The reference MIDI OUT circuit, 3.3 V version

The original 1983 output used +5 V and two 220 Ω resistors. Most current microcontrollers run at 3.3 V, so the 2014 update adds a 3.3 V variant. In Figure 1, RA connects pin 4 to the supply VTX, and RC connects pin 5 to the UART TX (optionally through a buffer):

| VTX | RA (pin 4) | RC (pin 5) |
|---|---|---|
| +5 V ± 10% | 220 Ω 5% 0.25 W | 220 Ω 5% 0.25 W |
| +3.3 V ± 5% | 33 Ω 5% **0.5 W** | 10 Ω 5% 0.25 W |

Pin 2 is grounded at the transmitter.

## Why 3.3 V needs different resistors

The loop is one series circuit: supply, RA, the cable, the receiver's 220 Ω resistor RB and its optocoupler LED, back through the cable, RC and into the UART pin. The LED takes a roughly fixed forward-voltage "bite" (about 1.4 V to 1.9 V depending on the part and current), and only what is left of the supply pushes current through the resistors. Ohm's law then gives the current:

```formula reference
I = (V_TX − V_F) / (R_A + R_C + R_B)
where
I: the loop current, in amperes (A); about 5 mA is the design target
V_TX: the transmitter's supply voltage (VTX), in volts (V)
V_F: the forward voltage dropped across the optocoupler's LED while it conducts, in volts; typically about 1.4 V to 1.9 V
R_A: the transmitter's resistor from the supply to pin 4, in ohms (Ω)
R_C: the transmitter's resistor from the UART TX pin to pin 5, in ohms
R_B: the receiver's series resistor, 220 Ω
V: volt, the unit of voltage
Ω: ohm, the unit of resistance
A: ampere, the unit of current
In words: the supply voltage left over after the LED's drop, divided by all the series resistance in the loop, sets the current.
```

From 5 V there is plenty of voltage to spare, so two 220 Ω resistors give about 5 mA. From 3.3 V the spare voltage is small, so the transmitter resistors must shrink to keep enough current flowing. The first three rows are CA-033's own figures; the last applies the same simple model (which ignores the cable and the driver's small low-state voltage) to a common mistake:

| Case | Loop current |
|---|---|
| 5 V, 220 Ω + 220 Ω, 1.7 V LED | about 5.0 mA |
| 3.3 V, 33 Ω + 10 Ω, 1.4 V LED | about 7.2 mA |
| 3.3 V worst case (−5% supply, +5% resistors, 1.9 V LED) | about 4.47 mA |
| Mistake: 3.3 V with the 5 V resistors, 1.4 V LED | about 2.9 mA |

The last row shows why you mustn't run the 5 V resistor values from 3.3 V: under 3 mA may not reliably switch every receiver. Notice also how sensitive the 3.3 V design is to the LED's forward voltage. That drop depends on the receiver's optocoupler, which the transmitter designer cannot choose, so the specification checks the worst case rather than a single typical figure.

## Key takeaways
- The MIDI loop is a single series circuit; the supply minus the LED's forward drop, divided by the total resistance, sets the current.
- From 3.3 V use CA-033's 33 Ω (0.5 W) and 10 Ω resistors; the 5 V values leave too little current.
- Low-voltage designs have little spare voltage, so check the worst case (low supply, high resistance, high LED drop), not just the typical one.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
