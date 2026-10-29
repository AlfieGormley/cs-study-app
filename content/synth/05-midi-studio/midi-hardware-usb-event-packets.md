---
id: midi-hardware-usb-event-packets
title: Decode USB MIDI 1.0 event packets
level: intermediate
minutes: 2
sourceLesson: midi-hardware
summary: USB MIDI 1.0 parsed event packets contain a cable/type header and complete MIDI bytes, rather than DIN framing.
---

## USB MIDI

USB MIDI carries the same MIDI messages over USB, defined by the USB-IF's **Device Class Definition for MIDI Devices** (release 1.0, 1999). Key facts from that document:

- MIDI is a subclass of the USB **Audio** class. A device that follows it is **class-compliant**: operating systems that include a USB MIDI class driver can use it without a vendor driver.
- Data travels in fixed **32-bit USB-MIDI Event Packets**: a header byte with a 4-bit **cable number** (up to 16 virtual MIDI cables per endpoint) and a 4-bit **Code Index Number** (the message type), then three MIDI-byte positions, with unused positions filled with zero.
- Each packet normally holds one complete message, status byte included, so running status isn't used. (The spec also has a single-byte mode, CIN 0xF, for passing an unparsed byte stream, but that is a special case.)

The header byte puts the cable number in its top nibble and the Code Index Number in its bottom nibble. For channel messages the Code Index Number simply repeats the status byte's message type, so a Note On on cable 0 has header `09`:

```
Note On, cable 0, ch 1, key 60, vel 100:
09 90 3C 64
^^ cable 0, CIN 9 (note on)
```

A SysEx message can span multiple USB-MIDI Event Packets. Its packet codes distinguish the start/continuation and the final one, two or three bytes; do not assume a whole patch dump fits in one packet.

USB also has far more bandwidth than 31,250 bit/s DIN (full-speed USB alone signals at 12 Mbit/s), so many event packets can travel in each millisecond, which helps with dense data. Actual throughput and timing still depend on the device, the host's scheduling and the driver. (USB MIDI 2.0, a later class specification, carries MIDI 2.0's packets natively and can fall back to USB MIDI 1.0.)

## Key takeaways
- USB MIDI 1.0 wraps each complete MIDI message in a 32-bit event packet: a header byte, then three MIDI byte positions.
- The header's top nibble is the virtual cable number and its bottom nibble the Code Index Number (the message type).
- Packets carry their status byte, so no running status; long SysEx spans several packets.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
