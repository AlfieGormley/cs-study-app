---
id: midi-hardware-input-isolation
title: Protect and isolate the MIDI input
level: intermediate
minutes: 2
sourceLesson: midi-hardware
summary: Use the reference isolated input instead of exposing an MCU pin directly to a DIN cable.
---

## Why the input needs an optocoupler

The receiver's end of the loop is the LED of an **optocoupler** (opto-isolator): an LED and an electrically isolated light sensor sealed in one package. The only connection between the two sides is light.

This gives **galvanic isolation**:

- The receiver's circuit ground is never connected to the sender's ground through the MIDI cable.
- A correctly isolated DIN MIDI input avoids adding a DC **ground loop** path: a second ground path between two pieces of mains-powered equipment that already share earth through their power leads. Ground loops let current flow in signal grounds, which you hear as hum in audio.
- It separates the receiver logic from the sender's signal voltage, within the component's and circuit's ratings. It is not an unlimited fault or safety-isolation guarantee.

In a studio full of devices connected by audio cables as well as MIDI, this matters. The spec's own words: "To avoid ground loops, and subsequent data errors, the transmitter circuitry and receiver circuitry are internally separated by an opto-isolator."

Wiring the DIN pins straight to a GPIO would tie the grounds together, break this isolation, and expose your microcontroller to whatever the sender drives. With a 3.3 V board whose pins are not 5 V tolerant (PJRC states this for the Teensy 4.1, for example), a 5 V MIDI output could damage it.

## Key takeaways
- Use the reference isolated input instead of exposing an MCU pin directly to a DIN cable.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
