---
id: midi-hardware-usb-host-roles
title: Provide a USB host for MIDI devices
level: intermediate
minutes: 3
sourceLesson: midi-hardware
summary: A device connector does not provide a host; choose DIN or an explicitly supported host and routing arrangement.
---

Product details in this unit refer to the original Digitakt OS 1.53 manual and Digitakt II OS 1.17 manual, fetched on 16 October 2026. Confirm your model, firmware and current manual before wiring or configuring it.

## Host and device: why two USB gadgets can't talk

USB is not peer-to-peer. Every USB connection has exactly one **host**, which schedules all transfers, and one or more **devices**, which only respond when the host polls them. Devices cannot talk to each other except via the host, and two hosts can't talk over USB directly. (USB On-The-Go and dual-role ports can switch roles, but at any moment one end must be acting as host; the other can be an ordinary USB device.)

> [!analogy] Real-world analogy: a meeting run by a chair
> In a formal meeting, nobody speaks unless the chair gives them the floor, and members don't talk to each other directly: everything goes through the chair. Put two members in a room with no chair and, under those rules, nobody ever speaks.
>
> **How it maps:** the USB host is the chair. It schedules every transfer and polls each device in turn; devices only answer when asked, and anything passing between two devices is relayed by the host. Two devices connected together are two members with no chair: the connection exists, but no transfer is ever scheduled.
>
> **Where it stops:** a USB host also powers and configures (enumerates) its devices, and dual-role ports can swap roles, which a meeting's fixed chair does not capture. The analogy is about who starts transfers, not about speed or wiring.

What this means for your setup:

- Both Digitakt models have a USB-B socket for connecting to a computer host, so the Digitakt acts as a USB **device**.
- Most development boards' main USB port is also a **device** port.
- Plug a USB-device synth into a USB-device Digitakt and **nothing happens**: there is no host. A matching cable shape doesn't mean the connection can work.

Ways to connect two USB devices:

1. **A computer as host.** Both plug into the computer, and software (Ableton, or a MIDI routing utility) forwards messages between them.
2. **A board with a USB host port.** PJRC's Teensy 4.1, for example, has a second USB port that operates in host mode, separate from its device port, supported by the USBHost_t36 library.
3. **A standalone USB MIDI host box** that hosts both devices and forwards between them.
4. **Use DIN MIDI instead.** Point to point, isolated, no host needed. For the illustrated standalone link, DIN avoids the USB host requirement; the final interface remains a project decision.

> [!note] Ordinary USB adds a ground path
> An ordinary non-isolated USB implementation joins host and device grounds. A product with an isolated USB implementation is an exception; do not infer its internal ground paths just from the connector. DIN MIDI doesn't, because of the optocoupler. That is one reason USB connections between mains-powered studio gear can introduce hum, as **Diagnose ground paths and run a test session** discusses. (Elektron lists the original Digitakt's USB port as electrically isolated; check your own model's documentation.)

## Key takeaways
- A device connector does not provide a host; choose DIN or an explicitly supported host and routing arrangement.

## Further reading
- [MIDI 1.0 Electrical Specification Update CA-033 (2014) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5 Pin DIN Electrical Specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [How to make your own 3.5 mm TRS-to-MIDI DIN cables (Type A and B) — MIDI Association](https://midi.org/updated-how-to-make-your-own-3-5mm-mini-stereo-trs-to-midi-5-pin-din-cables)
- [USB Device Class Definition for MIDI Devices 1.0 — USB-IF](https://www.usb.org/sites/default/files/midi10.pdf)
- [USB On-The-Go (host and device roles) — Wikipedia](https://en.wikipedia.org/wiki/USB_On-The-Go)
- [Teensy 4.1 (device and host USB ports, 3.3 V pins) — PJRC](https://www.pjrc.com/store/teensy41.html)
- [Opto-isolator — Wikipedia](https://en.wikipedia.org/wiki/Opto-isolator)
