---
id: emb-serial-buses-spi-modes
sourceLesson: emb-serial-buses
title: "SPI wiring and clock modes"
level: intermediate
minutes: 2
summary: "Match clock polarity and clock phase to the peripheral timing diagram."
---

## SPI: fast, simple, more wires

**SPI** (Serial Peripheral Interface) uses separate lines for each direction plus a clock and one select line per device:

| Signal | Direction | Job |
|---|---|---|
| SCK | Controller → device | Clock |
| MOSI (COPI) | Controller → device | Data out |
| MISO (CIPO) | Device → controller | Data in |
| CS (SS) | Controller → device | Select, active low |

There is no addressing: the controller pulls one device's **chip select** low, clocks data in both directions at once, then raises CS. This ordinary independently selected arrangement uses one CS per device; daisy chains and some single-device interfaces are exceptions defined by their parts.

SPI uses push-pull outputs (driven high and low), which often supports higher rates than ordinary I2C: often several MHz to tens of MHz, depending on the parts and wiring.

### Clock modes

Devices disagree on which clock edge to use, so SPI has four **modes**, set by two bits:

- **CPOL**: clock idle level (0 = idle low, 1 = idle high).
- **CPHA**: which edge samples data (0 = first edge, 1 = second edge).

| Mode | CPOL | CPHA |
|---|---|---|
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 2 | 1 | 0 |
| 3 | 1 | 1 |

Read the device's datasheet timing diagram and set the controller to match. A mode mismatch typically gives data that is shifted by a bit or garbage, while CS and clock look fine on a scope.

## Key takeaways
- Match clock polarity and clock phase to the peripheral timing diagram.
- Ordinary independently selected devices need their own select lines.

## Further reading
- [MIDI 1.0 Electrical Specification Update (CA-033) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5-pin DIN electrical specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [A Basic Guide to I2C (SBAA565) — Texas Instruments](https://www.ti.com/lit/an/sbaa565/sbaa565.pdf)
- [Understanding the I2C Bus (SLVA704) — Texas Instruments](https://www.ti.com/lit/an/slva704/slva704.pdf)
- [Serial Peripheral Interface — Wikipedia](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)
- [Universal asynchronous receiver-transmitter — Wikipedia](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter)
- [Teensy 4.1 communication ports — PJRC](https://www.pjrc.com/store/teensy41.html)
- [SPI signals, polarity and phase — MicroPython](https://docs.micropython.org/en/latest/library/machine.SPI.html)
