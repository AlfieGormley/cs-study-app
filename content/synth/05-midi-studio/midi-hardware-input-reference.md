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

Requirements from the spec: the receiver must need **less than 5 mA** to turn on, and rise and fall times should be under **2 µs**. Each MIDI bit lasts 32 µs (one bit at 31,250 bit/s), so a 2 µs edge uses only about a sixteenth of the bit. Slower optocouplers smear the edges, and the distortion accumulates along THRU chains.

The spec names the Sharp PC900V and Hewlett-Packard 6N138 as acceptable and notes that other high-speed optocouplers may be. Its only recommended RD value is **280 Ω for the PC900V with a 5 V pull-up supply (VRX)**. The reference parts use output circuitry requiring an external pull-up (the 6N138's output pin is the bare collector of its output transistor), which is why the pull-up RD is needed. Acceptance in the older CA-033 example does not prove a part works at a 3.3 V output supply. For a 3.3 V receiver, pick an optocoupler whose actual manufacturer datasheet supports that supply and choose RD from that datasheet. Pull the output up to **your MCU's supply (3.3 V)**, never to 5 V on a pin that isn't 5 V tolerant.

Optional additions in CA-033: ferrite beads on the signal pins, and a **0.1 µF capacitor** from MIDI IN pin 2 (or the jack shield) to ground. Why doesn't that capacitor break the "no DC path to ground" rule? Because a capacitor blocks DC entirely, and its opposition to AC (its **reactance**) falls as frequency rises:

```formula reference
X_C = 1 / (2πfC)
where
X_C: the capacitor's reactance, its opposition to alternating current, in ohms (Ω)
π: pi, about 3.14159
f: the frequency of the signal or interference, in hertz (Hz)
C: the capacitance, in farads (F); 0.1 µF is 0.0000001 F
Ω: ohm, the unit of resistance and reactance
In words: the higher the frequency (or the bigger the capacitor), the lower the reactance, so a small capacitor nearly blocks low frequencies and nearly shorts radio frequencies.
```

For the ideal 0.1 µF capacitor that means:

| Frequency | Reactance |
|---|---|
| 60 Hz (mains) | about 26.5 kΩ |
| 20 kHz (top of audio) | about 80 Ω |
| 10 MHz (radio) | about 0.16 Ω |

So the shield stays effectively disconnected at DC and mains frequencies while radio-frequency interference gets a low-impedance path to ground, as the specification intends. Do not call it an open circuit throughout the audio band: at 20 kHz it is only about 80 Ω. These are ideal-capacitor figures, the approximation CA-033 itself uses, not a complete RF model of a real part or cable.

## Key takeaways
- The reference input is a 220 Ω resistor, an optocoupler LED with a reverse-protection diode, and a pull-up on the output side.
- Pick an optocoupler and pull-up that are specified for your supply (3.3 V or 5 V), switch in under 2 µs and never pull a pin above its limit.
- An optional 0.1 µF shield capacitor keeps DC isolation while giving radio-frequency interference a path to ground; it is not an open circuit at every frequency.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
