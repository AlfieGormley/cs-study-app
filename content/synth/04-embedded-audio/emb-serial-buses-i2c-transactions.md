---
id: emb-serial-buses-i2c-transactions
sourceLesson: emb-serial-buses
title: "I2C addressing, ACK and pull-ups"
level: intermediate
minutes: 3
summary: "I2C transactions share clock and data lines with pull-ups."
---

## I2C: two wires, many devices

**I2C** (Inter-Integrated Circuit) uses two shared wires for a whole bus of devices:

- **SCL**: clock, driven by the controller (master).
- **SDA**: data, bidirectional.

Every device on the bus has an **I2C address**, usually 7 bits, so there are 128 addresses, of which 16 (0x00–0x07 and 0x78–0x7F) are reserved for special purposes. An I2C transaction looks like:

```
START | addr(7) R/W | ACK | reg | ACK
      | data | ACK | ... | STOP
```

The ninth clock after a byte is an acknowledgement slot. The receiver pulls SDA low for **ACK**, or leaves it high for **NACK**. During a read, the controller deliberately NACKs the final byte to end reception. A NACK on an ordinary target-address attempt means no target acknowledged; check address, power and wiring, but also device busy/not-ready behavior. Certain reserved protocol codes deliberately receive no ACK.

> [!analogy] Real-world analogy: Taking a class register
> A teacher calls out a name and waits for that pupil to answer "here". Silence means nobody with that name responded.
>
> **How it maps:** The controller sends an address, and the matching device acknowledges by pulling SDA low during the ninth clock. A NACK is the silence: the device may be absent, given the wrong address, unpowered, busy or miswired.
>
> **Where it stops:** In I2C the receiver also acknowledges each later byte, not only its address. And silence is just a line left high by its pull-up, so it does not tell you which cause applies.

### Open-drain and pull-ups

In ordinary bidirectional Standard/Fast/Fast-mode Plus I2C, devices do not actively drive the lines high. They are **open-drain**: they either pull the line low or let go. **Pull-up resistors** to the supply raise the line when everyone has let go. This is what allows several devices to share one wire without fighting.

The consequence: **an I2C bus without pull-ups does not work.** Many breakout boards include them; if you combine several breakouts, their pull-ups appear in parallel and the total may be too strong. TI's application notes describe the trade-off: smaller pull-ups give faster rising edges but more power; bus capacitance (wire length, number of devices) limits speed.

### Speed modes

From TI's *A Basic Guide to I2C* (which also lists a write-only Ultra-Fast mode at 5 Mbit/s, rarely seen in synth parts):

| Mode | Max rate |
|---|---|
| Standard-mode | 100 kbit/s |
| Fast-mode | 400 kbit/s |
| Fast-mode Plus | 1 Mbit/s |
| High-speed mode | 3.4 Mbit/s |

Each byte costs nine clocks: eight data bits plus the ACK/NACK slot.

A three-byte register write (address, register, value) therefore uses 27 clock pulses: 67.5 µs at 400 kHz, plus START/STOP setup and hold times, any bus-free interval and clock stretching. START and STOP are bus conditions, not two extra clock pulses. That is suitable for foreground codec configuration. Whether an individual transfer fits a particular budget is a calculation, but blocking bus access and stretching belong outside the callback.

## Key takeaways
- I2C transactions share clock and data lines with pull-ups.
- Count the ninth clock, setup and stretching when budgeting a transfer.

## Further reading
- [MIDI 1.0 Electrical Specification Update (CA-033) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5-pin DIN electrical specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [A Basic Guide to I2C (SBAA565) — Texas Instruments](https://www.ti.com/lit/an/sbaa565/sbaa565.pdf)
- [Understanding the I2C Bus (SLVA704) — Texas Instruments](https://www.ti.com/lit/an/slva704/slva704.pdf)
- [Serial Peripheral Interface — Wikipedia](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)
- [Universal asynchronous receiver-transmitter — Wikipedia](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter)
- [Teensy 4.1 communication ports — PJRC](https://www.pjrc.com/store/teensy41.html)
