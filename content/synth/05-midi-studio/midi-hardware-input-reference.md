---
id: midi-hardware-input-reference
title: Choose a compatible receiver circuit
level: intermediate
minutes: 4
sourceLesson: midi-hardware
summary: Check optocoupler supply, pull-up, speed and pin limits together; an optional shield capacitor preserves DC isolation but is not ideal at every frequency.
---

## The reference MIDI IN circuit

Figure 2 of CA-033 gives the input circuit. The essential parts:

| Part | Role |
|---|---|
| RB = 220 Ω | Series resistor in the loop |
| Optocoupler | Isolation; e.g. PC900V, 6N138 |
| D1 (1N914) | Reverse protection for the LED |
| RD (pull-up) | Opto output to VRX |
| Pin 2 | No DC path to ground |

How it works:

1. Loop current flows through RB and the optocoupler's LED.
2. The light detector and output circuitry respond to the LED, pulling the output low against the pull-up RD.
3. That output goes to your UART's RX pin. Current on gives a low (0), current off gives a high (1): the same low/high logic relationship the sender's UART produced.
4. D1, wired across the LED in the reverse direction, stops a reversed or faulty connection from putting a damaging reverse voltage on the LED.

Requirements from the spec: the receiver must need **less than 5 mA** to turn on, and rise and fall times should be under **2 µs**. To see why 2 µs is comfortable, compare it with the length of one bit:

```formula
t_bit = 1 / R
t_bit = 1 bit / (31250 bit/s)
t_bit = 0.000032 s = 32 µs
where
t_bit: the time one bit lasts on the wire, in seconds (s)
R: the DIN MIDI bit rate, 31,250 bits per second (bit/s)
bit: one binary digit
s: seconds
µs: microseconds, millionths of a second
In words: each MIDI bit lasts 32 µs, so a 2 µs edge uses up only about a sixteenth of it.
```

The spec names the Sharp PC900V and Hewlett-Packard 6N138 as acceptable and notes that other high-speed optocouplers may be. Its only recommended RD value is **280 Ω for the PC900V with a 5 V pull-up supply (VRX)**. The reference parts use output circuitry requiring an external pull-up (the 6N138's output pin is the bare collector of its output transistor), which is why the pull-up RD is needed. Acceptance in the older CA-033 example does not prove a part works at a 3.3 V output supply. For a 3.3 V receiver, pick an optocoupler whose actual manufacturer datasheet supports that supply and choose RD from that datasheet. Pull the output up to **your MCU's supply (3.3 V)**, never to 5 V on a pin that isn't 5 V tolerant.

Optional additions in CA-033: ferrite beads on the signal pins, and a **0.1 µF capacitor** from MIDI IN pin 2 (or the jack shield) to ground. A capacitor's opposition to AC (its reactance) falls as frequency rises:

```formula
X_C = 1 / (2πfC)
X_C = 1 / (2 × π × 60 Hz × 0.0000001 F)
X_C ≈ 26500 Ω = 26.5 kΩ
where
X_C: the capacitor's reactance, its opposition to alternating current, in ohms (Ω)
π: pi, about 3.14159
f: the frequency of the signal or interference, in hertz (Hz); 60 Hz here, a mains frequency
C: the capacitance, in farads (F); 0.1 µF = 0.0000001 F
Hz: hertz, cycles per second
F: farad, the unit of capacitance
Ω: ohm, the unit of resistance and reactance
kΩ: kilohm, 1,000 ohms
≈: approximately equal to (rounded)
In words: at mains frequencies the 0.1 µF capacitor looks like tens of thousands of ohms, nearly an open circuit.
```

Repeat it at a radio frequency of 10 MHz (10,000,000 Hz) and the reactance is about 0.16 Ω, close to a short circuit. This is the ideal-capacitor approximation used in CA-033, not a complete RF model of a real part or cable. At 20 kHz the same ideal capacitor is about 79.6 Ω, so do not call it an open circuit throughout the audio band. The optional connection preserves DC isolation while giving RF interference a lower-impedance path, as the specification intends.

## Key takeaways
- Check optocoupler supply, pull-up, speed and pin limits together; an optional shield capacitor preserves DC isolation but is not ideal at every frequency.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
