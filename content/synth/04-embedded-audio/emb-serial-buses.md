---
id: emb-serial-buses
title: "Serial buses: UART, I2C and SPI"
level: intermediate
minutes: 14
summary: The three serial buses found in every synth - UART (and why MIDI is a 31,250-baud UART), I2C (addresses, open-drain pull-ups, speed modes) and SPI (clock modes, chip select) - and which one to use for displays, codecs, MIDI and expanders.
---

Apart from audio itself, nearly everything a synth's MCU talks to uses one of three serial buses. MIDI arrives on a **UART**. Codecs and many small sensors are configured over **I2C**. Displays, flash memory and fast external ADCs use **SPI**. Each makes a different trade-off between wires, speed and complexity, and the right choice depends on the job.

## UART: asynchronous serial

A **UART** (universal asynchronous receiver-transmitter) sends bytes one bit at a time on a single wire per direction (TX and RX), with **no clock wire**. Both ends agree the bit rate (**baud rate**) in advance, and the receiver times each bit from the falling edge of a **start bit**.

A frame for the common **8-N-1** setting (8 data bits, no parity, 1 stop bit):

```
idle  start  D0 D1 D2 D3 D4 D5 D6 D7  stop
‾‾‾‾‾|____|  x  x  x  x  x  x  x  x |‾‾‾‾
       0     <- LSB first ->          1
```

- Idle line is high.
- Start bit is 0; stop bit is 1.
- Data bits go **LSB first** (the opposite of I2S's MSB-first audio words).
- 10 bit times per byte in total.

Because there is no clock, both ends' baud rates must match closely, typically within a few percent, or the receiver samples bits in the wrong place by the end of the frame.

### MIDI is a UART

The MIDI 1.0 electrical specification (as updated by the MIDI Association's CA-033 in 2014) says:

> The hardware MIDI interface operates at 31.25 (+/- 1%) Kbaud, asynchronous, with a start bit, 8 data bits (D0 to D7), and a stop bit. This makes a total of 10 bits for a period of 320 microseconds per serial byte.

So a 5-pin DIN MIDI port is an 8-N-1 UART at 31,250 baud. What it costs in time:

```python
baud = 31_250
bits_per_byte = 10    # start + 8 + stop
byte_us = bits_per_byte / baud * 1e6
print(f"one byte: {byte_us:.0f} us")
print(f"note-on: {3 * byte_us:.0f} us")
print(f"bytes/s: {baud // bits_per_byte}")
```

```
one byte: 320 us
note-on: 960 us
bytes/s: 3125
```

A three-byte note-on takes nearly a millisecond on the wire. A four-note chord is 12 bytes, so it takes about 3.8 ms to arrive in full (a little less if the sender uses MIDI's running-status shortcut, which omits repeated status bytes). That is a real, if small, timing smear, and it is part of the end-to-end latency budget in lesson 6.

> [!warning] DIN MIDI is not a bare UART pin
> The specification makes MIDI a 5 mA **current loop** with an **opto-isolator** at every MIDI IN, so that devices do not share ground (avoiding ground loops). You need the specified circuit between the jack and the MCU's UART pins; the CA-033 update gives resistor values for both 5 V and 3.3 V transmitters. Never wire a DIN jack straight to GPIO.

Teensy 4.1 has eight hardware serial ports, and PJRC lists MIDI as a typical use. The Daisy Seed exposes several UARTs (USART1 on pins D13/D14, among others). USB MIDI is a different transport entirely: it uses the USB connection rather than a UART.

## I2C: two wires, many devices

**I2C** (Inter-Integrated Circuit) uses two shared wires for a whole bus of devices:

- **SCL**: clock, driven by the controller (master).
- **SDA**: data, bidirectional.

Every device on the bus has an **address**, usually 7 bits, so there are 128 addresses, of which 16 (0x00–0x07 and 0x78–0x7F) are reserved for special purposes. A transaction looks like:

```
START | addr(7) R/W | ACK | reg | ACK
      | data | ACK | ... | STOP
```

After every byte, the receiver pulls SDA low for one clock to **acknowledge** (ACK). No ACK after the address byte (a **NACK**) means nobody answered: wrong address, wrong wiring, or the device is not powered.

### Open-drain and pull-ups

I2C devices never drive the lines high. They are **open-drain**: they either pull the line low or let go. **Pull-up resistors** to the supply raise the line when everyone has let go. This is what allows several devices to share one wire without fighting.

The consequence: **an I2C bus without pull-ups does not work.** Many breakout boards include them; if you combine several breakouts, their pull-ups appear in parallel and the total may be too strong. TI's application notes describe the trade-off: smaller pull-ups give faster rising edges but more power; bus capacitance (wire length, number of devices) limits speed.

### Speed modes

From TI's *A Basic Guide to I2C* (which also lists a write-only Ultra-Fast mode at 5 Mbit/s, rarely seen in synth parts):

| Mode | Max rate |
|---|---|
| Standard-mode | 100 kbit/s |
| Fast-mode | 400 kbit/s |
| Fast-mode Plus | 1 Mbit/s |
| High-speed mode | 3.4 Mbit/s |

Each byte costs 9 clocks (8 bits plus ACK). A three-byte register write (address, register, value) uses 27 clock pulses: 67.5 µs at 400 kHz, plus START/STOP setup and hold times, any bus-free interval and clock stretching. START and STOP are bus conditions, not two extra clock pulses. That is fine for configuring a codec once at start-up, and far too slow to do repeatedly inside an audio callback.

## SPI: fast, simple, more wires

**SPI** (Serial Peripheral Interface) uses separate lines for each direction plus a clock and one select line per device:

| Signal | Direction | Job |
|---|---|---|
| SCK | Controller → device | Clock |
| MOSI (COPI) | Controller → device | Data out |
| MISO (CIPO) | Device → controller | Data in |
| CS (SS) | Controller → device | Select, active low |

There is no addressing: the controller pulls one device's **chip select** low, clocks data in both directions at once, then raises CS. Each device needs its own CS line.

Outputs are push-pull (driven high and low), so SPI runs much faster than I2C: often several MHz to tens of MHz, depending on the parts and wiring.

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

No ranking of SPI-mode prevalence is given here because reliable survey evidence was unavailable. Read the device's datasheet timing diagram and set the controller to match. A mode mismatch typically gives data that is shifted by a bit or garbage, while CS and clock look fine on a scope.

## Which bus for which job?

A worked comparison: a 128×64 monochrome OLED display holds one bit per pixel, so a full frame is 1,024 bytes.

```python
frame = 128 * 64 // 8
print("frame bytes:", frame)
for hz in (100_000, 400_000):
    ms = frame * 9 / hz * 1000
    khz = hz // 1000
    print(f"I2C {khz} kHz: {ms:.1f} ms")
spi = 8_000_000
ms = frame * 8 / spi * 1000
print(f"SPI 8 MHz: {ms:.2f} ms")
```

```
frame bytes: 1024
I2C 100 kHz: 92.2 ms
I2C 400 kHz: 23.0 ms
SPI 8 MHz: 1.02 ms
```

(These ignore protocol overhead such as addresses and commands, so real I2C times are a little longer.) At 400 kHz I2C, a full redraw takes 23 ms; at 8 MHz SPI, about 1 ms. Both are usable for a status display, but SPI leaves far more headroom for animation, and a blocking 23 ms transfer must never run where it could delay audio.

| Job in a synth | Usual bus | Why |
|---|---|---|
| DIN MIDI in/out | UART | The MIDI spec is a UART |
| Codec configuration | I2C | Few writes, two wires |
| Codec audio data | I2S/SAI | Continuous, clocked |
| OLED/TFT display | SPI (or I2C) | Bulk pixel data |
| SD card, flash | SPI or SDIO | Bulk data |
| GPIO/LED expander | I2C or SPI | Pin count vs speed |
| External ADC | SPI | Fast, many reads |

Practical rules:

- **I2C** when you need few wires and modest data, and can afford a bus that one misbehaving device can lock up.
- **SPI** when speed matters and you have pins for a CS per device.
- **UART** when the protocol demands it (MIDI) or for a debug console.
- Do bus transfers from the main loop or with DMA, never by blocking inside the audio callback.

## Key takeaways
- UART: no clock, agreed baud rate, start bit + data (LSB first) + stop bit. 8-N-1 is 10 bits per byte.
- MIDI over DIN is a 31,250-baud 8-N-1 UART: 320 µs per byte, 960 µs per three-byte note-on. It needs the opto-isolated current-loop circuit from the spec.
- I2C: two open-drain wires, 7-bit addresses, ACK after each byte, mandatory pull-ups, 100 k / 400 k / 1 M / 3.4 Mbit/s modes.
- SPI: clock, two data lines, a chip select per device, four CPOL/CPHA modes; much faster than I2C.
- Choose by job: MIDI on UART, codec control on I2C, displays and bulk data on SPI.

## Further reading
- [MIDI 1.0 Electrical Specification Update (CA-033) — MIDI Association](https://www.midi.org/wp-content/uploads/wpforo/default_attachments/1709416667-ca33-MIDI-10-Electrical-Specification-Update.pdf)
- [5-pin DIN electrical specs — MIDI Association](https://midi.org/5-pin-din-electrical-specs)
- [A Basic Guide to I2C (SBAA565) — Texas Instruments](https://www.ti.com/lit/an/sbaa565/sbaa565.pdf)
- [Understanding the I2C Bus (SLVA704) — Texas Instruments](https://www.ti.com/lit/an/slva704/slva704.pdf)
- [Serial Peripheral Interface — Wikipedia](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface)
- [Universal asynchronous receiver-transmitter — Wikipedia](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter)
- [Teensy 4.1 communication ports — PJRC](https://www.pjrc.com/store/teensy41.html)
