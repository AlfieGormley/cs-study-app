---
id: midi-hardware-trs-thru
title: Choose TRS wiring and plan THRU chains
level: intermediate
minutes: 3
sourceLesson: midi-hardware
summary: Type A puts DIN pin 5 on the tip and pin 4 on the ring; check the actual product, cable and THRU configuration.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## MIDI THRU and daisy chains

A THRU socket re-transmits whatever arrives at IN. Each optocoupler slightly distorts the bit edges, and the errors accumulate along a chain. The spec says that for chains longer than three instruments, faster optocouplers help. Your Digitakt has a THRU port (it can also be set to send DIN sync instead).

## MIDI over TRS minijacks

Small devices often replace the DIN socket with a 3.5 mm TRS (tip-ring-sleeve) jack and an adapter cable. The MIDI Association standardised this in 2018 as **RP-054, which specifies Type A**. RP-054 actually recommends a 2.5 mm TRS connector; its wiring rules also apply when another size such as 3.5 mm is used. Its adapter cable is at most 2 m and uses shielded twisted pair. An ordinary stereo audio cable is not automatically an acceptable direct TRS MIDI cable. Before standardisation, two incompatible wirings spread:

| TRS | Type A (standard) | Type B |
|---|---|---|
| Tip | Pin 5 (sink) | Pin 4 (source) |
| Ring | Pin 4 (source) | Pin 5 (sink) |
| Sleeve | Pin 2 (shield) | Pin 2 (shield) |

The MIDI Association's article (written before RP-054) lists Akai Pro, IK Multimedia, Korg, Line 6, littleBits and Make Noise as using Type A, and Arturia, 1010music and Novation as using Type B. Wiring varies by product, so check each device's manual rather than assuming by brand.

Pins 4 and 5 are swapped between the types, so a Type B adapter on a Type A device drives the loop backwards. The same article says that connecting with incompatible cables "should not damage devices designed in accordance with the MIDI spec": in the reference receiver, the reverse-protection diode D1 conducts instead of the LED, so the loop current stays limited by the resistors, but no data gets through. A device that departs from the reference circuit (for example, one without D1) has no such guarantee. A few devices also use a two-conductor TS jack, sometimes informally called "Type C".

If you put a TRS MIDI jack on your synth, use Type A, label it clearly, and never plug it into an audio jack.

The official RP-054 document also recommends protection against accidental connection to non-MIDI equipment. Follow its reference circuitry rather than inferring safety from connector shape.

## Key takeaways
- Type A puts DIN pin 5 on the tip and pin 4 on the ring; check the actual product, cable and THRU configuration.

## Further reading
- [RP-054: use of TRS connectors — MIDI Association](https://midi.org/specification-for-use-of-trs-connectors-with-midi-devices)
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
