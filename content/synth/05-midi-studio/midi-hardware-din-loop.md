---
id: midi-hardware-din-loop
title: Trace the DIN MIDI current loop
level: intermediate
minutes: 3
sourceLesson: midi-hardware
summary: Check DIN pin numbering from the correct view; current on is logical zero, and MIDI IN keeps its shield free of a DC ground path.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

This lesson is about the wires: how a MIDI byte physically gets from the Digitakt to your synth's microcontroller, and why you can't just connect a DIN socket to a GPIO pin. The project's electronics notes say exactly that: "DIN MIDI is not a direct connection to arbitrary GPIO pins." Here is why, and what to build instead.

> [!warning] Low-voltage work only
> Everything in this lesson runs from your development board's 3.3 V or 5 V supply. Never open or modify mains-powered equipment. Before connecting any circuit to a board, check the pin voltage limits in that board's documentation.

## The 5-pin DIN connection

MIDI uses a 5-pin DIN connector with its pins spread over 180°. The MIDI electrical specification (updated in 2014 as document CA-033) fixes the details:

- Devices have **female sockets** labelled MIDI IN, MIDI OUT and (optionally) MIDI THRU. Cables are male-to-male.
- Only **three pins** are used: **pin 4** (current source), **pin 5** (current sink, the data line) and **pin 2** (shield). Pins 1 and 3 are left unconnected.
- The cable is shielded twisted pair, at most **15 m (50 ft)**, with the shield connected to pin 2 at both ends.
- **Pin 2 is grounded at the transmitter only.** At a MIDI IN, pin 2 must have no DC path to the receiver's ground.

That last rule is the key to the whole design, and it comes from how the signal is carried.

## A current loop, not a voltage

Most logic signals are voltages measured against a shared ground. MIDI instead sends a **current of about 5 mA** around a loop through the cable: out of the transmitter on pin 4, through an LED inside the receiver, and back to the transmitter on pin 5.

```diagram
 SENDER                  RECEIVER
 VTX-RA-pin4 ---------> pin4
                         |
                      RB 220
                         |
                     LED anode
                     LED cathode
                         |
 TX--RC-pin5 <--------- pin5
 GND----pin2 --shield-- pin2 (no GND)
```

The current enters the receiver on pin 4 and leaves on pin 5, so the LED's anode faces pin 4. RB and the LED are in series, so it makes no electrical difference which leg RB sits on; follow the reference figure when you build it.

- **Logical 0 = current on.** When the UART's TX pin goes low, current flows from VTX through the loop into TX.
- **Logical 1 = current off.** TX high: no voltage across the loop, no current. The line idles at 1, so an idle UART means no current.

So the UART needs no inversion: start bits (0) light the receiver's LED, stop bits (1) turn it off. The spec also says one output drives exactly one input.

## Key takeaways
- Check DIN pin numbering from the correct view; current on is logical zero, and MIDI IN keeps its shield free of a DC ground path.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
